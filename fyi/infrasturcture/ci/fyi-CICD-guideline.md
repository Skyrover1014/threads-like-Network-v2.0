# CI/CD Guideline

This document summarizes the current end-to-end workflow for Threads, from feature development to production deployment.

## 1. Branching & Testing Flow
- **Feature branches (`ci-*`, `feature-*`, `fix-*`, `refactor-*`, `test-*`, `chore-*`, `build-*`)**  
  - Pushes trigger `.github/workflows/feature_unit_test.yml`.  
  - The workflow writes the required `.env`, builds the Docker test stack (`backend/docker-compose-test.yml`), and runs unit/integration suites via the `web` service. Only green builds should move forward to pull requests.
- **Pull request → `dev`**  
  - After merge, `.github/workflows/dev_smoke_test.yml` builds runtime images for `web`, `celery`, `celery-beat`, and `nginx`, writes environment files, runs `docker-compose-smoke-test.yml`, hits `/healthz` plus static assets, then tears everything down. This guarantees the runtime images actually boot before being published.

## 2. Artifact Publishing & Tagging
- Once the dev smoke test succeeds, each runtime image is retagged as `${service}-${{ github.sha }}` and pushed to the ECR repository specified by `ECR_REPO_URL`.  
- These SHA-scoped tags are the single source of truth; downstream environments never rebuild images. The workflow now also cleans up the temporary dev tags after promotion to keep ECR tidy.

## 3. Manual Promotion & Validation
- Engineers can pull the freshly published dev tags onto EC2 (or any staging host) to perform deeper validation—compose the stack, inspect logs, or run load tests.  
- When a commit is declared “ready for prod”, `dev_promote_approved_tag.yml` records the approved SHA in the `prod` environment variable `APPROVED_DEV_TAG`. This makes the tag discoverable by later workflows without copy/paste.

## 4. Production Release Plan
- Pushing to `main` triggers `.github/workflows/prod_retag_deploy.yml`, which:
  1. Verifies `APPROVED_DEV_TAG` exists (set by the promotion workflow).
  2. Logs into ECR, pulls the four `${service}-${APPROVED_DEV_TAG}` images, and calculates a release tag (`YYYYMMDD-###`).
  3. Retags each image to `${service}-${release_tag}`, pushes them back to ECR, and deletes the temporary dev tags. No rebuild occurs; artifacts stay identical to what passed dev smoke tests.
- Production hosts (currently EC2) deploy by pulling the prod release tags. This keeps dev → manual staging → prod perfectly aligned.

## 5. Control & Future Enhancements
- GitHub Environments (`dev`, `test`, `prod`) already scope secrets; additional protections like required reviewers or manual approvals can be layered later.
- Potential next steps:
  - Add an automated staging workflow that pulls approved dev tags and runs heavier validation.
  - Gate `prod_retag_deploy` behind an environment approval or chat notification.
  - Integrate progressive delivery features (feature flags, rolling percentages) when scale demands it.

## 6. Key Principles
- **Build once, promote many**: images are created in `dev_smoke_test` and promoted unchanged.
- **Shift-left testing**: `feature_unit_test` blocks regressions before code reaches `dev`.
- **Observable deployments**: smoke tests hit health/static endpoints; future steps should keep expanding telemetry.
- **Operational hygiene**: deterministic tagging plus dev-tag cleanup keeps ECR understandable and cheap.
