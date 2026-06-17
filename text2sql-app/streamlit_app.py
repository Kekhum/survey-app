from snowflake.snowpark.context import get_active_session
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

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

BLUE       = "#29b5e8"
DARK_BLUE  = "#11567f"
COLORS     = px.colors.qualitative.Bold
TMPL       = "plotly_dark"

session = get_active_session()


@st.cache_data(ttl=30, show_spinner="Loading responses...")
def load_data() -> pd.DataFrame:
    return session.sql("""
        SELECT role, experience_years, fav_cloud, fav_language,
               coffees_per_day, uses_ai_daily, submitted_at
        FROM DEMO.PUBLIC.AUDIENCE_SURVEY
        ORDER BY submitted_at
    """).to_pandas()


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
n        = len(df)
ai_pct   = round(df["USES_AI_DAILY"].mean() * 100)
avg_exp  = round(df["EXPERIENCE_YEARS"].mean(), 1)
avg_cof  = round(df["COFFEES_PER_DAY"].mean(), 1)
top_lang = df["FAV_LANGUAGE"].value_counts().idxmax()

kpis = [
    (n,              "Responses"),
    (f"{avg_exp} yrs", "Avg Experience"),
    (f"{ai_pct}%",    "Use AI Daily"),
    (f"{avg_cof}",    "Avg Coffees / Day"),
]
for col, (val, label) in zip(st.columns(4), kpis):
    with col:
        st.markdown(f"""
        <div class="kpi-card">
            <p class="kpi-value">{val}</p>
            <p class="kpi-label">{label}</p>
        </div>""", unsafe_allow_html=True)

st.write("")

# Tabs
tab1, tab2, tab3 = st.tabs(["Who's in the room?", "Habits & Trends", "Raw data"])

# ---- TAB 1 ----------------------------------------------------------------
with tab1:
    c1, c2, c3 = st.columns(3)

    with c1:
        rc = df["ROLE"].value_counts().reset_index()
        rc.columns = ["Role", "Count"]
        fig = px.pie(rc, values="Count", names="Role",
                     title="Role distribution",
                     hole=0.55, color_discrete_sequence=COLORS, template=TMPL)
        fig.update_traces(textposition="outside", textinfo="percent+label")
        fig.update_layout(showlegend=False, margin=dict(t=50, b=10, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        cloud = df["FAV_CLOUD"].value_counts().reset_index()
        cloud.columns = ["Cloud", "Count"]
        fig = px.bar(cloud.sort_values("Count"), x="Count", y="Cloud",
                     orientation="h", title="Favorite cloud platform",
                     color="Count", color_continuous_scale=[DARK_BLUE, BLUE],
                     template=TMPL, text="Count")
        fig.update_traces(textposition="outside")
        fig.update_layout(coloraxis_showscale=False,
                          margin=dict(t=50, b=10, l=10, r=50),
                          xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    with c3:
        lang = df["FAV_LANGUAGE"].value_counts().reset_index()
        lang.columns = ["Language", "Count"]
        fig = px.bar(lang.sort_values("Count"), x="Count", y="Language",
                     orientation="h", title="Favorite language",
                     color="Count", color_continuous_scale=[DARK_BLUE, BLUE],
                     template=TMPL, text="Count")
        fig.update_traces(textposition="outside")
        fig.update_layout(coloraxis_showscale=False,
                          margin=dict(t=50, b=10, l=10, r=50),
                          xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    # Timeline (meaningful only when there are multiple timestamps)
    ts = pd.to_datetime(df["SUBMITTED_AT"])
    if ts.nunique() > 2:
        st.write("")
        tl = (ts.dt.floor("min")
                .value_counts()
                .sort_index()
                .cumsum()
                .reset_index())
        tl.columns = ["Time", "Cumulative responses"]
        fig = px.area(tl, x="Time", y="Cumulative responses",
                      title="Responses over time",
                      color_discrete_sequence=[BLUE], template=TMPL)
        fig.update_traces(fill="tozeroy", line_width=2.5)
        fig.update_layout(margin=dict(t=50, b=10, l=10, r=10),
                          xaxis_title="", yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

# ---- TAB 2 ----------------------------------------------------------------
with tab2:
    c1, c2 = st.columns(2)

    with c1:
        fig = px.histogram(df, x="EXPERIENCE_YEARS",
                           title="Experience distribution",
                           nbins=min(20, df["EXPERIENCE_YEARS"].nunique() + 1),
                           color_discrete_sequence=[BLUE], template=TMPL)
        fig.update_layout(bargap=0.08, margin=dict(t=50, b=10, l=10, r=10),
                          xaxis_title="Years", yaxis_title="People")
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        fig = px.box(df, x="ROLE", y="COFFEES_PER_DAY",
                     title="Coffee / day by role",
                     color="ROLE", color_discrete_sequence=COLORS,
                     template=TMPL, points="all")
        fig.update_layout(showlegend=False,
                          margin=dict(t=50, b=10, l=10, r=10),
                          xaxis_title="", yaxis_title="Coffees")
        st.plotly_chart(fig, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=ai_pct,
            title={"text": "AI Daily Adoption", "font": {"color": "white", "size": 16}},
            gauge={
                "axis": {"range": [0, 100], "ticksuffix": "%", "tickcolor": "white"},
                "bar": {"color": BLUE, "thickness": 0.28},
                "bgcolor": "rgba(0,0,0,0)",
                "steps": [
                    {"range": [0, 50],  "color": "#0a1628"},
                    {"range": [50, 100], "color": "#0d2137"},
                ],
                "threshold": {
                    "line": {"color": "white", "width": 2},
                    "thickness": 0.7,
                    "value": 50,
                },
            },
            number={"suffix": "%", "font": {"color": BLUE, "size": 52}},
        ))
        fig.update_layout(template=TMPL, height=320,
                          margin=dict(t=70, b=20, l=40, r=40))
        st.plotly_chart(fig, use_container_width=True)

    with c4:
        avg_r = (df.groupby("ROLE")[["EXPERIENCE_YEARS", "COFFEES_PER_DAY"]]
                   .mean().round(1).reset_index())
        fig = px.scatter(avg_r,
                         x="EXPERIENCE_YEARS", y="COFFEES_PER_DAY",
                         text="ROLE",
                         size=[40] * len(avg_r),
                         title="Experience vs coffee (by role)",
                         color="ROLE", color_discrete_sequence=COLORS,
                         template=TMPL)
        fig.update_traces(textposition="top center", marker_opacity=0.85)
        fig.update_layout(showlegend=False,
                          margin=dict(t=50, b=10, l=10, r=10),
                          xaxis_title="Avg experience (yrs)",
                          yaxis_title="Avg coffees / day")
        st.plotly_chart(fig, use_container_width=True)

# ---- TAB 3 ----------------------------------------------------------------
with tab3:
    st.caption(f"{n} responses - auto-refreshes every 30 seconds")
    st.dataframe(df, use_container_width=True, hide_index=True)
