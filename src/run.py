import sys
from .agent import run_agent

if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "What was the US unemployment rate in January 2024?"
    result = run_agent(q)
    print("\n=== ANSWER ===")
    print(result["answer"])
    print("\n=== TRACE ===")
    for t in result["trace"]:
        print(f"  -> {t['tool']}({t['args']})")