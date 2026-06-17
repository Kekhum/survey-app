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


@st.cache_data(show_spinner="Pobieranie schematu bazy danych...")
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
    st.warning("Nie znaleziono tabel w podanym schemacie. Sprawdz wartosci Database i Schema.")
    st.stop()

with st.expander("Schemat przekazany do modelu"):
    st.code(schema_context)

question = st.text_area(
    "Pytanie w jezyku naturalnym",
    placeholder="np. Ile osob preferuje Pythona?",
    height=80,
)


def extract_sql(text: str) -> str:
    text = text.strip()
    if "```sql" in text:
        text = text.split("```sql")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    return text.strip().rstrip(";").strip()


if st.button("Generuj SQL", type="primary", disabled=not question.strip()):
    prompt = (
        "Jestes ekspertem SQL dla Snowflake. "
        "Na podstawie podanego schematu bazy danych wygeneruj zapytanie SQL "
        "odpowiadajace na pytanie uzytkownika. "
        "Odpowiedz WYLACZNIE samym kodem SQL bez znacznikow markdown, "
        "bez dodatkowych komentarzy i bez srednika na koncu.\n\n"
        f"Schemat:\n{schema_context}\n\n"
        f"Pytanie: {question}\n\n"
        "SQL:"
    )
    # Escapowanie apostrofow przed wbudowaniem promptu w SQL
    safe_prompt = prompt.replace("'", "''")

    with st.spinner("Generowanie SQL przez Cortex..."):
        try:
            result = session.sql(
                f"SELECT SNOWFLAKE.CORTEX.COMPLETE('{model}', '{safe_prompt}')"
            ).collect()[0][0]
            st.session_state["generated_sql"] = extract_sql(result)
            st.session_state["query_result"] = None
        except Exception as exc:
            st.error(f"Blad generowania SQL: {exc}")

# Pokazujemy SQL zanim go uruchomimy -- kluczowe dla demo na zywo
if st.session_state.get("generated_sql"):
    st.subheader("Wygenerowany SQL")
    st.code(st.session_state["generated_sql"], language="sql")

    if st.button("Uruchom zapytanie"):
        with st.spinner("Wykonywanie zapytania..."):
            try:
                df = session.sql(st.session_state["generated_sql"]).to_pandas()
                st.session_state["query_result"] = df
            except Exception as exc:
                st.error(f"Blad wykonania zapytania: {exc}")
                st.session_state["query_result"] = None

if st.session_state.get("query_result") is not None:
    df: pd.DataFrame = st.session_state["query_result"]
    st.subheader(f"Wyniki ({len(df)} wierszy)")
    st.dataframe(df, use_container_width=True)

    # Auto wykres dla czytelnych kolumn kategoryczna + numeryczna
    if len(df) <= 50:
        cat_cols = [c for c in df.columns if df[c].dtype == object]
        num_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        if cat_cols and num_cols:
            st.bar_chart(
                df[[cat_cols[0], num_cols[0]]].set_index(cat_cols[0]),
                use_container_width=True,
            )
