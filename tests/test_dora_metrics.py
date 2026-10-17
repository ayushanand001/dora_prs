import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from dora_metrics import (
    compute_dora_metrics, daily_timeseries, overall_rating,
    rate_failure_rate, rate_frequency, rate_lead_time, rate_mttr,
)


def _df():
    return pd.DataFrame({
        "created_at": pd.to_datetime(["2026-01-01", "2026-01-02"]),
        "deployed_at": pd.to_datetime(["2026-01-02", "2026-01-03"]),
        "lead_time_hours": [10.0, 30.0],
        "change_fail": [False, True],
        "restore_hours": [0.0, 5.0],
    })


def test_tier_boundaries():
    assert rate_frequency(2) == "Elite"
    assert rate_lead_time(10) == "Elite"
    assert rate_failure_rate(50) == "Low"
    assert rate_mttr(5) == "High"


def test_all_tiers():
    assert rate_frequency(1.5) == "Elite"
    assert rate_frequency(0.5) == "High"
    assert rate_frequency(0.1) == "Medium"
    assert rate_frequency(0.01) == "Low"

    assert rate_lead_time(12) == "Elite"
    assert rate_lead_time(100) == "High"
    assert rate_lead_time(300) == "Medium"
    assert rate_lead_time(800) == "Low"

    assert rate_failure_rate(10) == "Elite"
    assert rate_failure_rate(25) == "High"
    assert rate_failure_rate(40) == "Medium"
    assert rate_failure_rate(60) == "Low"

    assert rate_mttr(0.5) == "Elite"
    assert rate_mttr(12) == "High"
    assert rate_mttr(100) == "Medium"
    assert rate_mttr(200) == "Low"


def test_compute_metrics():
    m = compute_dora_metrics(_df())
    assert m["total_deploys"] == 2
    assert m["change_fail_rate_pct"] == 50.0
    assert m["mttr_hours"] == 5.0
    assert m["overall"] in ("Elite", "High", "Medium", "Low")


def test_empty_dataframe():
    m = compute_dora_metrics(pd.DataFrame())
    assert m["total_deploys"] == 0
    assert m["overall"] == "Low"

    d = daily_timeseries(pd.DataFrame())
    assert d.empty


def test_daily():
    d = daily_timeseries(_df())
    assert "deploys_7d" in d.columns and "fail_rate_7d" in d.columns
    assert d["deploys"].sum() == 2


def test_overall_rating():
    assert overall_rating([]) == "Low"
    assert overall_rating(["Elite", "Elite", "Elite"]) == "Elite"
    assert overall_rating(["Elite", "High", "Elite"]) == "High"
    assert overall_rating(["Elite", "Medium"]) == "Medium"
    assert overall_rating(["Elite", "Low"]) == "Low"

