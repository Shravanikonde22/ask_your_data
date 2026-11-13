"""Creates shop.db: a small multi-table e-commerce database (SQLite)."""
import sqlite3
import numpy as np
import pandas as pd

rng = np.random.default_rng(11)

SCHEMA = """
CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT,
    city TEXT,
    region TEXT,        -- North, South, East, West, Central
    segment TEXT,       -- Consumer, Corporate, Home Office
    signup_date TEXT    -- YYYY-MM-DD
);
CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT,
    category TEXT,      -- Furniture, Technology, Office Supplies
    sub_category TEXT,
    unit_price REAL,    -- selling price in rupees
    unit_cost REAL      -- what it costs us, in rupees
);
CREATE TABLE orders (
    order_id INTEGER PRIMARY KEY,
    customer_id INTEGER REFERENCES customers(customer_id),
    order_date TEXT,    -- YYYY-MM-DD
    ship_mode TEXT,     -- Standard, Express, Same Day
    status TEXT         -- Delivered, Cancelled, Returned
);
CREATE TABLE order_items (
    item_id INTEGER PRIMARY KEY,
    order_id INTEGER REFERENCES orders(order_id),
    product_id INTEGER REFERENCES products(product_id),
    quantity INTEGER,
    discount REAL       -- 0.0 to 0.3 (0.1 means 10% off)
);
"""

# ---------- customers ----------
region_cities = {
    "West": ["Pune", "Mumbai", "Ahmedabad"], "South": ["Chennai", "Bengaluru", "Hyderabad"],
    "North": ["Delhi", "Jaipur", "Lucknow"], "East": ["Kolkata", "Patna"],
    "Central": ["Bhopal", "Nagpur"]}
regions = list(region_cities)
region_p = [0.30, 0.28, 0.20, 0.14, 0.08]
first = ["Aarav", "Diya", "Rohan", "Sneha", "Kabir", "Meera", "Arjun", "Isha", "Vikram", "Anaya",
         "Nikhil", "Priya", "Rahul", "Tara", "Yash", "Kavya", "Dev", "Riya", "Aditya", "Neha"]
last = ["Sharma", "Patil", "Iyer", "Gupta", "Reddy", "Das", "Khan", "Joshi", "Nair", "Singh",
        "Kulkarni", "Mehta", "Bose", "Rao", "Verma"]
n_cust = 300
cust_region = rng.choice(regions, n_cust, p=region_p)
customers = pd.DataFrame({
    "customer_id": range(1, n_cust + 1),
    "customer_name": [f"{first[i % 20]} {last[(i * 7) % 15]} {i}" for i in range(n_cust)],
    "city": [rng.choice(region_cities[r]) for r in cust_region],
    "region": cust_region,
    "segment": rng.choice(["Consumer", "Corporate", "Home Office"], n_cust, p=[0.5, 0.3, 0.2]),
    "signup_date": pd.to_datetime("2023-01-01")
                   + pd.to_timedelta(rng.integers(0, 700, n_cust), "D"),
})
customers["signup_date"] = customers["signup_date"].dt.strftime("%Y-%m-%d")

# ---------- products ----------
spec = {  # (category, sub_category): (min_price, max_price)
    ("Furniture", "Chairs"): (2500, 9000), ("Furniture", "Tables"): (6000, 25000),
    ("Furniture", "Bookcases"): (4000, 15000), ("Technology", "Phones"): (8000, 80000),
    ("Technology", "Laptops"): (30000, 120000), ("Technology", "Accessories"): (300, 4000),
    ("Office Supplies", "Paper"): (150, 900), ("Office Supplies", "Binders"): (100, 600),
    ("Office Supplies", "Pens"): (50, 500)}
adjectives = ["Classic", "Pro", "Lite", "Max", "Eco"]
rows = []
for (cat, sub), (lo, hi) in spec.items():
    for k in range(4):
        price = round(float(rng.uniform(lo, hi)), 2)
        rows.append((cat, sub, f"{adjectives[k]} {sub[:-1] if sub.endswith('s') else sub}", price,
                     round(price * float(rng.uniform(0.55, 0.85)), 2)))
products = pd.DataFrame(rows, columns=["category", "sub_category", "product_name",
                                       "unit_price", "unit_cost"])
products["product_name"] = products["product_name"] + " " + products.index.astype(str)
products.insert(0, "product_id", range(1, len(products) + 1))
products = products[["product_id", "product_name", "category", "sub_category",
                     "unit_price", "unit_cost"]]

# ---------- orders ----------
n_orders = 3000
days = np.arange(731)  # 2024-01-01 .. 2025-12-31
month = pd.to_datetime("2024-01-01") + pd.to_timedelta(days, "D")
day_w = (1 + 0.6 * days / 730) * (1 + 0.3 * (month.month >= 10))  # growth + Q4 rush
day_w = day_w / day_w.sum()
order_days = rng.choice(days, n_orders, p=day_w)
cust_w = rng.pareto(1.5, n_cust) + 0.2
cust_w[rng.choice(n_cust, 25, replace=False)] = 0  # 25 customers never order
cust_w = cust_w / cust_w.sum()
orders = pd.DataFrame({
    "order_id": range(1, n_orders + 1),
    "customer_id": rng.choice(customers["customer_id"], n_orders, p=cust_w),
    "order_date": (pd.to_datetime("2024-01-01")
                   + pd.to_timedelta(order_days, "D")).strftime("%Y-%m-%d"),
    "ship_mode": rng.choice(["Standard", "Express", "Same Day"], n_orders, p=[0.6, 0.3, 0.1]),
    "status": rng.choice(["Delivered", "Cancelled", "Returned"], n_orders, p=[0.90, 0.05, 0.05]),
})

# ---------- order items ----------
item_rows = []
for oid in orders["order_id"]:
    for pid in rng.choice(products["product_id"], rng.integers(1, 5), replace=False):
        item_rows.append((oid, int(pid), int(rng.integers(1, 6)),
                          float(rng.choice([0.0, 0.0, 0.05, 0.1, 0.2, 0.3]))))
items = pd.DataFrame(item_rows, columns=["order_id", "product_id", "quantity", "discount"])
items.insert(0, "item_id", range(1, len(items) + 1))

# ---------- write the database ----------
conn = sqlite3.connect("shop.db")
conn.executescript("DROP TABLE IF EXISTS order_items; DROP TABLE IF EXISTS orders; "
                   "DROP TABLE IF EXISTS products; DROP TABLE IF EXISTS customers;")
conn.executescript(SCHEMA)
for name, frame in [("customers", customers), ("products", products),
                    ("orders", orders), ("order_items", items)]:
    frame.to_sql(name, conn, if_exists="append", index=False)
conn.commit()
conn.close()
print("Saved shop.db:", len(customers), "customers,", len(products), "products,",
      len(orders), "orders,", len(items), "order items")
