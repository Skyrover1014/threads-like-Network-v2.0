# 使用 Python 官方映像
FROM python:3.11-slim AS base
ENV  POETRY_VERSION=1.6.1 \
  PYTHONUNBUFFERED=1 \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_NO_CACHE_DIR=off \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_HOME="/opt/poetry" \
  POETRY_VIRTUALENVS_IN_PROJECT=true \
  POETRY_NO_INTERACTION=1 \
  PYSETUP_PATH="/opt/pysetup" \
  VENV_PATH="/opt/pysetup/.venv"
ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

# ---------- builder base (共用安裝 poetry + 安裝路徑 + 依賴檔案) ----------
FROM base AS builder-base
RUN --mount=type=cache,target=/root/.cache \
    pip install "poetry==$POETRY_VERSION"
WORKDIR $PYSETUP_PATH
COPY pyproject.toml poetry.lock* ./

# ---------- builder: dev ----------
FROM builder-base AS builder-dev
RUN --mount=type=cache,target=$POETRY_HOME/pypoetry/cache \
    poetry install --with dev --no-root --without test

# ---------- runtime: dev ----------
FROM base AS runtime-dev
ENV DJANGO_SETTINGS_MODULE=core.settings
COPY --from=builder-dev $VENV_PATH $VENV_PATH
COPY manage.py /app/
COPY core /app/core
COPY threads /app/threads
WORKDIR /app
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


# ---------- builder: test ----------
FROM builder-base AS builder-test
RUN --mount=type=cache,target=$POETRY_HOME/pypoetry/cache \
    poetry install --with test --no-root --without dev


# ---------- runtime: test ----------
FROM base AS runtime-test
ENV DJANGO_SETTINGS_MODULE=core.settings
ENV PYTHONPATH=/app
COPY --from=builder-test $VENV_PATH $VENV_PATH
COPY manage.py /app/
COPY __init__.py /app/
COPY core /app/core
COPY threads /app/threads
COPY tests /app/tests
WORKDIR /app
EXPOSE 8000



# ---------- builder: deployment  ----------
FROM builder-base AS builder-deployment
RUN --mount=type=cache,target=$POETRY_HOME/pypoetry/cache \
    poetry install --no-dev


# ---------- runtime: web ----------
FROM base AS runtime-web
ENV DJANGO_SETTINGS_MODULE=core.settings
COPY --from=builder-deployment $VENV_PATH $VENV_PATH
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*
COPY manage.py /app/
COPY core /app/core
COPY threads /app/threads
WORKDIR /app
EXPOSE 8000
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]


# ---------- runtime: celery ----------
FROM runtime-web AS runtime-celery
CMD ["python", "-m", "celery", "-A", "core", "worker", "--loglevel=INFO", "--concurrency=2"]

# ---------- runtime: celery-beat ----------
FROM runtime-web AS runtime-celery-beat
CMD ["celery", "-A", "core", "beat", "--loglevel=INFO"]