# DORA Metrics & Velocity Tracker — Capstone #5

[![CI](https://github.com/ayushanand001/dora_prs/actions/workflows/ci.yml/badge.svg)](https://github.com/ayushanand001/dora_prs/actions/workflows/ci.yml)
[![Docker Publish](https://github.com/ayushanand001/dora_prs/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/ayushanand001/dora_prs/actions/workflows/docker-publish.yml)
[![Data Refresh](https://github.com/ayushanand001/dora_prs/actions/workflows/data-refresh.yml/badge.svg)](https://github.com/ayushanand001/dora_prs/actions/workflows/data-refresh.yml)
[![Security Scan](https://github.com/ayushanand001/dora_prs/actions/workflows/security.yml/badge.svg)](https://github.com/ayushanand001/dora_prs/actions/workflows/security.yml)

Implements Use Case 5: Deployment Frequency, Lead Time, Change Failure Rate, MTTR from mock GitHub PR data.

## Quickstart

```powershell
pip install -r requirements.txt
python generate_mock_data.py
pytest tests -v
streamlit run app.py
```

### Docker
```powershell
docker build -t dora-tracker:latest .
docker run -p 8501:8501 dora-tracker:latest
```

### Kubernetes (Kind / Minikube / Docker Desktop)
```powershell
kubectl apply -f k8s/
kubectl port-forward svc/dora-service 8080:80
# open http://localhost:8080
```

---

## 🚀 GitHub Actions CI/CD Pipelines

Automated workflows are located in [`.github/workflows/`](.github/workflows/):

1. **Continuous Integration ([`ci.yml`](.github/workflows/ci.yml))**:
   - **Linting & Code Style**: Runs `flake8` to enforce syntax checks and clean formatting.
   - **Test & Coverage Matrix**: Executes `pytest` with coverage report (`pytest-cov`) across Python 3.11 and 3.12.
   - **Data Sanity Check**: Verifies that `generate_mock_data.py` executes and outputs valid PR data.
   - **Kubernetes Validation**: Client-side dry-run validation of `k8s/` resource manifests.
   - **Docker Smoke Test**: Builds container image and performs live health-check probe against `http://localhost:8501/_stcore/health`.

2. **Docker Publish & Container Registry ([`docker-publish.yml`](.github/workflows/docker-publish.yml))**:
   - Triggers on pushes to `main` branch, tags (`v*.*.*`), or manual dispatch.
   - Builds and publishes production images to GitHub Container Registry (`ghcr.io/ayushanand001/dora_prs`).
   - Tags releases with `latest`, Git commit SHA, and Semantic Versioning.
   - Runs **Aqua Security Trivy** vulnerability scanning on the built container.

3. **Scheduled Data Refresh ([`data-refresh.yml`](.github/workflows/data-refresh.yml))**:
   - Scheduled daily at `02:00 UTC` (or triggered on demand via `workflow_dispatch`).
   - Automatically regenerates `data/prs.csv` and commits the latest dataset via `git-auto-commit-action`.

4. **Security & Vulnerability Scanning ([`security.yml`](.github/workflows/security.yml))**:
   - Scans dependencies for known CVEs using `pip-audit`.
   - Performs Python AST static application security testing using `bandit`.

---

## Project Structure

- `dora_metrics.py` — Pure DORA metric computations and rating tiers (unit tested)
- `app.py` — Streamlit dashboard (4 gauges, dual-axis velocity vs failure %, lead time trend, triage table)
- `generate_mock_data.py` — PR dataset generator (teams: Frontend, Backend, Data, Platform)
- `data/prs.csv` — PR dataset (350 PRs across 90 days)
- `k8s/` — Kubernetes Deployment (probes `/_stcore/health`), NodePort Service, and ConfigMap
- `tests/` — Automated test suite with Pytest
- `.github/workflows/` — Production GitHub Actions CI/CD pipelines
