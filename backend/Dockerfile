# 使用 Python 官方映像
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴與 Poetry
RUN apt-get update && apt-get install -y curl build-essential libpq-dev \
    && curl -sSL https://install.python-poetry.org | python3 - \
    && ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# 將 pyproject.toml 和 poetry.lock 複製進容器
COPY pyproject.toml poetry.lock* /app/

COPY README.md /app/

# 安裝依賴
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# 複製其餘專案檔案
COPY . /app/

# 預設執行指令
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]