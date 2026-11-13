from llm import answer, demo_writer, extract_sql

print(repr(extract_sql("```sql\nSELECT 1\n```")))
out = answer("What is our worst-selling region by revenue?", writer=demo_writer)
print(out["source"], "| attempts:", out["attempts"])
print(out["sql"][:80], "...")
print(out["data"])
out = answer("Which product is cheapest?", writer=demo_writer)
print("Error:", out["error"])
