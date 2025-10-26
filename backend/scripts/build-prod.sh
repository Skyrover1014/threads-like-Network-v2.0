#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
ENV_FILE="${PROJECT_ROOT}/.env"

if [[ -f "${ENV_FILE}" ]]; then
  # shellcheck source=/dev/null
  set -a
  source "${ENV_FILE}"
  set +a
fi

if [[ -z "${LOCAL_PROD_IMAGE_TAG:-}" ]]; then
  echo "LOCAL_PROD_IMAGE_TAG is not set. Define it in ${ENV_FILE} or export it before running this script." >&2
  exit 1
fi

echo "Building application images with tag: ${LOCAL_PROD_IMAGE_TAG}"
docker build \
  -t "web-prod:${LOCAL_PROD_IMAGE_TAG}" \
  --target runtime-web \
  -f "${PROJECT_ROOT}/Dockerfile" \
  "${PROJECT_ROOT}"

docker build \
  -t "celery-prod:${LOCAL_PROD_IMAGE_TAG}" \
  --target runtime-celery \
  -f "${PROJECT_ROOT}/Dockerfile" \
  "${PROJECT_ROOT}"

docker build \
  -t "celery-beat-prod:${LOCAL_PROD_IMAGE_TAG}" \
  --target runtime-celery-beat \
  -f "${PROJECT_ROOT}/Dockerfile" \
  "${PROJECT_ROOT}"

docker build \
  -t "nginx-prod:${LOCAL_PROD_IMAGE_TAG}" \
  -f "${PROJECT_ROOT}/nginx/Dockerfile" \
  "${PROJECT_ROOT}/nginx"

echo "Launching stack via docker compose with LOCAL_PROD_IMAGE_TAG=${LOCAL_PROD_IMAGE_TAG}"
docker compose \
  -f "${PROJECT_ROOT}/docker-compose-local-prod.yml" \
  up "$@"
