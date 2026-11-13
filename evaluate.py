"""evaluate.py - measures accuracy on the 30 test questions.
A question counts as correct if the AI's SQL returns the same numbers as the gold SQL."""
import pandas as pd
from db import DB_PATH, run_query
from llm import answer
from test_questions import QUESTIONS


def normalize(df):
    """Turn a result table into a sorted list of rounded rows, so order and names do not matter."""
    rows = []
    for row in df.itertuples(index=False):
        rows.append(tuple(round(v, 2) if isinstance(v, float) else v for v in row))
    return sorted(rows, key=str)


def same_result(a, b):
    return normalize(a) == normalize(b)


def evaluate(answer_fn=answer, db_path=DB_PATH):
    records = []
    for level, question, gold_sql in QUESTIONS:
        gold = run_query(gold_sql, db_path)
        out = answer_fn(question)
        ok = out["data"] is not None and same_result(gold, out["data"])
        records.append({"level": level, "question": question, "correct": ok,
                        "attempts": out["attempts"], "error": out["error"], "sql": out["sql"]})
    return pd.DataFrame(records)


def summarize(results):
    print(f"Overall accuracy: {results['correct'].mean():.0%} "
          f"({int(results['correct'].sum())}/{len(results)})")
    print(results.groupby("level")["correct"].mean().map("{:.0%}".format).to_string())


if __name__ == "__main__":
    res = evaluate()
    res.to_csv("eval_results.csv", index=False)
    summarize(res)
