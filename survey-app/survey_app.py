import streamlit as st
import snowflake.connector

# Wymagane dla nazwanych parametrow %(name)s
snowflake.connector.paramstyle = "pyformat"

st.set_page_config(page_title="Audience Survey", page_icon=":snowflake:")
st.title("Audience Survey")
st.caption("Fill in the survey and see your data queried live!")


def _connect():
    return snowflake.connector.connect(**st.secrets["snowflake"])


def fetch_count() -> int | None:
    conn = None
    try:
        conn = _connect()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM DEMO.PUBLIC.AUDIENCE_SURVEY")
        return cur.fetchone()[0]
    except Exception as exc:
        st.warning(f"Could not fetch response count: {exc}")
        return None
    finally:
        if conn:
            conn.close()


# Licznik odpowiedzi z przyciskiem odswiezania
col_metric, col_btn = st.columns([5, 2])
with col_metric:
    count = fetch_count()
    if count is not None:
        st.metric(label="Responses so far", value=count)
with col_btn:
    st.write("")
    st.write("")
    st.button("Refresh")  # klikniecie rerenderuje app i odpytuje COUNT ponownie

st.divider()

# Formularz ankiety
with st.form("survey"):
    st.subheader("Your response")

    role = st.selectbox(
        "Your role",
        ["Data Engineer", "Data Scientist", "Analyst", "Dev", "Manager", "Other"],
    )
    experience_years = st.slider(
        "Years of experience in IT", min_value=0, max_value=30, value=3
    )
    fav_cloud = st.selectbox(
        "Favorite cloud platform",
        ["Azure", "AWS", "GCP", "Snowflake", "None"],
    )
    fav_language = st.selectbox(
        "Favorite programming language",
        ["Python", "SQL", "Scala", "Java", "JavaScript", "Rust", "Other"],
    )
    coffees_per_day = st.slider(
        "Coffees per day?", min_value=0, max_value=10, value=2
    )
    uses_ai_daily = st.checkbox("I use AI daily at work")

    submitted = st.form_submit_button("Submit", type="primary")

if submitted:
    conn = None
    try:
        conn = _connect()
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO DEMO.PUBLIC.AUDIENCE_SURVEY
                (role, experience_years, fav_cloud, fav_language, coffees_per_day, uses_ai_daily)
            VALUES
                (%(role)s, %(experience_years)s, %(fav_cloud)s, %(fav_language)s,
                 %(coffees_per_day)s, %(uses_ai_daily)s)
            """,
            {
                "role": role,
                "experience_years": experience_years,
                "fav_cloud": fav_cloud,
                "fav_language": fav_language,
                "coffees_per_day": coffees_per_day,
                "uses_ai_daily": uses_ai_daily,
            },
        )
        conn.commit()
        st.success("Thank you! Your response has been saved.")
        st.balloons()
    except Exception as exc:
        st.error(f"Error saving response: {exc}")
    finally:
        if conn:
            conn.close()
