# Docker Compose 環境變數使用指南

## 1. 變數來源層級

### Docker Compose 層級 (`${VAR}`)
- **來源**：`docker-compose-*.yml` 同層的 `.env` 檔案
- **用途**：在 compose 檔案中替換變數值
- **語法**：`${VAR_NAME}`

### Container 層級 (`$${VAR}`)
- **來源**：Container 內部的環境變數
- **用途**：在 container 內部使用（如 health check）
- **語法**：`$${VAR_NAME}`

## 2. 專案變數流程

### Dev 環境 (`docker-compose-local-dev.yml`)

```yaml
services:
  db-dev:
    env_file:
      - conf/dev/.env
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]

  web-dev:
    build:
      context: .
      target: runtime-dev
    env_file: conf/dev/.env   # Django/ Celery 共用同一份設定
```

- Compose 層級目前沒有使用 `${VAR}`（dev 直接 build），所以不需要 `backend/.env`。
- `conf/dev/.env` 同時提供 Postgres 初始化需要的 `POSTGRES_*` 以及 Django `DATABASE_*`、API keys 等。

### Prod 環境 (`docker-compose-local-prod.yml`)

```yaml
services:
  init-static:
    image: web-prod:${LOCAL_PROD_IMAGE_TAG}  # 從 backend/.env 解析 tag

  db-prod:
    env_file:
      - conf/prod/.env
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U $${POSTGRES_USER} -d $${POSTGRES_DB}"]

  web-prod:
    image: web-prod:${LOCAL_PROD_IMAGE_TAG}
    env_file: conf/prod/.env
```

- Compose 層級透過 `backend/.env` 的 `LOCAL_PROD_IMAGE_TAG` 來決定要啟動哪個版本的映像。
- `conf/prod/.env` 會提供 DB 初始化變數（`POSTGRES_*`）與 Django 執行時配置（`DATABASE_*`、Redis、Secrets 等）。

## 3. 需要的環境檔案

### `backend/.env` (Docker Compose 層級)
```bash
# 指定要啟動/建置的映像版本
LOCAL_PROD_IMAGE_TAG=1.0.0
```

### `backend/conf/dev/.env` (Application 層級)
```bash
# Postgres 初始化 & healthcheck
POSTGRES_DB=db-dev
POSTGRES_USER=postgres
POSTGRES_PASSWORD=123456

# Django 設定
DATABASE_NAME=threads
DATABASE_USER=postgres
DATABASE_PASSWORD=123456
DATABASE_HOST=db-dev
DATABASE_PORT=5432

# Django Settings
DJANGO_SECRET_KEY=your-secret-key-here-change-in-production

# Redis Configuration
REDIS_URL=redis://redis-dev:6379/0
CELERY_BROKER_URL=redis://redis-dev:6379/0
CELERY_RESULT_BACKEND=redis://redis-dev:6379/0

# API Keys (add your actual keys)
OPENAI_API_KEY=your-openai-api-key
SERPAPI_API_KEY=your-serpapi-key
```

### `backend/conf/prod/.env` (Application 層級)
```bash
# Postgres 初始化 & healthcheck
POSTGRES_DB=threads
POSTGRES_USER=skyrover
POSTGRES_PASSWORD=jweflkn-123-ewfno-242

# Django 設定（可依實際環境調整）
DATABASE_NAME=threads
DATABASE_USER=skyrover
DATABASE_PASSWORD=jweflkn-123-ewfno-242
DATABASE_HOST=db-prod
DATABASE_PORT=5432

# Django Settings
DJANGO_SECRET_KEY=your-production-secret-key

# Redis Configuration
REDIS_URL=redis://redis-prod:6379/0
CELERY_BROKER_URL=redis://redis-prod:6379/0
CELERY_RESULT_BACKEND=redis://redis-prod:6379/0

# API Keys (add your actual keys)
OPENAI_API_KEY=your-openai-api-key
SERPAPI_API_KEY=your-serpapi-key
```

## 4. 變數解析順序

1. **Docker Compose 啟動時**：
   - 讀取 `backend/.env` → 解析 `${LOCAL_PROD_IMAGE_TAG}` 並套用到 `image: web-prod:${LOCAL_PROD_IMAGE_TAG}`。
   - 依照 `env_file` 設定，把 `conf/dev/.env` 或 `conf/prod/.env` 挂入對應的服務。

2. **Container 運行時**：
   - Postgres 官方映像會讀取 `POSTGRES_*` 並初始化資料庫，healthcheck 使用 `$${POSTGRES_DB}`/`$${POSTGRES_USER}`。
   - Django/Celery 從同一份 `env_file` 取得 `DATABASE_*`、`REDIS_URL` 等設定。

## 5. 關鍵差異

| 語法 | 來源 | 用途 | 範例 |
|------|------|------|------|
| `${VAR}` | Docker Compose 同層 `.env` | Compose 檔案內替換 | `${LOCAL_PROD_IMAGE_TAG}` |
| `$${VAR}` | Container 環境變數 | Container 內部使用 | `$${POSTGRES_DB}` |
| `env_file` | 指定路徑 `.env` | Application 設定 | `conf/dev/.env` |

## 6. 常見問題

### 問題：`FATAL: database "..." does not exist / role "..." does not exist`
**原因**：`conf/dev/.env` 或 `conf/prod/.env` 中的 `POSTGRES_*` 沒有被載入（檔案缺失、命名錯誤）。
**解決**：確認 `env_file` 指向的檔案存在且含有正確的 `POSTGRES_DB/POSTGRES_USER/POSTGRES_PASSWORD`。

### 問題：Health check 失敗
**原因**：Container 環境變數或 DB 初始化失敗。
**檢查**：
1. `conf/*/.env` 是否存在且內容格式正確
2. `docker compose config` 是否能解析出 service 的 `env_file`
3. 容器 log 是否顯示密碼錯誤或 `POSTGRES_USER` 拼錯等訊息

## 7. 最佳實踐

1. **分離環境變數**：
   - Docker Compose 層級：`backend/.env`
   - Application 層級：`conf/dev/.env`, `conf/prod/.env`

2. **變數命名規範**：
   - Docker Compose：`${ENV_SERVICE_VARIABLE}`
   - Container：`$${SERVICE_VARIABLE}`

3. **安全性**：
   - 不要將敏感資訊提交到版本控制
   - 使用 `.env.example` 作為範本
   - 生產環境使用更強的密碼

4. **除錯技巧**：
   ```bash
   # 檢查 container 環境變數
   docker exec -it container_name env
   
   # 檢查 Docker Compose 變數解析
   docker-compose config
   ```
