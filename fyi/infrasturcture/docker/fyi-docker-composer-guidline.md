# Docker Compose 使用指南

## 命名規則

### 專案群組名稱
- **Dev 環境**: `threads-dev`
- **Prod 環境**: `threads-prod`

### 容器命名規則
所有容器都遵循 `{project}-{environment}-{service}` 格式：

#### Dev 環境容器
- `threads-dev-db` - PostgreSQL 資料庫
- `threads-dev-redis` - Redis 快取
- `threads-dev-web` - Django Web 服務
- `threads-dev-celery` - Celery Worker
- `threads-dev-celery-beat` - Celery Beat 排程器

#### Prod 環境容器
- `threads-prod-db` - PostgreSQL 資料庫
- `threads-prod-redis` - Redis 快取
- `threads-prod-init-static` - 靜態文件初始化
- `threads-prod-web` - Django Web 服務 (Gunicorn)
- `threads-prod-celery` - Celery Worker
- `threads-prod-celery-beat` - Celery Beat 排程器
- `threads-prod-nginx` - Nginx 反向代理

## 1. 首次建立 Image 和啟動容器，與往後啟動方式

### Dev 環境 (`docker-compose-local-dev.yml`)

#### 首次啟動
```bash
# 在 backend/ 目錄執行
docker compose -f docker-compose-local-dev.yml up --build
```

#### 往後啟動
```bash
# 直接啟動（會自動重新構建）
docker compose -f docker-compose-local-dev.yml up --build

# 或背景執行
docker compose -f docker-compose-local-dev.yml up --build -d
```

### Prod 環境 (`docker-compose-local-prod.yml`)

#### 首次啟動（需要先構建映像）
```bash
# 0. 確保 backend/.env 內已設定 IMAGE_TAG=1.0.0（或任意版本）

# 1. 在 backend/ 目錄執行腳本（可附加 docker compose 的其他參數，例如 -d）
./scripts/build-prod.sh

# 2. 執行 migration（首次需要）
docker compose -f docker-compose-local-prod.yml exec web-prod python manage.py migrate

# 3. 創建超級用戶（首次需要）
docker compose -f docker-compose-local-prod.yml exec web-prod python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else print('Admin user already exists')"
```

#### 往後啟動
```bash
# 直接啟動（使用已構建的映像，腳本會自動讀取 IMAGE_TAG）
./scripts/build-prod.sh

# 或背景執行
./scripts/build-prod.sh -d
```

## 2. 核心運作差異

### Dev 環境特點

| 特性 | 說明 |
|------|------|
| **構建方式** | 每次 `up --build` 都會重新構建 |
| **Web 服務器** | Django 開發服務器 (`runserver`) |
| **端口暴露** | 直接暴露所有服務端口 (5432, 6379, 8000) |
| **靜態文件** | Django 直接處理，無需收集 |
| **熱重載** | 支援，程式碼變更即時生效 |
| **Volume 掛載** | 整個專案目錄掛載 (`.:/app`) |
| **依賴** | 包含開發依賴 (`--with dev`) |

### Prod 環境特點

| 特性 | 說明 |
|------|------|
| **構建方式** | 使用預構建映像，需要手動重新構建 |
| **Web 服務器** | Gunicorn WSGI 服務器 |
| **端口暴露** | 只有 nginx 暴露端口 (127.0.0.1:8080) |
| **靜態文件** | nginx 處理，需要先收集靜態文件 |
| **反向代理** | nginx 作為反向代理 |
| **安全隔離** | 服務間內部通信，更安全 |
| **生產優化** | 不包含開發依賴，更輕量 |

### 架構對比

#### Dev 架構
```
用戶 → Django Dev Server:8000 → 資料庫/Redis
```

#### Prod 架構
```
用戶 → nginx:8080 → Gunicorn:8000 → 資料庫/Redis
     ↓
   靜態文件直接提供
```

## 3. 檢查映像、容器、資料狀態

### 檢查映像
```bash
# 查看所有映像
docker images

# 查看特定映像
docker images | grep web-prod
docker images | grep nginx-prod
```

