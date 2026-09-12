# Enterprise Python Demo — Full GitLab CI/CD Showcase

A small FastAPI + PostgreSQL + Celery service used purely as a vehicle to
demonstrate a **complete GitLab CI/CD pipeline** end to end: source control,
code review, CI, security, CD, release management, change management,
audit, and monitoring — plus the broader technology capability matrix
(project mgmt, IaC, DB migrations, Kubernetes, multi-env promotion, etc.),
**scoped to Python only** (all Android-specific capabilities — code signing,
AAB/APK build, mobile distribution, mapping files — are intentionally
excluded, as noted in "Not Applicable" below).

## Project layout

```
app/                    FastAPI application (API, models, config, Celery tasks)
alembic/                Database migrations
tests/
  test_main.py          Unit tests (run against source code)
  test_api.py           API regression tests (run against a live deployment)
  performance/          Locust load test
terraform/              Infrastructure as Code (example: ECR repo per env)
k8s/
  base/                 Base Kubernetes Deployment + Service
  overlays/dev|uat|prod Kustomize overlays -> environment-specific config
scripts/                deploy.sh, migrate.sh, rollback.sh, notify.sh
.gitlab/
  CODEOWNERS            Mandatory reviewers per path (code review/approval)
  merge_request_templates/  Links MRs to Change Requests/tickets
  issue_templates/
.gitlab-ci.yml          The full pipeline (see below)
Dockerfile, docker-compose.yml
```

## Capability matrix -> where it lives

| Area | Implementation |
|---|---|
| Source Control | This Git repo; branch protection + MR workflow (GitLab native) |
| Code Review | `.gitlab/CODEOWNERS`, MR approval rules, `merge_request_templates/Default.md` |
| CI | `quality` + `test` stages: flake8, black, isort, mypy, pytest + coverage |
| Code Quality | `lint-flake8`, `format-check`, `type-check` jobs; `sonar-project.properties` |
| Unit Testing | `unit-tests` job (pytest, JUnit + Cobertura reports) |
| Security Scanning | GitLab SAST/Dependency-Scanning/Secret-Detection templates + `bandit-scan`, `dependency-safety-check`, `container-scan` (Trivy) |
| Secrets Management | All credentials (`DEV_DATABASE_URL`, `JWT_SECRET`, `SLACK_WEBHOOK_URL`, registry creds) as masked/protected CI/CD variables — never in the repo |
| Container Registry | `docker-build-push` job pushes to the GitLab Container Registry |
| Database Migration | `migrate-dev` / `migrate-uat` / `migrate-prod` jobs run Alembic via `scripts/migrate.sh` |
| Infrastructure as Code | `terraform-plan` / `terraform-apply` jobs in `terraform/` |
| Environment Management | `k8s/overlays/{dev,uat,prod}` + GitLab `environment:` blocks with distinct URLs/variables |
| Review Apps | `review-app` / `stop-review-app` jobs, one ephemeral env per merge request |
| Multi-Environment Promotion | Pipeline stages flow `deploy-dev -> api-test-dev -> deploy-uat -> performance-test -> approval -> deploy-prod`, each gated behind the previous |
| Approval Workflow | `change-approval-gate` (manual, requires `CHANGE_REQUEST_ID`) and manual `deploy-uat`/`deploy-prod` jobs |
| Change Management | MR template requires a linked CR/ticket ID; `change-approval-gate` enforces it in-pipeline |
| Performance Testing | `performance-test-uat` job runs Locust against UAT before prod release |
| API Testing | `api-regression-dev` runs `tests/test_api.py` against the deployed DEV URL |
| Release Management | `create-release` job creates a tagged GitLab Release from `CI_COMMIT_TAG` |
| Rollback | Manual `rollback-prod` job (`kubectl rollout undo`) |
| Monitoring | `notify-success` / `notify-failure` jobs post to Slack/Teams; `/health` and `/version` endpoints |
| Compliance & Audit | Native GitLab audit trail (who approved/deployed what, when) across environments, MRs, and pipelines |
| Scheduled Jobs | `scheduled-health-audit` job, triggered only by a GitLab **Pipeline Schedule** (cron), not by pushes |
| Notifications | `scripts/notify.sh` (Slack/Teams webhook), extensible to email |

## What You Cannot Add (Not Applicable — Python vs. Android)

| # | Component | Why Not |
|---|---|---|
| 1 | Code Signing | Python doesn't need code signing |
| 2 | Mobile Distribution | Python is not a mobile app |
| 3 | AAB/APK Build | Python is not Android |
| 4 | Mapping File | Python doesn't have obfuscation |

## Running the demo locally

```bash
cp .env.example .env
docker compose up --build
curl http://localhost:8000/health
```

## Running the pipeline in GitLab

1. Push this repo to a new GitLab project.
2. Under **Settings > CI/CD > Variables**, add (masked + protected as appropriate):
   - `DEV_DATABASE_URL`, `UAT_DATABASE_URL`, `PROD_DATABASE_URL`
   - `SLACK_WEBHOOK_URL` (optional)
   - `CHANGE_REQUEST_ID` (set per pipeline run, or via a triggered pipeline variable, to pass the change-approval gate)
   - Kubernetes/Terraform credentials your runners need (`KUBECONFIG`, AWS creds, etc.)
3. Under **Settings > CI/CD > Protected branches/tags**, protect `main` and release tags so only authorized users can trigger `deploy-uat`/`deploy-prod`.
4. Push to `main` → pipeline runs through DEV automatically; UAT and PROD are manual, gated promotions.
5. Tag a commit (e.g. `git tag v1.0.0 && git push --tags`) to trigger the production path and `create-release`.

## Local pipeline dry-run (no GitLab required)

```bash
pip install -r requirements-dev.txt
flake8 app tests
black --check app tests
pytest tests/test_main.py --cov=app
bandit -r app
docker build -t enterprise-python-demo:local .
```
