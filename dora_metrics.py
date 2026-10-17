"""Pure DORA metric calculations (testable, no Streamlit import)."""
from __future__ import annotations

import pandas as pd

TIERS = ["Elite", "High", "Medium", "Low"]


def rate_frequency(deploys_per_day: float) -> str:
    if deploys_per_day >= 1.0:
        return "Elite"
    if deploys_per_day >= 1 / 7:
        return "High"
    if deploys_per_day >= 1 / 30:
        return "Medium"
    return "Low"


def rate_lead_time(median_hours: float) -> str:
    if median_hours < 24:
        return "Elite"
    if median_hours < 168:
        return "High"
    if median_hours < 720:
        return "Medium"
    return "Low"


def rate_failure_rate(pct: float) -> str:
    if pct <= 15:
        return "Elite"
    if pct <= 30:
        return "High"
    if pct <= 45:
        return "Medium"
    return "Low"


def rate_mttr(hours: float) -> str:
    if hours < 1:
        return "Elite"
    if hours < 24:
        return "High"
    if hours < 168:
        return "Medium"
    return "Low"


def overall_rating(ratings: list[str]) -> str:
    """Overall = weakest link (standard DORA interpretation)."""
    for tier in reversed(TIERS):  # Low -> Elite
        if tier in ratings:
            return tier
    return "Low"


def compute_dora_metrics(df: pd.DataFrame) -> dict:
    """Expects columns: created_at, deployed_at, lead_time_hours, change_fail(bool), restore_hours."""
    if df.empty:
        return {
            "total_deploys": 0,
            "deploys_per_day": 0.0,
            "lead_time_median_hours": 0.0,
            "change_fail_rate_pct": 0.0,
            "mttr_hours": 0.0,
            "ratings": {},
            "overall": "Low",
        }
    total = len(df)
    days = max((df["deployed_at"].max() - df["deployed_at"].min()).total_seconds() / 86400, 1.0)
    freq = total / days
    lead_med = float(df["lead_time_hours"].median())
    fail_rate = float(df["change_fail"].mean() * 100)
    failed = df[df["change_fail"]]
    mttr = float(failed["restore_hours"].mean()) if len(failed) else 0.0

    ratings = {
        "frequency": rate_frequency(freq),
        "lead_time": rate_lead_time(lead_med),
        "failure_rate": rate_failure_rate(fail_rate),
        "mttr": rate_mttr(mttr),
    }
    return {
        "total_deploys": total,
        "deploys_per_day": round(freq, 3),
        "lead_time_median_hours": round(lead_med, 1),
        "change_fail_rate_pct": round(fail_rate, 1),
        "mttr_hours": round(mttr, 1),
        "ratings": ratings,
        "overall": overall_rating(list(ratings.values())),
    }


def daily_timeseries(df: pd.DataFrame) -> pd.DataFrame:
    """Daily grain + 7d/30d moving averages for velocity vs failure chart."""
    if df.empty:
        return pd.DataFrame()
    tmp = df.set_index("deployed_at").sort_index()
    daily = pd.DataFrame({
        "deploys": tmp.resample("D").size(),
        "failures": tmp[tmp["change_fail"]].resample("D").size(),
        "avg_lead_hours": tmp["lead_time_hours"].resample("D").mean(),
    }).fillna({"deploys": 0, "failures": 0}).reset_index()
    daily["fail_rate_pct"] = (daily["failures"] / daily["deploys"].replace(0, pd.NA) * 100).fillna(0)
    daily["deploys_7d"] = daily["deploys"].rolling(7, min_periods=1).mean()
    daily["deploys_30d"] = daily["deploys"].rolling(30, min_periods=1).mean()
    daily["fail_rate_7d"] = daily["fail_rate_pct"].rolling(7, min_periods=1).mean()
    daily["lead_7d"] = daily["avg_lead_hours"].rolling(7, min_periods=1).mean()
    return daily
