Ask Your Data
=============

Ask questions about a database in plain English and get back the SQL, a table and a chart. Claude writes the query, and a safety layer makes sure it can only ever read data.

Live demo: https://askyourdata-iaioh7rzjwkzrwqq2nrfzy.streamlit.app/

How it works
------------

1. You type a question, for example "What is our worst-selling region by revenue?"
2. The app sends Claude the table schema, 3 example rows per table, your business definitions and the question.
3. Claude returns one SQL query.
4. The query is checked, then run on a read-only connection.
5. If it fails, the error goes back to Claude for one retry.
6. The app shows the SQL, an automatically chosen chart and the result table.

Without an API key the app falls back to a small demo mode that knows six questions. The sidebar tells you which engine answered.

Safety by design
----------------

SQL written by an AI is untrusted input, so there are three layers:

| Layer | What it does |
|-------|--------------|
| Validator | Allows only a single SELECT or WITH query and rejects words like DROP, DELETE and UPDATE |
| Read-only connection | The database is opened with mode=ro and query_only, so writing is impossible even if the validator had a bug |
| Limits | Queries stop after 5 seconds and return at most 500 rows |

Only the schema and 3 sample rows per table are sent to Claude, never the full data. The validator is deliberately crude: it also blocks harmless text like 'Update' inside quotes. It fails safe.

Automatic chart choice
----------------------

| Result looks like | Shown as |
|-------------------|----------|
| One row, one column | Big number |
| Label column plus number columns | Bar chart |
| Date or month column plus number columns | Line chart |
| Anything else, or more than 40 rows | Table only |

The rules are simple and predictable on purpose, which makes them easy to test.

The practice database
---------------------

make_sample_db.py builds a small online shop in SQLite with four connected tables: customers, products, orders and order_items (300 customers, 36 products, 3,000 orders). Some things are planted on purpose to make the questions realistic:

- Revenue is not stored anywhere. It is quantity * unit_price * (1 - discount).
- Only orders with status Delivered count as sales.
- The Central region is much smaller than the others.
- Some customers never ordered, and some ordered more than 10 times.
- Orders cover 2024 and 2025, and 2025 is bigger.

Accuracy test
-------------

The project includes 30 test questions (10 easy, 12 medium, 8 hard) with correct SQL written by hand. A question counts as correct when the AI's SQL returns the same result as the gold SQL (execution accuracy). Column names and row order are ignored, and decimals are rounded to 2 places. Run it with:

    python evaluate.py

This prints accuracy overall and by level and saves every generated query and error to eval_results.csv. You can also run it from the Accuracy test tab in the app.

Checks on the test harness itself (using fake AIs, no API key needed):

| Test | Result |
|------|--------|
| Perfect fake AI that returns the gold SQL | 100% (30/30) |
| Flawed fake AI with 4 planted mistakes | 87% (26/30), the retry fixed the planted typo |
| Demo mode, no API key | 13% (4/30), it only knows six questions |
| Dangerous SQL (DROP, DELETE, UPDATE, two statements) | All blocked, data unchanged |

Claude on the 30 questions:

| Setup | Accuracy |
|-------|----------|
| Bare prompt | |
| Plus business notes | |
| Plus retry | |
| Plus worked examples | |

Real dataset:

| Database | Tables | Easy | Medium | Hard | Overall |
|----------|--------|------|--------|------|---------|
| Practice shop | 4 | | | | |
| Olist or Superstore | | | | | |

Tech stack
----------

Python, SQLite, pandas, Streamlit

Project structure
-----------------

    make_sample_db.py     builds the practice shop database
    db.py                 the only file that touches the database: validator, read-only connection, limits
    llm.py                question to SQL, business notes, retry, demo mode
    charts.py             picks metric, bar, line or table
    test_questions.py     30 questions with gold SQL
    evaluate.py           measures execution accuracy
    app.py                Streamlit web app
    load_csv_folder.py    turns a folder of CSV files into one SQLite database

Run locally
-----------

    pip install -r requirements.txt
    python make_sample_db.py
    streamlit run app.py
    

Using your own data
-------------------

    python load_csv_folder.py my_csv_folder mydata.db

Then change DB_PATH in db.py, rewrite NOTES in llm.py (what counts as revenue, which status counts as a sale, how dates are stored), and write your own test questions.

Limitations
-----------

- Ambiguous words like "best" get a guessed meaning.
- 30 questions is a small test set, and scores vary slightly between runs.
- Only tested on SQLite.
- The validator is crude by design.
- A very large schema would not fit in one prompt. The fix would be to retrieve only the relevant tables.
- Each question and the schema with sample rows go to Claude, so only use practice or public data when deployed.

Author
------

Shravani Konde
