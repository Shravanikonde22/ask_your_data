"""app.py - the screen the user sees. Run with: streamlit run app.py"""
import streamlit as st
from charts import pick_chart
from db import get_schema
from evaluate import evaluate
from llm import answer, claude_writer, pick_writer

st.set_page_config(page_title="Ask Your Data", layout="wide")
st.title("Ask Your Data")
st.caption("Ask a question in plain English. Get SQL, a table and a chart.")

engine = "Claude" if pick_writer() is claude_writer else "Demo rules (no API key)"
st.sidebar.write(f"Answer engine: **{engine}**")
with st.sidebar.expander("Database schema"):
    st.code(get_schema(), language="sql")

EXAMPLES = ["What is our worst-selling region by revenue?",
            "What is the total revenue for each product category?",
            "What is the monthly revenue?",
            "How many orders did each region place?"]


def set_question(q):
    st.session_state.question = q


def show_result(res):
    st.caption(f"Written by: {res['source']} | attempts: {res['attempts']}")
    st.code(res["sql"] or "(no SQL)", language="sql")
    if res["error"]:
        st.error(f"Could not answer: {res['error']}")
        return
    data = res["data"]
    kind = pick_chart(data)
    if kind == "metric":
        st.metric(str(data.columns[0]), f"{data.iloc[0, 0]:,.2f}"
                  if isinstance(data.iloc[0, 0], float) else data.iloc[0, 0])
    elif kind == "bar":
        st.bar_chart(data.set_index(data.columns[0]))
    elif kind == "line":
        st.line_chart(data.set_index(data.columns[0]))
    st.dataframe(data, hide_index=True)


tab1, tab2 = st.tabs(["Ask", "Accuracy test"])

with tab1:
    st.write("Try an example:")
    for col, q in zip(st.columns(len(EXAMPLES)), EXAMPLES):
        col.button(q, on_click=set_question, args=(q,))
    question = st.text_input("Your question", key="question")
    if st.button("Ask") and question:
        with st.spinner("Thinking..."):
            st.session_state.result = answer(question)
    if "result" in st.session_state:
        show_result(st.session_state.result)

with tab2:
    st.write("Runs the 30 test questions and checks each answer against the correct SQL.")
    if st.button("Run accuracy test"):
        with st.spinner("Running 30 questions..."):
            st.session_state.eval = evaluate()
    if "eval" in st.session_state:
        res = st.session_state.eval
        st.metric("Accuracy", f"{res['correct'].mean():.0%}")
        st.bar_chart(res.groupby("level")["correct"].mean())
        st.dataframe(res[["level", "question", "correct", "attempts", "error"]], hide_index=True)
