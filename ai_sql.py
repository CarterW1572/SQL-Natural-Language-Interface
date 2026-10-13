"""Natural language -> SQL -> natural language, using OpenAI and SQLite.

Pipeline (per the assignment):
  1. Send the question plus the schema to GPT and get back a SQL query.
  2. Run that query against store.db.
  3. Send the question, query and rows back to GPT for a friendly answer.

Step 1 supports the three prompting strategies from Chang & Fosler-Lussier,
"How to Prompt LLMs for Text-to-SQL" (https://arxiv.org/abs/2305.11853):
  zero_shot      - schema and question only
  single_domain  - adds example question/SQL pairs written for THIS database
  cross_domain   - adds example question/SQL pairs from a DIFFERENT database
"""

import json
import re
import sqlite3
from pathlib import Path

from openai import OpenAI

ROOT = Path(__file__).parent
DB_PATH = ROOT / "store.db"
SCHEMA_PATH = ROOT / "schema.sql"
SECRETS_PATH = ROOT / "secrets.json"

MODEL = "gpt-4o-mini"
STRATEGIES = ["zero_shot", "single_domain", "cross_domain"]

SQL_INSTRUCTIONS = (
    "You are an expert SQLite developer. Given the database schema and a question, "
    "write one SQLite SELECT query that answers it. Respond with only the SQL, "
    "no explanation and no markdown code fences."
)

# Examples written against our own store schema.
SINGLE_DOMAIN_EXAMPLES = [
    (
        "Which products are out of stock?",
        "SELECT name, brand FROM products WHERE in_stock = 0;",
    ),
    (
        "How much has each customer spent in total, in dollars?",
        "SELECT c.first_name, c.last_name, SUM(o.cost) / 100.0 AS total_spent_dollars\n"
        "FROM customers c JOIN orders o ON o.customer_id = c.id\n"
        "GROUP BY c.id ORDER BY total_spent_dollars DESC;",
    ),
    (
        "What products did Emma Johnson buy?",
        "SELECT DISTINCT p.name\n"
        "FROM customers c\n"
        "JOIN orders o ON o.customer_id = c.id\n"
        "JOIN order_items oi ON oi.order_id = o.id\n"
        "JOIN products p ON p.id = oi.product_id\n"
        "WHERE c.first_name = 'Emma' AND c.last_name = 'Johnson';",
    ),
]

# A small, unrelated database (a library) with its own examples.
CROSS_DOMAIN_SCHEMA = """CREATE TABLE authors (id INTEGER PRIMARY KEY, name TEXT, country TEXT);
CREATE TABLE books (id INTEGER PRIMARY KEY, title TEXT, author_id INTEGER REFERENCES authors(id), published_year INTEGER, copies INTEGER);
CREATE TABLE members (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, joined DATE);
CREATE TABLE loans (id INTEGER PRIMARY KEY, book_id INTEGER REFERENCES books(id), member_id INTEGER REFERENCES members(id), loan_date DATE, return_date DATE);"""

CROSS_DOMAIN_EXAMPLES = [
    (
        "Which books have no copies available?",
        "SELECT title FROM books WHERE copies = 0;",
    ),
    (
        "How many books has each member borrowed?",
        "SELECT m.first_name, m.last_name, COUNT(l.id) AS books_borrowed\n"
        "FROM members m LEFT JOIN loans l ON l.member_id = m.id\n"
        "GROUP BY m.id ORDER BY books_borrowed DESC;",
    ),
    (
        "Which authors did Sarah Lee borrow books by?",
        "SELECT DISTINCT a.name\n"
        "FROM members m\n"
        "JOIN loans l ON l.member_id = m.id\n"
        "JOIN books b ON b.id = l.book_id\n"
        "JOIN authors a ON a.id = b.author_id\n"
        "WHERE m.first_name = 'Sarah' AND m.last_name = 'Lee';",
    ),
]

ANSWER_INSTRUCTIONS = (
    "You are a helpful assistant for an online store. You are given a customer-service "
    "question, the SQL query that was run to answer it, and the rows it returned. "
    "Answer the question in plain, friendly language using only that data. "
    "Money columns named price or cost are in cents, so convert them to dollars, "
    "unless the column name says it is already in dollars. If the data does not "
    "answer the question, say so."
)


def load_api_key():
    secrets = json.loads(SECRETS_PATH.read_text())
    # Accept the misspelled key that is already in secrets.json, too.
    for key in ("openai_api_key", "onpenai_api_key"):
        if secrets.get(key):
            return secrets[key]
    raise KeyError(f"No OpenAI API key found in {SECRETS_PATH.name}")


def schema_text():
    return SCHEMA_PATH.read_text()


def format_examples(examples):
    return "\n\n".join(f"Question: {q}\nSQL: {sql}" for q, sql in examples)


def build_sql_prompt(question, strategy):
    if strategy == "zero_shot":
        return f"Schema:\n{schema_text()}\n\nQuestion: {question}\nSQL:"
    if strategy == "single_domain":
        return (
            f"Schema:\n{schema_text()}\n\n"
            f"Examples:\n{format_examples(SINGLE_DOMAIN_EXAMPLES)}\n\n"
            f"Question: {question}\nSQL:"
        )
    if strategy == "cross_domain":
        return (
            f"Here is an example database and some example queries.\n\n"
            f"Example schema:\n{CROSS_DOMAIN_SCHEMA}\n\n"
            f"Examples:\n{format_examples(CROSS_DOMAIN_EXAMPLES)}\n\n"
            f"Now write a query for this database.\n\n"
            f"Schema:\n{schema_text()}\n\nQuestion: {question}\nSQL:"
        )
    raise ValueError(f"Unknown strategy {strategy!r}; choose from {STRATEGIES}")


def clean_sql(text):
    """Strip markdown fences in case the model adds them anyway."""
    match = re.search(r"```(?:sql)?\s*(.*?)```", text, re.DOTALL | re.IGNORECASE)
    if match:
        text = match.group(1)
    return text.strip()


class StoreAssistant:
    def __init__(self, model=MODEL, strategy="zero_shot"):
        self.client = OpenAI(api_key=load_api_key())
        self.model = model
        self.strategy = strategy

    def _chat(self, system, user):
        response = self.client.chat.completions.create(
            model=self.model,
            temperature=0,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        )
        return response.choices[0].message.content

    def generate_sql(self, question):
        return clean_sql(self._chat(SQL_INSTRUCTIONS, build_sql_prompt(question, self.strategy)))

    @staticmethod
    def run_sql(sql):
        """Run a query on a read-only connection so GPT can't modify the data."""
        conn = sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)
        try:
            cursor = conn.execute(sql)
            columns = [d[0] for d in cursor.description or []]
            return columns, cursor.fetchall()
        finally:
            conn.close()

    def friendly_answer(self, question, sql, columns, rows):
        data = json.dumps({"columns": columns, "rows": rows[:100]}, default=str)
        prompt = f"Question: {question}\n\nSQL:\n{sql}\n\nResult:\n{data}"
        return self._chat(ANSWER_INSTRUCTIONS, prompt)

    def ask(self, question):
        """Run the full pipeline. Returns a dict describing every step."""
        result = {"question": question, "strategy": self.strategy, "model": self.model}
        result["sql"] = self.generate_sql(question)
        try:
            columns, rows = self.run_sql(result["sql"])
        except sqlite3.Error as e:
            result["error"] = str(e)
            result["answer"] = f"The generated SQL failed to run: {e}"
            return result
        result["columns"] = columns
        result["rows"] = rows
        result["answer"] = self.friendly_answer(question, result["sql"], columns, rows)
        return result
