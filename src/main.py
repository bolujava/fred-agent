import sys
from pathlib import Path
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse

sys.path.insert(0, str(Path(__file__).parent / "src"))
from .agent import run_agent

app = FastAPI()

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>FRED Economic Data Agent</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        :root {
            --bg-color: #0b0f19;
            --card-bg: #111827;
            --card-border: #1f293d;
            --text-main: #f3f4f6;
            --text-muted: #9ca3af;
            --accent-gradient: linear-gradient(135deg, #6366f1 0%, #3b82f6 100%);
            --accent-glow: rgba(99, 102, 241, 0.25);
            --input-bg: #1f2937;
            --input-border: #374151;
            --focus-border: #6366f1;
            --error-color: #f87171;
        }

        * {
            box-sizing: border-box;
            margin: 0;
            padding: 0;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            background-image: 
                radial-gradient(at 0% 0%, rgba(99, 102, 241, 0.12) 0px, transparent 50%),
                radial-gradient(at 100% 100%, rgba(59, 130, 246, 0.08) 0px, transparent 50%);
            background-repeat: no-repeat;
            background-attachment: fixed;
            color: var(--text-main);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }

        .container {
            width: 100%;
            max-width: 680px;
            background: var(--card-bg);
            border: 1px solid var(--card-border);
            border-radius: 12px;
            padding: 32px;
            box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5);
        }

        .header {
            margin-bottom: 24px;
        }

        h1 {
            font-size: 1.5em;
            font-weight: 600;
            letter-spacing: -0.025em;
            margin-bottom: 6px;
            background: linear-gradient(to right, #ffffff, #93c5fd);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }

        p {
            color: var(--text-muted);
            font-size: 0.95em;
        }

        .input-group {
            display: flex;
            flex-direction: column;
            gap: 12px;
            margin-bottom: 20px;
        }

        input[type=text] {
            width: 100%;
            padding: 14px 16px;
            font-size: 0.95em;
            background-color: var(--input-bg);
            border: 1px solid var(--input-border);
            border-radius: 8px;
            color: var(--text-main);
            outline: none;
            transition: all 0.2s ease;
        }

        input[type=text]:focus {
            border-color: var(--focus-border);
            box-shadow: 0 0 0 3px var(--accent-glow);
        }

        input[type=text]::placeholder {
            color: #6b7280;
        }

        button {
            padding: 12px 24px;
            font-size: 0.95em;
            font-weight: 500;
            background: var(--accent-gradient);
            color: #ffffff;
            border: none;
            border-radius: 8px;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: 0 4px 12px var(--accent-glow);
        }

        button:hover:not(:disabled) {
            opacity: 0.95;
            transform: translateY(-1px);
        }

        button:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
            box-shadow: none;
        }

        #result {
            margin-top: 20px;
            padding: 16px;
            background: #0f172a;
            border: 1px solid var(--card-border);
            border-radius: 8px;
            white-space: pre-wrap;
            font-size: 0.95em;
            line-height: 1.6;
            color: #e2e8f0;
        }

        #meta {
            font-size: 0.8em;
            color: var(--text-muted);
            margin-top: 10px;
            font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace;
        }

        .error {
            color: var(--error-color);
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>FRED Economic Data Agent</h1>
            <p>Ask a question about US economic data.</p>
        </div>

        <div class="input-group">
            <input type="text" id="q" placeholder="e.g. What was the US unemployment rate in January 2024?" />
            <button id="ask">Ask</button>
        </div>

        <div id="result" style="display:none;"></div>
        <div id="meta"></div>
    </div>

    <script>
        const q = document.getElementById('q');
        const btn = document.getElementById('ask');
        const result = document.getElementById('result');
        const meta = document.getElementById('meta');

        async function ask() {
            const question = q.value.trim();
            if (!question) return;

            btn.disabled = true;
            result.style.display = 'block';
            result.textContent = 'Thinking...';
            meta.textContent = '';

            try {
                const resp = await fetch('/api/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/x-www-form-urlencoded'},
                    body: 'question=' + encodeURIComponent(question)
                });
                const data = await resp.json();
                result.textContent = data.answer;
                const tools = data.trace && data.trace.length
                    ? data.trace.map(t => t.tool).join(' → ')
                    : 'none';
                meta.textContent = `Tools: ${tools} | Latency: ${data.latency}s`;
            } catch (e) {
                result.innerHTML = '<span class="error">Error: ' + e.message + '</span>';
            } finally {
                btn.disabled = false;
            }
        }

        btn.onclick = ask;
        q.addEventListener('keypress', e => { if (e.key === 'Enter') ask(); });
    </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML


@app.post("/api/ask")
async def ask(question: str = Form(...)):
    import time
    start = time.time()
    try:
        result = run_agent(question)
        return {
            "answer": result["answer"],
            "trace": [{"tool": t["tool"], "args": t["args"]} for t in result["trace"]],
            "latency": round(time.time() - start, 2),
        }
    except Exception as e:
        return {
            "answer": f"Error: {str(e)[:200]}",
            "trace": [],
            "latency": round(time.time() - start, 2),
        }