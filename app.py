import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from pathlib import Path

from dora_metrics import compute_dora_metrics, daily_timeseries

st.set_page_config(page_title="DORA Metrics Tracker", page_icon="📈", layout="wide")
st.title("📈 DORA Metrics & Engineering Velocity Tracker")
st.markdown("Deployment Frequency · Lead Time · Change Failure Rate · Time to Restore (MTTR)")

DATA = Path(__file__).parent / "data" / "prs.csv"

TIER_COLOR = {"Elite": "#28a745", "High": "#17a2b8", "Medium": "#ffc107", "Low": "#dc3545"}


def gauge(label: str, value: float, suffix: str, tier: str, max_v: float):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        number={"suffix": suffix},
        title={"text": f"{label}<br><span style='color:{TIER_COLOR[tier]}'>{tier}</span>"},
        gauge={
            "axis": {"range": [0, max_v]},
            "bar": {"color": TIER_COLOR[tier]},
            "steps": [
                {"range": [0, max_v * 0.375], "color": "#f0f0f0"},
                {"range": [max_v * 0.375, max_v], "color": "#e8e8e8"},
            ],
        },
    ))
    fig.update_layout(height=230, margin=dict(t=60, b=10))
    return fig


@st.cache_data
def load():
    try:
        df = pd.read_csv(DATA, parse_dates=["created_at", "merged_at", "deployed_at"])
    except FileNotFoundError:
        st.error("Data not found. Run `python generate_mock_data.py` first.")
        st.stop()
    return df


df = load()

st.sidebar.header("Filters")
teams = st.sidebar.multiselect("Teams", sorted(df["team"].unique()), default=sorted(df["team"].unique()))
dmin, dmax = df["deployed_at"].min().date(), df["deployed_at"].max().date()
drange = st.sidebar.date_input("Date range", [dmin, dmax], min_value=dmin, max_value=dmax)

mask = df["team"].isin(teams)
if len(drange) == 2:
    mask &= (df["deployed_at"].dt.date >= drange[0]) & (df["deployed_at"].dt.date <= drange[1])
fdf = df[mask]

m = compute_dora_metrics(fdf)
st.subheader(f"Overall rating: :{ 'green' if m['overall']=='Elite' else 'red' }[{m['overall']}]  ·  {m['total_deploys']} deployments")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.plotly_chart(gauge("Deploy Freq /day", m["deploys_per_day"], "", m["ratings"].get("frequency", "Low"), max(2, m["deploys_per_day"] * 1.5)), use_container_width=True)
with c2:
    st.plotly_chart(gauge("Lead Time median", m["lead_time_median_hours"], "h", m["ratings"].get("lead_time", "Low"), max(720, m["lead_time_median_hours"] * 1.2)), use_container_width=True)
with c3:
    st.plotly_chart(gauge("Change Fail Rate", m["change_fail_rate_pct"], "%", m["ratings"].get("failure_rate", "Low"), 100), use_container_width=True)
with c4:
    st.plotly_chart(gauge("MTTR", m["mttr_hours"], "h", m["ratings"].get("mttr", "Low"), max(168, m["mttr_hours"] * 1.2)), use_container_width=True)

st.divider()
daily = daily_timeseries(fdf)

colL, colR = st.columns(2)
with colL:
    st.subheader("Velocity vs Failure (dual axis + 7d avg)")
    if not daily.empty:
        fig = go.Figure()
        fig.add_bar(x=daily["deployed_at"], y=daily["deploys"], name="Deploys/day", opacity=0.5)
        fig.add_scatter(x=daily["deployed_at"], y=daily["deploys_7d"], name="Deploys 7d avg", mode="lines")
        fig.add_scatter(x=daily["deployed_at"], y=daily["fail_rate_7d"], name="Fail % 7d avg", mode="lines", yaxis="y2",
                        line=dict(color="#dc3545", dash="dash"))
        fig.update_layout(yaxis=dict(title="Deploys"), yaxis2=dict(title="Fail %", overlaying="y", side="right", range=[0, 100]),
                          legend=dict(orientation="h"), height=380, margin=dict(t=30))
        st.plotly_chart(fig, use_container_width=True)
with colR:
    st.subheader("Lead Time trend (daily avg + 7d)")
    if not daily.empty:
        fig2 = px.line(daily, x="deployed_at", y=["avg_lead_hours", "lead_7d"],
                       labels={"value": "hours", "variable": "series"})
        fig2.update_layout(height=380, margin=dict(t=30))
        st.plotly_chart(fig2, use_container_width=True)

st.subheader("Slowest / failed changes (triage)")
if not fdf.empty:
    top = fdf.sort_values("lead_time_hours", ascending=False).head(15)[
        ["pr_id", "team", "deployed_at", "lead_time_hours", "change_fail", "restore_hours"]]
    st.dataframe(top, use_container_width=True)
else:
    st.warning("No data for current filters.")

with st.expander("DORA tier reference"):
    st.markdown("""
| Metric | Elite | High | Medium | Low |
|---|---|---|---|---|
| Frequency (/day) | ≥1 | ≥1/wk | ≥1/mo | <1/mo |
| Lead Time | <24h | <1wk | <1mo | >1mo |
| Fail Rate | ≤15% | ≤30% | ≤45% | >45% |
| MTTR | <1h | <24h | <1wk | >1wk |
""")
