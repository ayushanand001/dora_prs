"""Generate mock GitHub PR / deployment data for DORA tracker (local-only, no API needed)."""
import random
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd

NUM_PRS = 350
DAYS = 90
TEAMS = ["Frontend", "Backend", "Data", "Platform"]
FAIL_PROB = 0.28

OUT = Path(__file__).parent / "data" / "prs.csv"


def main() -> None:
    random.seed(42)
    np.random.seed(42)
    end = datetime.now().replace(microsecond=0)
    start = end - timedelta(days=DAYS)

    rows = []
    for i in range(NUM_PRS):
        team = random.choice(TEAMS)
        # Team velocity skew: Platform deploys faster, Data slower
        team_shift = {"Platform": -0.4, "Frontend": -0.1, "Backend": 0.0, "Data": 0.4}[team]
        created = start + timedelta(seconds=random.randint(0, DAYS * 86400))
        lead_hours = float(np.random.lognormal(mean=3.5 + team_shift, sigma=1.0))
        lead_hours = max(1.0, min(lead_hours, 2160.0))  # clamp 1h..90d
        deployed = created + timedelta(hours=lead_hours)
        if deployed > end:
            deployed = end - timedelta(hours=random.randint(0, 48))
            lead_hours = (deployed - created).total_seconds() / 3600
        failed = random.random() < FAIL_PROB
        if failed:
            restore = float(np.random.lognormal(mean=2.5, sigma=1.2))  # median ~12h
            if random.random() < 0.08:  # major incident tail
                restore *= 10
            restore = max(0.2, min(restore, 720.0))
        else:
            restore = 0.0
        rows.append({
            "pr_id": 2000 + i,
            "team": team,
            "created_at": created,
            "merged_at": created + timedelta(hours=lead_hours * 0.7),
            "deployed_at": deployed,
            "lead_time_hours": round(lead_hours, 1),
            "change_fail": failed,
            "restore_hours": round(restore, 1),
        })
    df = pd.DataFrame(rows).sort_values("deployed_at")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT, index=False)
    print(f"Wrote {len(df)} PRs to {OUT} | fail_rate={df['change_fail'].mean()*100:.1f}% "
          f"median_lead={df['lead_time_hours'].median():.1f}h")


if __name__ == "__main__":
    main()
