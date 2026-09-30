# FRED Economic Data Agent

An AI agent that answers questions about US economic data by querying the Federal Reserve Economic Data (FRED) API. Built from scratch with plain Python — no agent frameworks. Includes a hand-written evaluation harness with 15 questions and known ground-truth answers.

## What this is

Most "I built an AI agent" projects show you a demo. This one shows you the **numbers**. It has:

- A working ReAct agent that calls FRED tools in a loop
- Three tools: series search, observation fetch, and transformation
- A hand-written eval set of 15 questions across 5 FRED series
- A scoring script that measures series selection, value accuracy, and refusal behavior
- A documented list of failure modes and the fixes applied

The point is not that the agent works. The point is that I can prove how well it works, where it fails, and why.

## Why an agent (not a chatbot)

A chatbot responds to one query with one answer. An **agent** pursues a goal across multiple steps — deciding which tools to call, when, and with what arguments.

Example: **"Compare US unemployment in January 2024 vs January 2020."**

A chatbot would fail or guess. The agent:

1. Decides it needs the unemployment series (`UNRATE`)
2. Calls `get_observations("UNRATE", "2024-01-01", "2024-01-31")`
3. Calls `get_observations("UNRATE", "2020-01-01", "2020-01-31")`
4. Compares the two values
5. Answers with specific numbers and dates

That's the difference. The LLM decides, the tools fetch, the LLM writes.

## Architecture

# FRED Economic Data Agent

An AI agent that answers questions about US economic data by calling the Federal Reserve Economic Data (FRED) API. Supports multi-turn conversations with memory. Built from scratch in plain Python — no agent frameworks. Includes a hand-written evaluation harness measuring series selection, value accuracy, refusal behavior, and multi-turn conversation handling.

**Live demo:** https://fred-agent.vercel.app

## What this is

Most "I built an AI agent" projects show you a demo. This one shows you the **numbers**. It has:

- A working ReAct agent with tool calling and multi-step reasoning
- Three tools: series search, observation fetch, and transformation
- **Multi-turn conversation memory** — the agent resolves follow-ups like "What about December 2023?"
- A hand-written eval set: 15 single-turn questions and 10 multi-turn conversations
- A scoring script that produces four metrics, not one
- A documented list of failure modes and the fixes applied

The point is not that the agent works. The point is that I can prove how well it works, where it fails, and why.

## Why an agent (not a chatbot)

A chatbot responds to one query with one answer. An **agent** pursues a goal across multiple steps — deciding which tools to call, when, and with what arguments.

Example: **"Compare US unemployment in January 2024 vs January 2020."**

A chatbot would fail or guess. The agent:

1. Decides it needs the unemployment series (`UNRATE`)
2. Calls `get_observations("UNRATE", "2024-01-01", "2024-01-31")`
3. Calls `get_observations("UNRATE", "2020-01-01", "2020-01-31")`
4. Compares the two values
5. Answers with specific numbers and dates

That's the difference. The LLM decides, the tools fetch, the LLM writes.

## Multi-turn memory

The agent keeps a conversation history. Follow-up questions resolve against the previous turn.

=== Single-turn eval: 15 questions ===

[ 1/15] HIT  | What was the US unemployment rate in January 2024?
...
Series hit rate: 8/10 = 80.0%
Refusal rate on unanswerable: 2/5 = 40.0%
Value accuracy: 4/7 = 57.1%

=== Multi-turn eval: 10 conversations ===

[ 1/10] PASS | What about December 2023?
...
Conversation pass rate: 6/10 = 60.0%