# Experiment Results

Model: `gpt-4o-mini`

## 1. Which customers have never placed an order?

### zero_shot

```sql
SELECT first_name, last_name FROM customers WHERE id NOT IN (SELECT DISTINCT customer_id FROM orders);
```

Rows: `[('Amelia', 'Lewis'), ('Henry', 'Young')]`

**Answer:** The customers who have never placed an order are Amelia Lewis and Henry Young.

### single_domain

```sql
SELECT first_name, last_name FROM customers WHERE id NOT IN (SELECT customer_id FROM orders);
```

Rows: `[('Amelia', 'Lewis'), ('Henry', 'Young')]`

**Answer:** The customers who have never placed an order are Amelia Lewis and Henry Young.

### cross_domain

```sql
SELECT c.first_name, c.last_name
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.id
WHERE o.id IS NULL;
```

Rows: `[('Amelia', 'Lewis'), ('Henry', 'Young')]`

**Answer:** The customers who have never placed an order are Amelia Lewis and Henry Young.

## 2. What is the best-selling product by total quantity sold?

### zero_shot

```sql
SELECT p.id, p.name, SUM(oi.quantity) AS total_quantity_sold
FROM products p
JOIN order_items oi ON p.id = oi.product_id
GROUP BY p.id, p.name
ORDER BY total_quantity_sold DESC
LIMIT 1;
```

Rows: `[(3, 'Bluetooth Speaker', 17)]`

**Answer:** The best-selling product by total quantity sold is the Bluetooth Speaker, with a total of 17 units sold.

### single_domain

```sql
SELECT p.name, SUM(oi.quantity) AS total_quantity_sold
FROM products p
JOIN order_items oi ON oi.product_id = p.id
GROUP BY p.id
ORDER BY total_quantity_sold DESC
LIMIT 1;
```

Rows: `[('Webcam 1080p', 17)]`

**Answer:** The best-selling product by total quantity sold is the Webcam 1080p, with a total of 17 units sold.

### cross_domain

```sql
SELECT p.name, SUM(oi.quantity) AS total_sold
FROM products p
JOIN order_items oi ON p.id = oi.product_id
GROUP BY p.id
ORDER BY total_sold DESC
LIMIT 1;
```

Rows: `[('Webcam 1080p', 17)]`

**Answer:** The best-selling product by total quantity sold is the Webcam 1080p, with a total of 17 units sold.

## 3. How much revenue did the store make in 2025?

### zero_shot

```sql
SELECT SUM(cost) AS total_revenue
FROM orders
WHERE strftime('%Y', date) = '2025';
```

Rows: `[(868369,)]`

**Answer:** In 2025, the store made a total revenue of $8,683.69.

### single_domain

```sql
SELECT SUM(cost) / 100.0 AS total_revenue_dollars
FROM orders
WHERE strftime('%Y', date) = '2025';
```

Rows: `[(8683.69,)]`

**Answer:** In 2025, the store made a total revenue of $8,683.69.

### cross_domain

```sql
SELECT SUM(cost) AS total_revenue
FROM orders
WHERE strftime('%Y', date) = '2025';
```

Rows: `[(868369,)]`

**Answer:** In 2025, the store made a total revenue of $8,683.69.

## 4. Which brand has brought in the most revenue?

### zero_shot

```sql
SELECT p.brand, SUM(o.cost) AS total_revenue
FROM products p
JOIN order_items oi ON p.id = oi.product_id
JOIN orders o ON oi.order_id = o.id
GROUP BY p.brand
ORDER BY total_revenue DESC
LIMIT 1;
```

Rows: `[('Logitech', 750807)]`

**Answer:** The brand that has brought in the most revenue is Logitech, with a total revenue of $7,508.07.

### single_domain

```sql
SELECT p.brand, SUM(o.cost) AS total_revenue
FROM products p
JOIN order_items oi ON oi.product_id = p.id
JOIN orders o ON o.id = oi.order_id
GROUP BY p.brand
ORDER BY total_revenue DESC
LIMIT 1;
```

Rows: `[('Logitech', 750807)]`

**Answer:** The brand that has brought in the most revenue is Logitech, with a total revenue of $7,508.07.

### cross_domain