### 檢查容器狀態
```bash
# 查看所有運行中的容器
docker ps

# 查看特定 compose 服務狀態
docker compose -f docker-compose-local-prod.yml ps
docker compose -f docker-compose-local-dev.yml ps

# 查看特定容器（使用自定義名稱）
docker ps | grep threads-dev-web
docker ps | grep threads-prod-nginx

# 查看容器詳細資訊
docker inspect threads-dev-web
docker inspect threads-prod-nginx
```

### 檢查 Volume 狀態
```bash
# 查看所有 volumes
docker volume ls

# 查看特定 volume 詳情
docker volume inspect threads_postgres_data
docker volume inspect threads_postgres_data_prod
docker volume inspect threads_static_volume

# 查看 volume 使用情況
docker system df -v
```

### 檢查服務健康狀態
```bash
# 查看服務日誌（使用服務名稱）
docker compose -f docker-compose-local-prod.yml logs web-prod
docker compose -f docker-compose-local-prod.yml logs nginx-prod

# 查看容器日誌（使用容器名稱）
docker logs threads-prod-web
docker logs threads-prod-nginx

# 查看所有服務日誌
docker compose -f docker-compose-local-prod.yml logs

# 即時查看日誌
docker compose -f docker-compose-local-prod.yml logs -f web-prod
docker logs -f threads-prod-web
```

### 檢查資料庫狀態
```bash
# 進入資料庫容器（使用服務名稱）
docker compose -f docker-compose-local-prod.yml exec db-prod psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}

# 進入資料庫容器（使用容器名稱）
docker exec -it threads-prod-db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB}

# 檢查 migration 狀態
docker compose -f docker-compose-local-prod.yml exec web-prod python manage.py showmigrations
docker exec threads-prod-web python manage.py showmigrations

# 檢查 Django 資料庫連接
docker compose -f docker-compose-local-prod.yml exec web-prod python manage.py dbshell
docker exec threads-prod-web python manage.py dbshell
```

### 常用維護命令

#### 停止服務
```bash
# 停止所有服務
docker compose -f docker-compose-local-prod.yml down
docker compose -f docker-compose-local-dev.yml down

# 停止並刪除 volumes（危險！會刪除資料）
docker compose -f docker-compose-local-prod.yml down --volumes
```

#### 重新啟動特定服務
```bash
# 重新啟動 web 服務（使用服務名稱）
docker compose -f docker-compose-local-prod.yml restart web-prod

# 重新啟動 web 服務（使用容器名稱）
docker restart threads-prod-web

# 重新啟動所有服務
docker compose -f docker-compose-local-prod.yml restart
```

#### 清理資源
```bash
# 清理未使用的映像
docker image prune

# 清理所有未使用的資源
docker system prune

# 清理 volumes（危險！）
docker volume prune
```

## 4. 故障排除

### 常見問題

#### 1. 500 錯誤
```bash
# 檢查 web 服務日誌
docker compose -f docker-compose-local-prod.yml logs web-prod

# 檢查 migration 狀態
docker compose -f docker-compose-local-prod.yml exec web-prod python manage.py showmigrations
```

#### 2. 資料庫連接問題
```bash
# 檢查資料庫健康狀態
docker compose -f docker-compose-local-prod.yml ps db-prod

# 檢查資料庫日誌
docker compose -f docker-compose-local-prod.yml logs db-prod
```

#### 3. 靜態文件問題
```bash
# 重新收集靜態文件
docker compose -f docker-compose-local-prod.yml exec web-prod python manage.py collectstatic --noinput
```

#### 4. nginx 問題
```bash
# 檢查 nginx 配置
docker compose -f docker-compose-local-prod.yml exec nginx-prod nginx -t

# 重新載入 nginx 配置
docker compose -f docker-compose-local-prod.yml exec nginx-prod nginx -s reload
```

## 5. 最佳實踐

### 開發流程
1. 使用 dev 環境進行開發
2. 定期測試 prod 環境
3. 程式碼變更後重新構建 prod 映像

### 部署流程
1. 構建新的 prod 映像
2. 停止舊服務
3. 啟動新服務
4. 檢查服務健康狀態

### 資料備份
```bash
# 備份資料庫
docker compose -f docker-compose-local-prod.yml exec db-prod pg_dump -U ${POSTGRES_USER} ${POSTGRES_DB} > backup.sql

# 恢復資料庫
docker compose -f docker-compose-local-prod.yml exec -T db-prod psql -U ${POSTGRES_USER} ${POSTGRES_DB} < backup.sql
```
