"""charts.py - looks at a result table and decides how to show it."""
import re
import pandas as pd


def looks_like_time(series, name):
    """True for columns like month, order_date, or values like '2025-03'."""
    if re.search(r"(date|month|year|week|day)", str(name), re.IGNORECASE):
        return True
    return bool(series.astype(str).str.match(r"^\d{4}(-\d{2}){0,2}$").all())


def pick_chart(df):
    """Returns 'metric', 'line', 'bar' or 'table'."""
    if df is None or df.empty:
        return "table"
    if df.shape == (1, 1):
        return "metric"
    if df.shape[1] < 2 or df.shape[0] < 2 or df.shape[0] > 40:
        return "table"
    label, values = df.columns[0], df.columns[1:]
    if not all(pd.api.types.is_numeric_dtype(df[c]) for c in values):
        return "table"
    if looks_like_time(df[label], label):
        return "line"
    if pd.api.types.is_numeric_dtype(df[label]):
        return "table"
    return "bar"