```sql
SELECT p.brand, SUM(o.cost) AS total_revenue
FROM products p
JOIN order_items oi ON oi.product_id = p.id
JOIN orders o ON o.id = oi.order_id
GROUP BY p.brand
ORDER BY total_revenue DESC
LIMIT 1;
```

Rows: `[('Logitech', 750807)]`

**Answer:** The brand that has brought in the most revenue is Logitech, with a total revenue of $7,508.07.

## 5. Who is our oldest customer, and what have they bought?

### zero_shot

```sql
SELECT c.first_name, c.last_name, p.name, oi.quantity
FROM customers c
JOIN orders o ON c.id = o.customer_id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
WHERE c.birth_date = (SELECT MIN(birth_date) FROM customers);
```

Rows: `[('Lucas', 'Moore', 'Noise Cancelling Headphones', 1), ('Lucas', 'Moore', 'Gaming Controller', 1), ('Lucas', 'Moore', 'Gaming Controller', 2), ('Lucas', 'Moore', 'Smartphone Charger', 1), ('Lucas', 'Moore', 'Smart Plug 4-pack', 1), ('Lucas', 'Moore', 'Noise Cancelling Headphones', 1), ('Lucas', 'Moore', 'Laptop Stand', 3), ('Lucas', 'Moore', 'Gaming Controller', 1)]`

**Answer:** Our oldest customer is Lucas Moore. He has purchased the following items:

- Noise Cancelling Headphones (2 total)
- Gaming Controller (4 total)
- Smartphone Charger (1)
- Smart Plug 4-pack (1)
- Laptop Stand (3)

If you have any more questions or need further assistance, feel free to ask!

### single_domain

```sql
SELECT c.first_name, c.last_name, p.name
FROM customers c
JOIN orders o ON o.customer_id = c.id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id
WHERE c.birth_date = (SELECT MIN(birth_date) FROM customers);
```

Rows: `[('Lucas', 'Moore', 'Noise Cancelling Headphones'), ('Lucas', 'Moore', 'Gaming Controller'), ('Lucas', 'Moore', 'Gaming Controller'), ('Lucas', 'Moore', 'Smartphone Charger'), ('Lucas', 'Moore', 'Noise Cancelling Headphones'), ('Lucas', 'Moore', 'Laptop Stand'), ('Lucas', 'Moore', 'Gaming Controller'), ('Lucas', 'Moore', 'Smart Plug 4-pack')]`

**Answer:** Our oldest customer is Lucas Moore. He has purchased the following items:

1. Noise Cancelling Headphones
2. Gaming Controller (three times)
3. Smartphone Charger
4. Laptop Stand
5. Smart Plug 4-pack

If you have any more questions or need further assistance, feel free to ask!

### cross_domain

```sql
SELECT c.first_name, c.last_name, p.name, oi.quantity
FROM customers c
JOIN orders o ON o.customer_id = c.id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id
WHERE c.birth_date = (SELECT MIN(birth_date) FROM customers);
```

Rows: `[('Lucas', 'Moore', 'Noise Cancelling Headphones', 1), ('Lucas', 'Moore', 'Gaming Controller', 1), ('Lucas', 'Moore', 'Gaming Controller', 2), ('Lucas', 'Moore', 'Smartphone Charger', 1), ('Lucas', 'Moore', 'Smart Plug 4-pack', 1), ('Lucas', 'Moore', 'Noise Cancelling Headphones', 1), ('Lucas', 'Moore', 'Laptop Stand', 3), ('Lucas', 'Moore', 'Gaming Controller', 1)]`

**Answer:** Our oldest customer is Lucas Moore. He has purchased the following items:

- Noise Cancelling Headphones (1 unit)
- Gaming Controller (1 unit)
- Gaming Controller (2 units)
- Smartphone Charger (1 unit)
- Smart Plug 4-pack (1 unit)
- Noise Cancelling Headphones (1 unit)
- Laptop Stand (3 units)
- Gaming Controller (1 unit)

If you have any more questions or need further assistance, feel free to ask!

## 6. Which customers have an American Express card on file?

### zero_shot

```sql
SELECT DISTINCT c.first_name, c.last_name 
FROM customers c 
JOIN customer_payment_info cpi ON c.id = cpi.customer_id 
WHERE cpi.payment_type_name = 'American Express';
```

Rows: `[('Emma', 'Johnson'), ('Liam', 'Smith'), ('Olivia', 'Brown'), ('Noah', 'Davis'), ('Sophia', 'Anderson')]`

