# Online Store — AI + SQL Natural Language Interface

My project models the database of a small online electronics store: customers, their saved payment methods, products and inventory, orders, and the items in each order. You can ask it questions in plain English, like "who hasn't ordered anything yet?", and it answers from the data.

![Schema](Schema.png)

## How it works

1. The question and the schema ([schema.sql](schema.sql)) go to `gpt-4o-mini`, which returns a SQLite query.
2. The query runs against [store.db](store.db) on a **read-only** connection, so generated SQL can't change the data.
3. The question, the SQL and the rows go back to GPT, which writes a friendly answer.

## Setup

```bash
pip install -r requirements.txt
```

Copy `secrets.example.json` to `secrets.json` and add your OpenAI API key. `secrets.json` is git-ignored.

```bash
python setup_db.py
```

```bash
python app.py --strategy zero_shot
```

```bash
python run_experiments.py
```

`setup_db.py` rebuilds `store.db` from a fixed random seed. `app.py` is the interactive CLI. `run_experiments.py` runs 10 questions under all three strategies and writes [results.md](results.md).

## Prompting strategies

From [Chang & Fosler-Lussier, *How to Prompt LLMs for Text-to-SQL*](https://arxiv.org/abs/2305.11853):

| Strategy | What the prompt contains |
|---|---|
| `zero_shot` | Schema + question |
| `single_domain` | Schema + 3 example question/SQL pairs written for this store database + question |
| `cross_domain` | A different (library) schema with 3 example question/SQL pairs, then the store schema + question |

## Query it did well on

_TODO: fill in from results.md_

## Question it tripped up on

_TODO: fill in from results.md_

## Strategy comparison

_TODO: fill in from results.md_

## More examples

See [results.md](results.md) for all 10 questions under each strategy (30 runs).

## Notes on the schema

- SQLite has no `bigint` or `enum`, so IDs are `INTEGER PRIMARY KEY` and `cc_num` is `TEXT`. The card numbers are randomly generated fakes.
- Money (`products.price`, `orders.cost`) is stored as integer cents. The schema comments say so, which tests whether the model remembers to divide by 100.
- `order_items` has a composite primary key `(order_id, product_id)`, and every foreign key is declared.
