from charts import pick_chart
from db import run_query

tests = {
    "one number": "SELECT COUNT(*) FROM orders",
    "by region": "SELECT region, COUNT(*) AS n FROM customers GROUP BY region",
    "by month": "SELECT strftime('%Y-%m', order_date) AS month, COUNT(*) AS n "
                "FROM orders GROUP BY month",
    "two labels": "SELECT region, segment, COUNT(*) AS n FROM customers GROUP BY 1, 2",
}
for name, sql in tests.items():
    print(f"{name:<11} -> {pick_chart(run_query(sql))}")
