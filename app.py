"""Ask the online store database questions in plain English.

Run:  python app.py [--strategy zero_shot|single_domain|cross_domain] [--model gpt-4o-mini]
Type 'quit' to exit.
"""

import argparse

from ai_sql import MODEL, STRATEGIES, StoreAssistant


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--strategy", choices=STRATEGIES, default="zero_shot")
    parser.add_argument("--model", default=MODEL)
    args = parser.parse_args()

    assistant = StoreAssistant(model=args.model, strategy=args.strategy)
    print(f"Online store assistant ({args.model}, {args.strategy}). Type 'quit' to exit.\n")

    while True:
        try:
            question = input("Question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if question.lower() in {"quit", "exit", "q"}:
            break
        if not question:
            continue

        result = assistant.ask(question)
        print(f"\nSQL:\n{result['sql']}\n")
        if "error" not in result:
            print(f"Rows ({len(result['rows'])}): {result['rows'][:10]}\n")
        print(f"Answer: {result['answer']}\n")


if __name__ == "__main__":
    main()
