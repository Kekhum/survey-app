from snowflake.snowpark.context import get_active_session
import streamlit as st
import pandas as pd
import altair as alt

st.set_page_config(page_title="Audience Insights", layout="wide")

st.markdown("""
<style>
.kpi-card {
    background: linear-gradient(135deg, #0a1628 0%, #0d2137 100%);
    border: 1px solid #29b5e8;
    border-radius: 14px;
    padding: 28px 16px;
    text-align: center;
}
.kpi-value {
    font-size: 2.6rem;
    font-weight: 800;
    color: #29b5e8;
    margin: 0;
    line-height: 1;
}
.kpi-label {
    font-size: 0.72rem;
    color: #7a9bb5;
    text-transform: uppercase;
    letter-spacing: 1.8px;
    margin-top: 10px;
    margin-bottom: 0;
}
</style>
""", unsafe_allow_html=True)

BLUE  = "#29b5e8"
session = get_active_session()


def dark(chart: alt.Chart) -> alt.Chart:
    return (chart
        .configure_view(fill="#0a1628", strokeWidth=0)
        .configure_axis(
            labelColor="#8aacbf", titleColor="#8aacbf",
            gridColor="#152234", domainColor="#152234",
        )
        .configure_legend(labelColor="#8aacbf", titleColor="#8aacbf")
        .configure_title(color="white", fontSize=14, anchor="start")
    )


@st.cache_data(ttl=30, show_spinner="Loading responses...")
def load_data() -> pd.DataFrame:
    df = session.sql("""
        SELECT role, experience_years, fav_cloud, fav_language,
               coffees_per_day, uses_ai_daily, submitted_at
        FROM DEMO.PUBLIC.AUDIENCE_SURVEY
        ORDER BY submitted_at
    """).to_pandas()
    df["USES_AI_DAILY"] = df["USES_AI_DAILY"].astype(bool)
    return df


# Header
col_h, col_btn = st.columns([5, 1])
with col_h:
    st.title("Audience Insights")
with col_btn:
    st.write("")
    st.write("")
    if st.button("Refresh", use_container_width=True):
        st.cache_data.clear()
        st.rerun()

df = load_data()

if df.empty:
    st.info("No responses yet. Share the QR code!")
    st.stop()

# KPIs
n       = len(df)
ai_pct  = round(df["USES_AI_DAILY"].mean() * 100)
avg_exp = round(df["EXPERIENCE_YEARS"].mean(), 1)
avg_cof = round(df["COFFEES_PER_DAY"].mean(), 1)

