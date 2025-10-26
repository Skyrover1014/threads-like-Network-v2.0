# CI/CD Guideline

This document summarizes the current end-to-end workflow for Threads, from feature development to production deployment.

## 1. Branching & Testing Flow
- **Feature branches (`ci-*`)**: push triggers `.github/workflows/test.yml`, which builds the test stack defined in `backend/docker-compose-test.yml` and runs unit/integration suites inside the `web-test` container. Only green builds should proceed to pull requests.
- **Pull request → `dev`**: after code review and merge, `.github/workflows/smoke_test_dev.yml` runs automatically. It builds runtime images (web, celery, celery-beat, nginx), writes the necessary `.env`, spins up `docker-compose-smoke-test.yml`, checks `/healthz` and static assets, then tears everything down.

## 2. Artifact Publishing
- Successful dev smoke tests retag each runtime image with `${{ github.sha }}` and push them to ECR via the `ECR_REPO` secret. These images are the single source of truth for subsequent stages (no rebuilds downstream).

## 3. Manual Promotion & Validation
- After the dev workflow pushes images, engineers manually pull the same tags on AWS (currently EC2) to verify real infrastructure concerns—e.g., compose up the services, monitor logs, and optionally run stress tests. This acts as an interim staging/canary step without requiring a separate automated workflow yet.

## 4. Production Release Plan
- Merging `dev` → `prod`/`master` should not rebuild code. Instead:
  1. GitHub workflow authenticates to ECR, pulls the dev tag, and runs production smoke tests (reusing runtime compose files or ECS tasks).
  2. On success, retag the image as `prod-${sha}` (or semantic versions) and push it back to ECR.
  3. Deployment jobs/EC2 pull the prod tag and update the running services.
- This ensures all environments (dev → manual staging → prod) consume the identical artifact produced in step 2.

## 5. Control & Future Enhancements
- Use GitHub Environments (`dev`, `staging`, `prod`) to scope secrets, require approvals, and guard promotions.
- When ready, add automated staging/prod workflows that:
  - Pull dev tags and redeploy to staging with optional load tests.
  - Require manual approval before promoting the same tag to prod.
  - Integrate feature flags or weighted routing for gradual rollouts.

## 6. Key Principles
- **Build once, promote many**: binaries/images are produced only in `smoke_test_dev` and reused everywhere else.
- **Shift-left testing**: `test.yml` blocks regressions before code hits `dev`.
- **Observable deployments**: every stage should emit logs/metrics (health endpoints, docker logs, etc.) to expedite rollback decisions.
- **Room to scale**: the current flow already aligns with industry practices, and can later absorb staging automation, canary releases, or infra-as-code driven deployments without major redesign.
