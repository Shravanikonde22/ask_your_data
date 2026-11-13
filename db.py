"""db.py - talks to the database safely. The AI's SQL must pass through here."""
import re
import sqlite3
import time
import pandas as pd

DB_PATH = "shop.db"

# Words that change data or the database. We refuse any SQL that contains them.
FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|replace|attach|detach|pragma|vacuum|reindex)\b",
    re.IGNORECASE)


def connect_readonly(path=DB_PATH):
    """Open the database in read-only mode. Even a bug cannot change your data."""
    conn = sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    conn.execute("PRAGMA query_only = ON")
    return conn


def get_schema(path=DB_PATH, sample_rows=3):
    """Text description of every table: CREATE statement plus a few example rows."""
    conn = connect_readonly(path)
    parts = []
    tables = conn.execute("SELECT name, sql FROM sqlite_master WHERE type='table'").fetchall()
    for name, create_sql in tables:
        sample = pd.read_sql_query(f"SELECT * FROM {name} LIMIT {sample_rows}", conn)
        parts.append(f"{create_sql.strip()}\n-- example rows:\n{sample.to_string(index=False)}")
    conn.close()
    return "\n\n".join(parts)


def check_sql(sql):
    """Allow only ONE read-only SELECT. Returns the cleaned SQL or raises ValueError."""
    sql = sql.strip().rstrip(";").strip()
    if not sql:
        raise ValueError("Empty SQL")
    if ";" in sql:
        raise ValueError("Only one statement is allowed")
    if not re.match(r"^(select|with)\b", sql, re.IGNORECASE):
        raise ValueError("Only SELECT queries are allowed")
    if FORBIDDEN.search(sql):
        raise ValueError("This query contains a forbidden word")
    return sql


def run_query(sql, path=DB_PATH, max_rows=500, timeout=5):
    """Check the SQL, run it, return a DataFrame (at most max_rows rows)."""
    sql = check_sql(sql)
    conn = connect_readonly(path)
    start = time.time()
    # Stop any query that runs longer than `timeout` seconds
    conn.set_progress_handler(lambda: 1 if time.time() - start > timeout else 0, 100000)
    try:
        cur = conn.execute(sql)
        columns = [d[0] for d in cur.description]
        rows = cur.fetchmany(max_rows)
    finally:
        conn.close()
    return pd.DataFrame(rows, columns=columns)
