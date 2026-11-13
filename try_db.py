from db import get_schema, run_query

print(get_schema()[:330], "...\n")
print(run_query("SELECT COUNT(*) AS customers FROM customers"), "\n")
for bad in ["DROP TABLE orders", "SELECT 1; DELETE FROM orders",
            "UPDATE orders SET status = 'x'"]:
    try:
        run_query(bad)
    except ValueError as e:
        print("BLOCKED:", bad, "->", e)
