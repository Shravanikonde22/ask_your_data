"""llm.py - turns a question into SQL. Claude writes it; db.py checks and runs it.
Without an API key, a few built-in demo rules answer a handful of questions."""
import os
from db import DB_PATH, get_schema, run_query

MODEL = "claude-sonnet-5-5"

# Business definitions the AI cannot guess. Always tell it what your words mean.
NOTES = (
    "Revenue = quantity * unit_price * (1 - discount), using order_items joined to products. "
    "Only orders with status 'Delivered' count as sales or revenue unless the question "
    "says otherwise. Dates are text in YYYY-MM-DD format; use strftime() to get a year or month."
)

SYSTEM = (
    "You are an expert SQLite analyst. Write ONE read-only SQLite SELECT query that answers "
    "the question. Use only the tables and columns in the schema. "
    "Return ONLY the SQL: no explanation and no markdown."
)


def extract_sql(text):
    """Claude sometimes wraps SQL in ```sql fences. Remove them."""
    text = text.strip()
    if "```" in text:
        text = text.split("```")[1]
        if text.lower().startswith("sql"):
            text = text[3:]
    return text.strip()


def claude_writer(question, schema, previous_sql=None, error=None):
    import anthropic
    client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY automatically
    prompt = f"Schema:\n{schema}\n\nNotes:\n{NOTES}\n\nQuestion: {question}"
    messages = [{"role": "user", "content": prompt}]
    if error:  # second try: show Claude its own mistake
        messages += [
            {"role": "assistant", "content": previous_sql.strip()},
            {"role": "user", "content": f"That SQL failed with this error: {error}\n"
                                        "Return a corrected query. SQL only."}]
    msg = client.messages.create(model=MODEL, max_tokens=600, system=SYSTEM, messages=messages)
    return extract_sql(msg.content[0].text)


# ---------- Demo mode: a few canned answers, no API key needed ----------
REV = "oi.quantity * p.unit_price * (1 - oi.discount)"
DEMO_RULES = [
    (("worst", "region"),
     f"SELECT c.region FROM order_items oi JOIN orders o ON o.order_id = oi.order_id "
     f"JOIN products p ON p.product_id = oi.product_id "
     f"JOIN customers c ON c.customer_id = o.customer_id "
     f"WHERE o.status = 'Delivered' GROUP BY c.region ORDER BY SUM({REV}) ASC LIMIT 1"),
    (("revenue", "category"),
     f"SELECT p.category, SUM({REV}) AS revenue FROM order_items oi "
     f"JOIN orders o ON o.order_id = oi.order_id JOIN products p ON p.product_id = oi.product_id "
     f"WHERE o.status = 'Delivered' GROUP BY p.category ORDER BY revenue DESC"),
    (("monthly", "revenue"),
     f"SELECT strftime('%Y-%m', o.order_date) AS month, SUM({REV}) AS revenue FROM order_items oi "
     f"JOIN orders o ON o.order_id = oi.order_id JOIN products p ON p.product_id = oi.product_id "
     f"WHERE o.status = 'Delivered' GROUP BY month ORDER BY month"),
    (("how many", "customers"), "SELECT COUNT(*) AS customers FROM customers"),
    (("how many", "orders"), "SELECT COUNT(*) AS orders FROM orders"),
    (("orders", "region"),
     "SELECT c.region, COUNT(*) AS orders FROM orders o JOIN customers c "
     "ON c.customer_id = o.customer_id GROUP BY c.region ORDER BY orders DESC"),
]


def demo_writer(question, schema, previous_sql=None, error=None):
    q = question.lower()
    for words, sql in DEMO_RULES:
        if all(w in q for w in words):
            return sql
    raise ValueError("Demo mode only knows a few questions. Add an API key to ask anything.")


def pick_writer():
    return claude_writer if os.getenv("ANTHROPIC_API_KEY") else demo_writer


def answer(question, db_path=DB_PATH, writer=None):
    """Write SQL, run it. If it fails, show the error to the writer and try once more."""
    writer = writer or pick_writer()
    source = "Claude" if writer is claude_writer else "Demo rules"
    schema = get_schema(db_path)
    sql, error = None, None
    for attempt in (1, 2):
        try:
            new_sql = writer(question, schema, sql, error)
            sql = new_sql
            data = run_query(sql, db_path)
            return {"sql": sql, "data": data, "error": None, "attempts": attempt, "source": source}
        except Exception as e:
            error = str(e)
    return {"sql": sql, "data": None, "error": error, "attempts": 2, "source": source}
