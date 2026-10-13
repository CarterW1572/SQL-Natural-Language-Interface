"""Run a fixed set of questions under every prompting strategy.

Run:  python run_experiments.py
Writes results.json (raw data) and results.md (readable report).
"""

import json
from pathlib import Path

from ai_sql import STRATEGIES, StoreAssistant

ROOT = Path(__file__).parent

QUESTIONS = [
    "Which customers have never placed an order?",
    "What is the best-selling product by total quantity sold?",
    "How much revenue did the store make in 2025?",
    "Which brand has brought in the most revenue?",
    "Who is our oldest customer, and what have they bought?",
    "Which customers have an American Express card on file?",
    "What was the busiest month for orders?",
    "Which customers bought a product that is now out of stock, so we can tell them it's backordered?",
    "Which customers under 30 have spent more than $500 in total?",
    "Do any order totals not match the sum of their item prices times quantities?",
]


def run():
    results = []
    for strategy in STRATEGIES:
        assistant = StoreAssistant(strategy=strategy)
        for question in QUESTIONS:
            print(f"[{strategy}] {question}")
            results.append(assistant.ask(question))

    (ROOT / "results.json").write_text(json.dumps(results, indent=2, default=str))
    write_report(results)
    print("Wrote results.json and results.md")


def write_report(results):
    lines = ["# Experiment Results", "", f"Model: `{results[0]['model']}`", ""]
    for i, question in enumerate(QUESTIONS, start=1):
        lines += [f"## {i}. {question}", ""]
        for r in (r for r in results if r["question"] == question):
            lines += [f"### {r['strategy']}", "", "```sql", r["sql"], "```", ""]
            if "error" in r:
                lines += [f"**Error:** `{r['error']}`", ""]
            else:
                shown = r["rows"][:10]
                more = f" (first 10 of {len(r['rows'])})" if len(r["rows"]) > 10 else ""
                lines += [f"Rows{more}: `{shown}`", ""]
            lines += [f"**Answer:** {r['answer']}", ""]
    (ROOT / "results.md").write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    run()
