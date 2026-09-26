import json
from openai import OpenAI
from dotenv import load_dotenv
import os

from .tools import TOOL_MAP

load_dotenv()

client = OpenAI(
    base_url="https://api.groq.com/openai/v1",
    api_key=os.getenv("GROQ_API_KEY"),
)

SYSTEM_PROMPT = """You are a FRED economic data agent.
You have three tools:
1. search_series(query) - find series IDs by keyword. ALWAYS use this first if you don't know the series ID.
2. get_observations(series_id, start, end) - fetch data for a series.
3. transform_series(series_id, transform) - apply percent_change, yoy, or raw.

To answer a question:
- First search for the right series if you don't know its ID.
- Then fetch the observations.
- Then answer with specific numbers and dates.

QUARTER DEFINITIONS:
- Q1 = January, February, March (dates: YYYY-01-01 to YYYY-03-31)
- Q2 = April, May, June (dates: YYYY-04-01 to YYYY-06-30)
- Q3 = July, August, September (dates: YYYY-07-01 to YYYY-09-30)
- Q4 = October, November, December (dates: YYYY-10-01 to YYYY-12-31)

When asked about a specific quarter, use ONLY the dates of that quarter.
- For GDP quarterly data, the last month of the quarter is the quarter-end value.
- Do NOT fetch data beyond the quarter.

EXAMPLES:
- "Q1 2024 GDP" → get_observations("GDP", start="2024-01-01", end="2024-03-31") → report the March 2024 value.
- "Q4 2023 GDP" → get_observations("GDP", start="2023-10-01", end="2023-12-31") → report the December 2023 value.

Be concise. Always include the actual numbers and their dates."""

# Tool schemas for the LLM
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "search_series",
            "description": "Search FRED for series IDs matching a keyword. Use this when you don't know the series ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search keyword like 'unemployment rate' or 'inflation'"}
                },
                "required": ["query"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_observations",
            "description": "Fetch data for a specific FRED series ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "series_id": {"type": "string", "description": "FRED series ID like UNRATE or GDP"},
                    "start": {"type": "string", "description": "Start date YYYY-MM-DD"},
                    "end": {"type": "string", "description": "End date YYYY-MM-DD"}
                },
                "required": ["series_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "transform_series",
            "description": "Apply a transformation to a series: percent_change, yoy, or raw.",
            "parameters": {
                "type": "object",
                "properties": {
                    "series_id": {"type": "string", "description": "FRED series ID"},
                    "transform": {"type": "string", "description": "percent_change, yoy, or raw"}
                },
                "required": ["series_id"]
            }
        }
    }
]


def run_agent(question: str, max_steps: int = 5) -> dict:
    """Run the ReAct loop. Returns final answer and tool call trace."""
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": question},
    ]
    trace = []

    for step in range(max_steps):
        response = None
        for attempt in range(2):
            try:
                response = client.chat.completions.create(
                    model="openai/gpt-oss-120b",
                    messages=messages,
                    tools=TOOLS,
                    tool_choice="auto",
                    temperature=0,
                )
                break
            except Exception as e:
                if attempt == 1:
                    raise
                print(f"  [retry] {type(e).__name__}: {str(e)[:80]}")
        msg = response.choices[0].message

        # If no tool calls, we're done
        if not msg.tool_calls:
            return {"answer": msg.content, "trace": trace}

        # Add the assistant's tool call to history
        messages.append(msg)

        # Execute each tool call
        for call in msg.tool_calls:
            name = call.function.name
            args = json.loads(call.function.arguments)
            fn = TOOL_MAP.get(name)
            result = fn(**args) if fn else f"Unknown tool: {name}"

            trace.append({"tool": name, "args": args, "result_preview": str(result)[:200]})

            messages.append({
                "role": "tool",
                "tool_call_id": call.id,
                "content": str(result),
            })

    return {"answer": "Max steps reached", "trace": trace}