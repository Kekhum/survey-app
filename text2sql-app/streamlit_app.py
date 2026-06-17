from snowflake.snowpark.context import get_active_session
import streamlit as st
import pandas as pd

MODEL = "llama3.1-70b"
MODEL_OPTIONS = ["llama3.1-70b", "mistral-large2", "claude-3-5-sonnet"]

st.set_page_config(page_title="Talk to your data", layout="wide")
st.title("Talk to your data")

session = get_active_session()

# Konfiguracja: baza, schemat, model
col_db, col_schema, col_model = st.columns([2, 2, 3])
with col_db:
    database = st.text_input("Database", value="DEMO")
with col_schema:
    schema_name = st.text_input("Schema", value="PUBLIC")
with col_model:
    model = st.selectbox("Model LLM", MODEL_OPTIONS, index=MODEL_OPTIONS.index(MODEL))

st.divider()


@st.cache_data(show_spinner="Fetching database schema...")
def get_schema_context(db: str, sch: str) -> str:
    rows = session.sql(
        f"""
        SELECT table_name, column_name, data_type
        FROM {db}.INFORMATION_SCHEMA.COLUMNS
        WHERE table_schema = UPPER('{sch}')
        ORDER BY table_name, ordinal_position
        """
    ).collect()
    tables: dict = {}
    for row in rows:
        tbl = row["TABLE_NAME"]
        if tbl not in tables:
            tables[tbl] = []
        tables[tbl].append(f"{row['COLUMN_NAME']} {row['DATA_TYPE']}")
    return "\n".join(f"{t}({', '.join(cols)})" for t, cols in tables.items())


schema_context = get_schema_context(database, schema_name)

if not schema_context:
    st.warning("No tables found in the given schema. Check the Database and Schema values.")
    st.stop()

with st.expander("Schema passed to the model"):
    st.code(schema_context)

question = st.text_area(
    "Question in natural language",
    placeholder="e.g. How many people prefer Python?",
    height=80,
)


def extract_sql(text: str) -> str:
    text = text.strip()
    if "```sql" in text:
        text = text.split("```sql")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    return text.strip().rstrip(";").strip()


if st.button("Generate SQL", type="primary", disabled=not question.strip()):
    prompt = (
        "You are a Snowflake SQL expert. "
        "Based on the provided database schema, generate a SQL query "
        "that answers the user's question. "
        "Return ONLY the raw SQL code with no markdown, no explanations, "
        "and no trailing semicolon.\n\n"
        f"Schema:\n{schema_context}\n\n"
        f"Question: {question}\n\n"
        "SQL:"
    )
    safe_prompt = prompt.replace("'", "''")

    with st.spinner("Generating SQL with Cortex..."):
        try:
            result = session.sql(
                f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{safe_prompt}')"
            ).collect()[0][0]
            st.session_state["generated_sql"] = extract_sql(result)
            st.session_state["query_result"] = None
        except Exception as exc:
            st.error(f"Error generating SQL: {exc}")

if st.session_state.get("generated_sql"):
    st.subheader("Generated SQL")
    st.code(st.session_state["generated_sql"], language="sql")

    if st.button("Run query"):
        with st.spinner("Running query..."):
            try:
                df = session.sql(st.session_state["generated_sql"]).to_pandas()
                st.session_state["query_result"] = df
            except Exception as exc:
                st.error(f"Error running query: {exc}")
                st.session_state["query_result"] = None

if st.session_state.get("query_result") is not None:
    df: pd.DataFrame = st.session_state["query_result"]
    st.subheader(f"Results ({len(df)} rows)")
    st.dataframe(df, use_container_width=True)

    # Auto chart for categorical + numeric columns
    if len(df) <= 50:
        cat_cols = [c for c in df.columns if df[c].dtype == object]
        num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        if cat_cols and num_cols:
            st.bar_chart(
                df[[cat_cols[0], num_cols[0]]].set_index(cat_cols[0]),
                use_container_width=True,
            )
