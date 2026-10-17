import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pandas as pd
from dora_metrics import (
    compute_dora_metrics, daily_timeseries,
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


def test_compute_metrics():
    m = compute_dora_metrics(_df())
    assert m["total_deploys"] == 2
    assert m["change_fail_rate_pct"] == 50.0
    assert m["mttr_hours"] == 5.0
    assert m["overall"] in ("Elite", "High", "Medium", "Low")


def test_daily():
    d = daily_timeseries(_df())
    assert "deploys_7d" in d.columns and "fail_rate_7d" in d.columns
    assert d["deploys"].sum() == 2
