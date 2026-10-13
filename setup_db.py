"""Create store.db from schema.sql and fill it with sample data.

Run:  python setup_db.py
Re-running deletes and rebuilds the database. The data is generated with a
fixed random seed, so it is the same every time.
"""

import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).parent
DB_PATH = ROOT / "store.db"
SCHEMA_PATH = ROOT / "schema.sql"

CUSTOMERS = [
    ("Emma", "Johnson", "1995-03-14"),
    ("Liam", "Smith", "1988-07-22"),
    ("Olivia", "Brown", "2001-11-02"),
    ("Noah", "Davis", "1979-01-30"),
    ("Ava", "Martinez", "1999-06-18"),
    ("Ethan", "Wilson", "1992-09-05"),
    ("Sophia", "Anderson", "1985-12-25"),
    ("Mason", "Taylor", "2003-04-11"),
    ("Isabella", "Thomas", "1990-08-08"),
    ("Lucas", "Moore", "1975-02-19"),
    ("Mia", "Jackson", "1998-10-31"),
    ("James", "White", "1983-05-27"),
    ("Charlotte", "Harris", "2000-01-15"),
    ("Benjamin", "Clark", "1994-07-04"),
    ("Amelia", "Lewis", "1987-03-03"),
    ("Henry", "Young", "2002-12-12"),
]

# (name, brand, in_stock, price in cents)
PRODUCTS = [
    ("Wireless Earbuds", "Sony", 42, 12999),
    ("Noise Cancelling Headphones", "Bose", 15, 32900),
    ("Bluetooth Speaker", "JBL", 60, 9995),
    ("Smartphone Charger", "Anker", 120, 1999),
    ("USB-C Cable 6ft", "Anker", 200, 1299),
    ("Mechanical Keyboard", "Logitech", 25, 14999),
    ("Wireless Mouse", "Logitech", 80, 3999),
    ("27-inch Monitor", "Dell", 10, 27999),
    ("Laptop Stand", "Rain Design", 35, 4995),
    ("Webcam 1080p", "Logitech", 0, 6999),
    ("Smart Watch", "Garmin", 18, 24999),
    ("Fitness Tracker", "Fitbit", 0, 9995),
    ("Portable SSD 1TB", "Samsung", 50, 10999),
    ("Gaming Controller", "Microsoft", 30, 5999),
    ("E-Reader", "Amazon", 22, 13999),
    ("Desk Lamp", "BenQ", 12, 17900),
    ("Phone Case", "OtterBox", 150, 4995),
    ("Tablet 10-inch", "Samsung", 8, 32999),
    ("Smart Plug 4-pack", "Kasa", 3, 2999),
    ("Backpack", "North Face", 40, 8900),
]

CARD_TYPES = ["Visa", "Mastercard", "American Express", "Discover"]


def fake_card_number(rng, card_type):
    """Random digits with a realistic prefix. Not real card numbers."""
    prefix = {"Visa": "4", "Mastercard": "5", "American Express": "37", "Discover": "6011"}[card_type]
    length = 15 if card_type == "American Express" else 16
    return prefix + "".join(str(rng.randint(0, 9)) for _ in range(length - len(prefix)))


def build(db_path=DB_PATH):
    rng = random.Random(452)
    if db_path.exists():
        db_path.unlink()

    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA_PATH.read_text())

    conn.executemany(
        "INSERT INTO customers (first_name, last_name, birth_date) VALUES (?, ?, ?)",
        CUSTOMERS,
    )
    conn.executemany(
        "INSERT INTO products (name, brand, in_stock, price) VALUES (?, ?, ?, ?)",
        PRODUCTS,
    )

    # Every customer gets 1-2 payment methods; some use PayPal (no card number).
    for customer_id in range(1, len(CUSTOMERS) + 1):
        for _ in range(rng.choice([1, 1, 2])):
            if rng.random() < 0.2:
                payment = ("PayPal", None)
            else:
                card = rng.choice(CARD_TYPES)
                payment = (card, fake_card_number(rng, card))
            conn.execute(
                "INSERT INTO customer_payment_info (customer_id, payment_type_name, cc_num) VALUES (?, ?, ?)",
                (customer_id, *payment),
            )

    # About 40 orders from Jan 2025 through Sep 2026. Customers 15 and 16 never order.
    prices = {i + 1: p[3] for i, p in enumerate(PRODUCTS)}
    start = datetime(2025, 1, 1)
    order_dates = sorted(
        start + timedelta(minutes=rng.randint(0, 640 * 24 * 60)) for _ in range(40)
    )
    for order_id, when in enumerate(order_dates, start=1):
        customer_id = rng.randint(1, len(CUSTOMERS) - 2)
        items = {pid: rng.choice([1, 1, 1, 2, 3]) for pid in rng.sample(list(prices), rng.randint(1, 4))}
        cost = sum(prices[pid] * qty for pid, qty in items.items())
        conn.execute(
            "INSERT INTO orders (id, customer_id, cost, date) VALUES (?, ?, ?, ?)",
            (order_id, customer_id, cost, when.strftime("%Y-%m-%d %H:%M:%S")),
        )
        conn.executemany(
            "INSERT INTO order_items (order_id, product_id, quantity) VALUES (?, ?, ?)",
            [(order_id, pid, qty) for pid, qty in items.items()],
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    build()
    conn = sqlite3.connect(DB_PATH)
    for table in ["customers", "customer_payment_info", "products", "orders", "order_items"]:
        count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        print(f"{table:24} {count} rows")
    conn.close()
    print(f"Created {DB_PATH.name}")
