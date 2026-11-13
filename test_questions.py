"""test_questions.py - 30 questions with the correct ("gold") SQL, written by YOU.
Never let the AI write the answer key."""

REV = "oi.quantity * p.unit_price * (1 - oi.discount)"
JOIN_SALES = ("FROM order_items oi JOIN orders o ON o.order_id = oi.order_id "
              "JOIN products p ON p.product_id = oi.product_id "
              "JOIN customers c ON c.customer_id = o.customer_id WHERE o.status = 'Delivered'")

QUESTIONS = [
    # ---------------- easy: one table ----------------
    ("easy", "How many customers do we have?", "SELECT COUNT(*) FROM customers"),
    ("easy", "How many orders were placed in total?", "SELECT COUNT(*) FROM orders"),
    ("easy", "How many products are in the Technology category?",
     "SELECT COUNT(*) FROM products WHERE category = 'Technology'"),
    ("easy", "List all the different ship modes.", "SELECT DISTINCT ship_mode FROM orders"),
    ("easy", "What is the name of our most expensive product?",
     "SELECT product_name FROM products ORDER BY unit_price DESC LIMIT 1"),
    ("easy", "How many orders were cancelled?",
     "SELECT COUNT(*) FROM orders WHERE status = 'Cancelled'"),
    ("easy", "How many customers are in the Corporate segment?",
     "SELECT COUNT(*) FROM customers WHERE segment = 'Corporate'"),
    ("easy", "What is the average unit price of Furniture products?",
     "SELECT AVG(unit_price) FROM products WHERE category = 'Furniture'"),
    ("easy", "How many customers live in Pune?",
     "SELECT COUNT(*) FROM customers WHERE city = 'Pune'"),
    ("easy", "How many different product categories are there?",
     "SELECT COUNT(DISTINCT category) FROM products"),
    # ---------------- medium: joins and grouping ----------------
    ("medium", "How many orders did each region place?",
     "SELECT c.region, COUNT(*) FROM orders o JOIN customers c ON c.customer_id = o.customer_id "
     "GROUP BY c.region"),
    ("medium", "What is the total revenue for each product category?",
     f"SELECT p.category, SUM({REV}) {JOIN_SALES} GROUP BY p.category"),
    ("medium", "What is our worst-selling region by revenue?",
     f"SELECT c.region {JOIN_SALES} GROUP BY c.region ORDER BY SUM({REV}) ASC LIMIT 1"),
    ("medium", "Who are our top 5 customers by revenue?",
     f"SELECT c.customer_name {JOIN_SALES} GROUP BY c.customer_id "
     f"ORDER BY SUM({REV}) DESC LIMIT 5"),
    ("medium", "How many orders were placed with each ship mode?",
     "SELECT ship_mode, COUNT(*) FROM orders GROUP BY ship_mode"),
    ("medium", "What is the average discount given in each category?",
     "SELECT p.category, AVG(oi.discount) FROM order_items oi "
     "JOIN products p ON p.product_id = oi.product_id GROUP BY p.category"),
    ("medium", "How many units were sold in each sub-category?",
     f"SELECT p.sub_category, SUM(oi.quantity) {JOIN_SALES} GROUP BY p.sub_category"),
    ("medium", "Which city has the most customers?",
     "SELECT city FROM customers GROUP BY city ORDER BY COUNT(*) DESC LIMIT 1"),
    ("medium", "What is the revenue for each customer segment?",
     f"SELECT c.segment, SUM({REV}) {JOIN_SALES} GROUP BY c.segment"),
    ("medium", "How many orders were placed in 2025?",
     "SELECT COUNT(*) FROM orders WHERE strftime('%Y', order_date) = '2025'"),
    ("medium", "What percentage of orders were returned?",
     "SELECT 100.0 * SUM(status = 'Returned') / COUNT(*) FROM orders"),
    ("medium", "Which product has sold the most units?",
     f"SELECT p.product_name {JOIN_SALES} GROUP BY p.product_id "
     "ORDER BY SUM(oi.quantity) DESC LIMIT 1"),
    # ---------------- hard: dates, subqueries, windows ----------------
    ("hard", "What was the revenue in each month of 2025?",
     f"SELECT strftime('%m', o.order_date), SUM({REV}) {JOIN_SALES} "
     "AND strftime('%Y', o.order_date) = '2025' GROUP BY strftime('%m', o.order_date)"),
    ("hard", "Which category made the most profit? "
             "Profit = quantity * (price after discount - unit cost).",
     "SELECT p.category FROM order_items oi JOIN orders o ON o.order_id = oi.order_id "
     "JOIN products p ON p.product_id = oi.product_id WHERE o.status = 'Delivered' "
     "GROUP BY p.category "
     "ORDER BY SUM(oi.quantity * (p.unit_price * (1 - oi.discount) - p.unit_cost)) DESC LIMIT 1"),
    ("hard", "How many customers have never placed an order?",
     "SELECT COUNT(*) FROM customers WHERE customer_id NOT IN (SELECT customer_id FROM orders)"),
    ("hard", "For each region, which category earns the most revenue?",
     f"SELECT region, category FROM (SELECT c.region AS region, p.category AS category, "
     f"ROW_NUMBER() OVER (PARTITION BY c.region ORDER BY SUM({REV}) DESC) AS rk "
     f"{JOIN_SALES} GROUP BY c.region, p.category) WHERE rk = 1"),
    ("hard", "What is the average order value?",
     f"SELECT SUM({REV}) / COUNT(DISTINCT o.order_id) {JOIN_SALES}"),
    ("hard", "How many customers placed more than 10 orders?",
     "SELECT COUNT(*) FROM (SELECT customer_id FROM orders GROUP BY customer_id "
     "HAVING COUNT(*) > 10)"),
    ("hard", "By what percentage did revenue grow from 2024 to 2025?",
     f"SELECT 100.0 * (SUM(CASE WHEN strftime('%Y', o.order_date) = '2025' THEN {REV} END) / "
     f"SUM(CASE WHEN strftime('%Y', o.order_date) = '2024' THEN {REV} END) - 1) {JOIN_SALES}"),
    ("hard", "Which region has the highest return rate (returned orders divided by all orders)?",
     "SELECT c.region FROM orders o JOIN customers c ON c.customer_id = o.customer_id "
     "GROUP BY c.region ORDER BY 1.0 * SUM(o.status = 'Returned') / COUNT(*) DESC LIMIT 1"),
]
