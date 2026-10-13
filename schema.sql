-- Online store schema (see Schema.png).
-- All money columns (products.price, orders.cost) are stored as INTEGER cents.

CREATE TABLE customers (
    id          INTEGER PRIMARY KEY,
    first_name  VARCHAR(50) NOT NULL,
    last_name   VARCHAR(50) NOT NULL,
    birth_date  DATE        -- 'YYYY-MM-DD'
);

CREATE TABLE customer_payment_info (
    id                 INTEGER PRIMARY KEY,
    customer_id        INTEGER NOT NULL REFERENCES customers(id),
    payment_type_name  VARCHAR(30) NOT NULL,  -- 'Visa', 'Mastercard', 'American Express', 'Discover', 'PayPal'
    cc_num             TEXT                   -- card number; NULL for PayPal
);

CREATE TABLE products (
    id        INTEGER PRIMARY KEY,
    name      VARCHAR(100) NOT NULL,
    brand     VARCHAR(50)  NOT NULL,
    in_stock  INTEGER NOT NULL DEFAULT 0,  -- units currently in inventory
    price     INTEGER NOT NULL             -- price in cents (1999 = $19.99)
);

CREATE TABLE orders (
    id           INTEGER PRIMARY KEY,
    customer_id  INTEGER NOT NULL REFERENCES customers(id),
    cost         INTEGER NOT NULL,  -- order total in cents
    date         DATETIME NOT NULL  -- 'YYYY-MM-DD HH:MM:SS'
);

CREATE TABLE order_items (
    order_id    INTEGER NOT NULL REFERENCES orders(id),
    product_id  INTEGER NOT NULL REFERENCES products(id),
    quantity    INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (order_id, product_id)
);