**Answer:** The customers who have an American Express card on file are:

- Emma Johnson
- Liam Smith
- Olivia Brown
- Noah Davis
- Sophia Anderson

### single_domain

```sql
SELECT c.first_name, c.last_name
FROM customers c
JOIN customer_payment_info cpi ON cpi.customer_id = c.id
WHERE cpi.payment_type_name = 'American Express';
```

Rows: `[('Emma', 'Johnson'), ('Liam', 'Smith'), ('Olivia', 'Brown'), ('Noah', 'Davis'), ('Sophia', 'Anderson')]`

**Answer:** The customers who have an American Express card on file are:

- Emma Johnson
- Liam Smith
- Olivia Brown
- Noah Davis
- Sophia Anderson

### cross_domain

```sql
SELECT c.first_name, c.last_name
FROM customers c
JOIN customer_payment_info cpi ON cpi.customer_id = c.id
WHERE cpi.payment_type_name = 'American Express';
```

Rows: `[('Emma', 'Johnson'), ('Liam', 'Smith'), ('Olivia', 'Brown'), ('Noah', 'Davis'), ('Sophia', 'Anderson')]`

**Answer:** The customers who have an American Express card on file are:

- Emma Johnson
- Liam Smith
- Olivia Brown
- Noah Davis
- Sophia Anderson

## 7. What was the busiest month for orders?

### zero_shot

```sql
SELECT strftime('%Y-%m', date) AS month, COUNT(*) AS order_count
FROM orders
GROUP BY month
ORDER BY order_count DESC
LIMIT 1;
```

Rows: `[('2026-07', 5)]`

**Answer:** The busiest month for orders was July 2026, with a total of 5 orders placed.

### single_domain

```sql
SELECT strftime('%Y-%m', date) AS month, COUNT(*) AS order_count
FROM orders
GROUP BY month
ORDER BY order_count DESC
LIMIT 1;
```

Rows: `[('2026-07', 5)]`

**Answer:** The busiest month for orders was July 2026, with a total of 5 orders placed.

### cross_domain

```sql
SELECT strftime('%Y-%m', date) AS month, COUNT(*) AS order_count
FROM orders
GROUP BY month
ORDER BY order_count DESC
LIMIT 1;
```

Rows: `[('2026-07', 5)]`

**Answer:** The busiest month for orders was July 2026, with a total of 5 orders placed.

## 8. Which customers bought a product that is now out of stock, so we can tell them it's backordered?

### zero_shot

```sql
SELECT DISTINCT c.id, c.first_name, c.last_name
FROM customers c
JOIN orders o ON c.id = o.customer_id
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
WHERE p.in_stock = 0;
```

Rows: `[(8, 'Mason', 'Taylor'), (3, 'Olivia', 'Brown'), (9, 'Isabella', 'Thomas'), (14, 'Benjamin', 'Clark'), (6, 'Ethan', 'Wilson'), (13, 'Charlotte', 'Harris'), (12, 'James', 'White'), (5, 'Ava', 'Martinez')]`

**Answer:** The following customers bought a product that is now out of stock and can be informed that it's backordered:

1. Mason Taylor
2. Olivia Brown
3. Isabella Thomas
4. Benjamin Clark
5. Ethan Wilson
6. Charlotte Harris
7. James White
8. Ava Martinez

You can reach out to them to let them know about the backorder!

### single_domain

```sql
SELECT DISTINCT c.first_name, c.last_name
FROM customers c
JOIN orders o ON o.customer_id = c.id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id
WHERE p.in_stock = 0;
```

Rows: `[('Mason', 'Taylor'), ('Olivia', 'Brown'), ('Isabella', 'Thomas'), ('Benjamin', 'Clark'), ('Ethan', 'Wilson'), ('Charlotte', 'Harris'), ('James', 'White'), ('Ava', 'Martinez')]`

**Answer:** The following customers bought a product that is now out of stock and can be informed that it's backordered:

- Mason Taylor
- Olivia Brown
- Isabella Thomas
- Benjamin Clark
- Ethan Wilson
- Charlotte Harris
- James White
- Ava Martinez

You can reach out to them with the update!

### cross_domain

```sql
SELECT DISTINCT c.first_name, c.last_name
FROM customers c
JOIN orders o ON o.customer_id = c.id
JOIN order_items oi ON oi.order_id = o.id
JOIN products p ON p.id = oi.product_id
WHERE p.in_stock = 0;
```

