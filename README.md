# DORA Metrics & Velocity Tracker — Capstone #5 (local-only)

Implements Use Case 5: Deployment Frequency, Lead Time, Change Failure Rate, MTTR
from mock GitHub PR data. Same toolchain as `day1→day4`.

## Quickstart (NOW, local only)

```powershell
cd capstone_dora
pip install -r requirements.txt
python generate_mock_data.py
pytest tests -v
streamlit run app.py
```

Docker:
```powershell
docker build -t dora-tracker:latest .
docker run -p 8501:8501 dora-tracker:latest
```

K8s (kind/minikube/Docker Desktop):
```powershell
kubectl apply -f k8s/
kubectl port-forward svc/dora-service 8080:80
# open http://localhost:8080
```

Cron refresh: see `refresh.yaml` — daily `0 2 * * *` regenerates `data/prs.csv`.
Swap that step for `gh api repos/{owner}/{repo}/pulls --paginate` + a parser when ready.

## Files
- `dora_metrics.py` — pure functions + tier logic (tested)
- `app.py` — Streamlit: 4 gauges, dual-axis velocity vs fail%, lead-time trend, triage table
- `data/prs.csv` — 350 PRs / 90d, teams Frontend/Backend/Data/Platform
- `k8s/` — Deployment (probes `/_stcore/health`) + NodePort Service + ConfigMap
- Current mock overall: **Medium** (Freq Elite, Lead High, Fail High, MTTR Medium)