for col, (val, label) in zip(st.columns(4), [
    (n,                "Responses"),
    (f"{avg_exp} yrs", "Avg Experience"),
    (f"{ai_pct}%",     "Use AI Daily"),
    (f"{avg_cof}",     "Avg Coffees / Day"),
]):
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <p class="kpi-value">{val}</p>
            <p class="kpi-label">{label}</p>
        </div>""", unsafe_allow_html=True)

st.write("")

tab1, tab2, tab3 = st.tabs(["Who's in the room?", "Habits & Trends", "Raw data"])

# ---- TAB 1 ----------------------------------------------------------------
with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        rc = df["ROLE"].value_counts().reset_index()
        rc.columns = ["Role", "Count"]
        chart = (
            alt.Chart(rc, title="Role distribution")
            .mark_arc(innerRadius=65, outerRadius=120)
            .encode(
                theta=alt.Theta("Count:Q"),
                color=alt.Color("Role:N", scale=alt.Scale(scheme="tableau10"),
                                legend=alt.Legend(orient="bottom")),
                tooltip=["Role:N", "Count:Q"],
            )
        )
        st.altair_chart(dark(chart), use_container_width=True)

    with c2:
        cloud = df["FAV_CLOUD"].value_counts().reset_index()
        cloud.columns = ["Cloud", "Count"]
        chart = (
            alt.Chart(cloud, title="Favorite cloud platform")
            .mark_bar()
            .encode(
                x=alt.X("Count:Q", axis=alt.Axis(title="")),
                y=alt.Y("Cloud:N", sort="-x", axis=alt.Axis(title="")),
                color=alt.Color("Count:Q",
                                scale=alt.Scale(range=["#11567f", BLUE]),
                                legend=None),
                tooltip=["Cloud:N", "Count:Q"],
                text=alt.Text("Count:Q"),
            )
        )
        st.altair_chart(dark(chart + chart.mark_text(align="left", dx=4, color="white")),
                        use_container_width=True)

    with c3:
        lang = df["FAV_LANGUAGE"].value_counts().reset_index()
        lang.columns = ["Language", "Count"]
        chart = (
            alt.Chart(lang, title="Favorite language")
            .mark_bar()
            .encode(
                x=alt.X("Count:Q", axis=alt.Axis(title="")),
                y=alt.Y("Language:N", sort="-x", axis=alt.Axis(title="")),
                color=alt.Color("Count:Q",
                                scale=alt.Scale(range=["#11567f", BLUE]),
                                legend=None),
                tooltip=["Language:N", "Count:Q"],
            )
        )
        text = chart.mark_text(align="left", dx=4, color="white").encode(
            text=alt.Text("Count:Q")
        )
        st.altair_chart(dark(chart + text), use_container_width=True)

    # Timeline
    ts = pd.to_datetime(df["SUBMITTED_AT"])
    if ts.nunique() > 2:
        st.write("")
        tl = (ts.dt.floor("min")
                .value_counts().sort_index().cumsum()
                .reset_index())
        tl.columns = ["Time", "Cumulative"]
        chart = (
            alt.Chart(tl, title="Responses over time")
            .mark_area(color=BLUE, opacity=0.5,
                       line={"color": BLUE, "width": 2})
            .encode(
                x=alt.X("Time:T", axis=alt.Axis(title="")),
                y=alt.Y("Cumulative:Q", axis=alt.Axis(title="Responses")),
                tooltip=["Time:T", "Cumulative:Q"],
            )
        )
        st.altair_chart(dark(chart), use_container_width=True)

# ---- TAB 2 ----------------------------------------------------------------
with tab2:
    c1, c2 = st.columns(2)

    with c1:
        chart = (
            alt.Chart(df, title="Experience distribution")
            .mark_bar(color=BLUE, opacity=0.85)
            .encode(
                x=alt.X("EXPERIENCE_YEARS:Q", bin=alt.Bin(maxbins=20),
                         axis=alt.Axis(title="Years")),
                y=alt.Y("count():Q", axis=alt.Axis(title="People")),
                tooltip=["count():Q"],
            )
        )
        st.altair_chart(dark(chart), use_container_width=True)

    with c2:
        chart = (
            alt.Chart(df, title="Coffee / day by role")
            .mark_boxplot(extent="min-max", size=40)
            .encode(
                x=alt.X("ROLE:N", axis=alt.Axis(title="", labelAngle=-20)),
                y=alt.Y("COFFEES_PER_DAY:Q", axis=alt.Axis(title="Coffees")),
                color=alt.Color("ROLE:N", scale=alt.Scale(scheme="tableau10"),
                                legend=None),
                tooltip=["ROLE:N", "COFFEES_PER_DAY:Q"],
            )
        )
        st.altair_chart(dark(chart), use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        st.write("")
        st.markdown(f"""
        <div class="kpi-card" style="padding: 40px 16px;">
            <p class="kpi-value" style="font-size:4rem">{ai_pct}%</p>
            <p class="kpi-label">use AI daily at work</p>
        </div>""", unsafe_allow_html=True)
        st.write("")
        ai_comp = (df.groupby("USES_AI_DAILY")["EXPERIENCE_YEARS"]
                     .mean().round(1).reset_index())
        ai_comp["Group"] = ai_comp["USES_AI_DAILY"].map(
            {True: "Daily AI user", False: "Not daily"}
        )
        chart = (
            alt.Chart(ai_comp, title="Avg experience: AI users vs others")
            .mark_bar()
            .encode(
                x=alt.X("Group:N", axis=alt.Axis(title="")),
                y=alt.Y("EXPERIENCE_YEARS:Q", axis=alt.Axis(title="Avg years")),
                color=alt.Color("Group:N",
                                scale=alt.Scale(
                                    domain=["Daily AI user", "Not daily"],
                                    range=[BLUE, "#11567f"]
                                ),
                                legend=None),
                tooltip=["Group:N", "EXPERIENCE_YEARS:Q"],
            )
        )
        st.altair_chart(dark(chart), use_container_width=True)

    with c4:
        avg_r = (df.groupby("ROLE")[["EXPERIENCE_YEARS", "COFFEES_PER_DAY"]]
                   .mean().round(1).reset_index())
        base = (
            alt.Chart(avg_r, title="Experience vs coffee (avg by role)")
            .encode(
                x=alt.X("EXPERIENCE_YEARS:Q", axis=alt.Axis(title="Avg experience (yrs)")),
                y=alt.Y("COFFEES_PER_DAY:Q", axis=alt.Axis(title="Avg coffees / day")),
                color=alt.Color("ROLE:N", scale=alt.Scale(scheme="tableau10"),
                                legend=None),
                tooltip=["ROLE:N", "EXPERIENCE_YEARS:Q", "COFFEES_PER_DAY:Q"],
            )
        )
        points = base.mark_point(size=250, filled=True, opacity=0.9)
        labels = base.mark_text(align="left", dx=10, fontSize=12,
                                color="#cde8f5").encode(text="ROLE:N")
        st.altair_chart(dark(points + labels), use_container_width=True)

# ---- TAB 3 ----------------------------------------------------------------
with tab3:
    st.caption(f"{n} responses - auto-refreshes every 30 s")
    st.dataframe(df, use_container_width=True, hide_index=True)
