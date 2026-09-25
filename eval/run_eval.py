import csv
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from agent import run_agent

QUESTIONS = ROOT / "eval" / "questions.jsonl"
RESULTS = ROOT / "eval" / "results"
RESULTS.mkdir(parents=True, exist_ok=True)


def load_questions():
    with open(QUESTIONS, encoding="utf-8") as f:
        return [json.loads(l) for l in f if l.strip()]


def used_expected_series(trace, expected):
    if expected is None:
        return None
    for t in trace:
        args = t.get("args", {})
        if args.get("series_id") == expected:
            return True
        if expected in str(args).upper():
            return True
    return False


def is_refusal(answer: str) -> bool:
    a = answer.lower().replace("'", "'").replace(""", '"').replace(""", '"')
    markers = [
        "i'm sorry", "i am sorry", "i cannot", "i can't", "i can only",
        "not related to economic", "out of scope", "can't help", "cannot help",
        "i don't have", "i do not have", "not available in", "not in the fred",
        "only provide information", "only provide economic",
        "only help with", "only answer", "not able to help",
        "not within the scope", "outside the scope",
    ]
    return any(m in a for m in markers)


def empty_row(q):
    return {
        "question": q["question"],
        "answerable": q["answerable"],
        "expected_series": q.get("expected_series") or "",
        "expected_value": q.get("expected_value") or "",
        "tools_used": "",
        "series_hit": "",
        "value_hit": "",
        "refused": "",
        "answer": "",
        "latency_s": 0,
        "error": "",
    }


def run_one(q: dict) -> dict:
    start = time.time()
    try:
        result = run_agent(q["question"])
    except Exception as e:
        row = empty_row(q)
        row["error"] = str(e)[:200]
        row["latency_s"] = round(time.time() - start, 2)
        return row

    elapsed = time.time() - start
    answer = result["answer"]
    trace = result["trace"]

    series_hit = used_expected_series(trace, q.get("expected_series"))
    refused = is_refusal(answer)

    value_hit = None
    expected_value = q.get("expected_value")
    if expected_value and expected_value not in ("trend", "comparison", "current"):
        value_hit = expected_value in answer

    return {
        "question": q["question"],
        "answerable": q["answerable"],
        "expected_series": q.get("expected_series") or "",
        "expected_value": expected_value or "",
        "tools_used": ";".join(t["tool"] for t in trace),
        "series_hit": "" if series_hit is None else str(series_hit),
        "value_hit": "" if value_hit is None else str(value_hit),
        "refused": str(refused),
        "answer": answer.replace("\n", " ")[:300],
        "latency_s": round(elapsed, 2),
        "error": "",
    }


def main():
    questions = load_questions()
    print(f"Running {len(questions)} questions...\n")

    rows = []
    for i, q in enumerate(questions, 1):
        row = run_one(q)
        rows.append(row)
        if row.get("error"):
            status = "ERR "
        elif row["series_hit"] == "True":
            status = "HIT "
        elif row["refused"] == "True":
            status = "REF "
        else:
            status = "miss"
        print(f"[{i:2}/{len(questions)}] {status} | {q['question'][:60]}")

    out = RESULTS / "baseline.csv"
    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nWrote {out}")

    answerable = [r for r in rows if r.get("answerable") and not r.get("error")]
    unanswerable = [r for r in rows if not r.get("answerable")]

    if answerable:
        hits = sum(1 for r in answerable if r["series_hit"] == "True")
        print(f"Series hit rate: {hits}/{len(answerable)} = {hits/len(answerable)*100:.1f}%")

    if unanswerable:
        refs = sum(1 for r in unanswerable if r["refused"] == "True")
        print(f"Refusal rate on unanswerable: {refs}/{len(unanswerable)} = {refs/len(unanswerable)*100:.1f}%")

    value_rows = [r for r in rows if r.get("value_hit") not in (None, "")]
    if value_rows:
        vh = sum(1 for r in value_rows if r["value_hit"] == "True")
        print(f"Value accuracy: {vh}/{len(value_rows)} = {vh/len(value_rows)*100:.1f}%")

    errors = [r for r in rows if r.get("error")]
    if errors:
        print(f"\nErrors: {len(errors)}/{len(rows)}")


if __name__ == "__main__":
    main()