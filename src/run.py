import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from agent import run_agent
from memory import Conversation


if __name__ == "__main__":
    # If arguments passed, run single question
    if len(sys.argv) > 1:
        q = " ".join(sys.argv[1:])
        result = run_agent(q)
        print("\n=== ANSWER ===")
        print(result["answer"])
        print("\n=== TRACE ===")
        for t in result["trace"]:
            print(f"  -> {t['tool']}({t['args']})")
    else:
        # Otherwise, interactive multi-turn chat
        print("FRED Agent — interactive mode. Type 'exit' to quit.\n")
        conversation = Conversation()
        while True:
            q = input("You: ").strip()
            if not q or q.lower() in ("exit", "quit"):
                break
            result = run_agent(q, conversation=conversation)
            print(f"\nAgent: {result['answer']}\n")
            if result["trace"]:
                print(f"  [tools: {' → '.join(t['tool'] for t in result['trace'])}]\n")