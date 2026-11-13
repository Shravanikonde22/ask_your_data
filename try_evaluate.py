"""Tests the test-harness itself with a FAKE AI, so no API key is needed."""
from evaluate import evaluate, summarize
from llm import answer
from test_questions import QUESTIONS

GOLD = {q: sql for _, q, sql in QUESTIONS}


def perfect(question, schema, prev=None, err=None):
    return GOLD[question]


def flawed(question, schema, prev=None, err=None):
    if question.startswith("What is the total revenue"):    # forgets the Delivered filter
        return GOLD[question].replace("o.status = 'Delivered'", "1 = 1")
    if question.startswith("How many orders were cancelled"):  # wrong value
        return "SELECT COUNT(*) FROM orders WHERE status = 'Returned'"
    if question.startswith("Which city has the most"):      # extra column
        return "SELECT city, COUNT(*) FROM customers GROUP BY city ORDER BY 2 DESC LIMIT 1"
    if question.startswith("How many customers do we have"):  # typo, fixed on 2nd try
        return "SELEC COUNT(*) FROM customers" if err is None else GOLD[question]
    if question.startswith("Which product has sold"):       # invalid SQL every time
        return "SELECT nonexistent FROM nowhere"
    return GOLD[question]


for name, fake in [("Perfect fake AI", perfect), ("Flawed fake AI", flawed)]:
    print(name)
    summarize(evaluate(lambda q: answer(q, writer=fake)))
    print()
