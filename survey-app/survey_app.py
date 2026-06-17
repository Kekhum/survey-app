import streamlit as st
import snowflake.connector

# Wymagane dla nazwanych parametrow %(name)s
snowflake.connector.paramstyle = "pyformat"

st.set_page_config(page_title="Ankieta Demo", page_icon=":snowflake:")
st.title("Ankieta publicznosci")
st.caption("Wypelnij ankiete i sprawdz, co mowia Twoje dane na zywo!")


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
        st.warning(f"Nie mozna pobrac licznika: {exc}")
        return None
    finally:
        if conn:
            conn.close()


# Licznik odpowiedzi z przyciskiem odswiezania
col_metric, col_btn = st.columns([5, 2])
with col_metric:
    count = fetch_count()
    if count is not None:
        st.metric(label="Odpowiedzi juz w bazie", value=count)
with col_btn:
    st.write("")
    st.write("")
    st.button("Odswiez licznik")  # klikniecie rerenderuje app i odpytuje COUNT ponownie

st.divider()

# Formularz ankiety
with st.form("survey"):
    st.subheader("Twoja odpowiedz")

    role = st.selectbox(
        "Twoja rola",
        ["Data Engineer", "Data Scientist", "Analyst", "Dev", "Manager", "Inne"],
    )
    experience_years = st.slider(
        "Lata doswiadczenia w IT", min_value=0, max_value=30, value=3
    )
    fav_cloud = st.selectbox(
        "Ulubiona platforma chmurowa",
        ["Azure", "AWS", "GCP", "Snowflake", "Zadna"],
    )
    fav_language = st.selectbox(
        "Ulubiony jezyk programowania",
        ["Python", "SQL", "Scala", "Java", "JavaScript", "Rust", "Inne"],
    )
    coffees_per_day = st.slider(
        "Ile kaw dziennie wypiasz?", min_value=0, max_value=10, value=2
    )
    uses_ai_daily = st.checkbox("Uzywam AI codziennie w pracy")

    submitted = st.form_submit_button("Wyslij odpowiedz", type="primary")

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
        st.success("Dzieki! Twoja odpowiedz zostala zapisana.")
        st.balloons()
    except Exception as exc:
        st.error(f"Blad zapisu do bazy danych: {exc}")
    finally:
        if conn:
            conn.close()