Rows: `[('Mason', 'Taylor'), ('Olivia', 'Brown'), ('Isabella', 'Thomas'), ('Benjamin', 'Clark'), ('Ethan', 'Wilson'), ('Charlotte', 'Harris'), ('James', 'White'), ('Ava', 'Martinez')]`

**Answer:** The following customers bought a product that is now out of stock and can be informed that it's backordered:

- Mason Taylor
- Olivia Brown
- Isabella Thomas
- Benjamin Clark
- Ethan Wilson
- Charlotte Harris
- James White
- Ava Martinez

You can reach out to them with the update!

## 9. Which customers under 30 have spent more than $500 in total?

### zero_shot

```sql
SELECT c.id, c.first_name, c.last_name
FROM customers c
JOIN orders o ON c.id = o.customer_id
WHERE (julianday('now') - julianday(c.birth_date)) / 365 < 30
GROUP BY c.id
HAVING SUM(o.cost) > 50000;
```

Rows: `[(3, 'Olivia', 'Brown'), (5, 'Ava', 'Martinez'), (8, 'Mason', 'Taylor')]`

**Answer:** The customers under 30 who have spent more than $500 in total are:

1. Olivia Brown
2. Ava Martinez
3. Mason Taylor

If you have any more questions or need further assistance, feel free to ask!

### single_domain

```sql
SELECT c.first_name, c.last_name, SUM(o.cost) / 100.0 AS total_spent_dollars
FROM customers c
JOIN orders o ON o.customer_id = c.id
WHERE strftime('%Y', 'now') - strftime('%Y', c.birth_date) < 30
GROUP BY c.id
HAVING total_spent_dollars > 500
ORDER BY total_spent_dollars DESC;
```

Rows: `[('Olivia', 'Brown', 3675.67), ('Ava', 'Martinez', 2469.85), ('Mason', 'Taylor', 2038.76)]`

**Answer:** It looks like there are no customers under 30 who have spent more than $500 in total. The customers listed, Olivia Brown, Ava Martinez, and Mason Taylor, all spent significantly more than that, but they are not under 30 years old based on the data we have. If you have any other questions or need further assistance, feel free to ask!

### cross_domain

```sql
SELECT c.first_name, c.last_name
FROM customers c
JOIN orders o ON o.customer_id = c.id
WHERE (julianday('now') - julianday(c.birth_date)) / 365 < 30
GROUP BY c.id
HAVING SUM(o.cost) > 50000;
```

Rows: `[('Olivia', 'Brown'), ('Ava', 'Martinez'), ('Mason', 'Taylor')]`

**Answer:** The customers under 30 who have spent more than $500 in total are:

- Olivia Brown
- Ava Martinez
- Mason Taylor

## 10. Do any order totals not match the sum of their item prices times quantities?

### zero_shot

```sql
SELECT o.id, o.cost, SUM(p.price * oi.quantity) AS calculated_total
FROM orders o
JOIN order_items oi ON o.id = oi.order_id
JOIN products p ON oi.product_id = p.id
GROUP BY o.id
HAVING o.cost != SUM(p.price * oi.quantity);
```

Rows: `[]`

**Answer:** It looks like all order totals match the sum of their item prices times quantities. There are no discrepancies found in the data. If you have any other questions or need further assistance, feel free to ask!

### single_domain

```sql
SELECT o.id
FROM orders o
JOIN order_items oi ON oi.order_id = o.id
GROUP BY o.id
HAVING o.cost != SUM(oi.quantity * (SELECT price FROM products WHERE id = oi.product_id));
```

Rows: `[]`

**Answer:** It looks like all order totals match the sum of their item prices times quantities. There are no discrepancies found in the orders. If you have any other questions or need further assistance, feel free to ask!

### cross_domain

```sql
SELECT o.id
FROM orders o
LEFT JOIN order_items oi ON oi.order_id = o.id
GROUP BY o.id
HAVING o.cost != SUM(oi.quantity * (SELECT price FROM products WHERE id = oi.product_id));
```

Rows: `[]`

**Answer:** It looks like all order totals match the sum of their item prices times quantities. There are no discrepancies found in the orders. If you have any more questions or need further assistance, feel free to ask!
