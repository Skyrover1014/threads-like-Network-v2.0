# Threads Backend API

一個基於 Django 的社交媒體後端服務，採用 Clean Architecture 設計模式，提供類似 Twitter 的社交功能。

## 🏗️ 專案架構

本專案採用 **Clean Architecture（清潔架構）** 設計模式，將系統分為四個主要層次：

### 1. Domain Layer（領域層）

- **位置**: `threads/domain/`
- **職責**: 核心業務邏輯，不依賴任何外部框架
- **主要組件**:
  - `entities.py`: 領域實體（User, Post, Comment, Like, Follow）
  - `repository.py`: 倉儲介面定義（抽象類）
  - `enum.py`: 業務枚舉

### 2. Infrastructure Layer（基礎設施層）

- **位置**: `threads/infrastructure/`
- **職責**: 技術實現，包含資料庫操作和外部服務整合
- **主要組件**:
  - `repository/`: 倉儲具體實現
  - `cache.py`: Redis 快取服務
  - `external/`: 外部 API 整合（OpenAI）

### 3. Use Cases Layer（用例層）

- **位置**: `threads/use_cases/`
- **職責**: 應用邏輯，協調 Domain 和 Infrastructure 層
- **結構**:
  - `commands/`: 寫操作（創建、更新、刪除）
  - `queries/`: 讀操作（查詢、列表）

### 4. Interface Layer（介面層）

- **位置**: `threads/interface/`
- **職責**: HTTP 請求處理和響應
- **主要組件**:
  - `views/`: Django 視圖
  - `serializers/`: 資料序列化
  - `util/`: 工具函數

## 🚀 技術棧

- **框架**: Django 5.2 + Django REST Framework
- **資料庫**: PostgreSQL
- **快取**: Redis
- **任務佇列**: Celery
- **認證**: JWT (Simple JWT)
- **API 文檔**: drf-spectacular (Swagger)
- **容器化**: Docker + Docker Compose
- **反向代理**: Nginx

## 📡 API 服務

### 認證相關

- `POST /api/token/` - 獲取 JWT Token
- `POST /api/token/refresh/` - 刷新 JWT Token

### 用戶管理

- `POST /api/threads/users/` - 用戶註冊
- `GET /api/threads/users/{user_id}/` - 獲取用戶資料

### 貼文功能

- `GET /api/threads/posts/` - 獲取貼文列表
  - 支援參數: `author_id`, `following`, `offset`, `limit`
- `POST /api/threads/posts/` - 創建新貼文
- `GET /api/threads/posts/{post_id}` - 獲取單一貼文
- `PUT /api/threads/posts/{post_id}` - 更新貼文
- `DELETE /api/threads/posts/{post_id}` - 刪除貼文

### 評論功能

- `GET /api/threads/posts/{post_id}/comments` - 獲取貼文評論
- `POST /api/threads/posts/{post_id}/comments` - 創建評論
- `GET /api/threads/comments/{comment_id}/child_comments` - 獲取子評論
- `POST /api/threads/comments/{comment_id}/child_comments` - 創建子評論
- `PUT /api/threads/comments/{comment_id}` - 更新評論
- `DELETE /api/threads/comments/{comment_id}` - 刪除評論

### 互動功能

- `POST /api/threads/posts/{post_id}/repost` - 轉發貼文
- `POST /api/threads/comments/{comment_id}/repost` - 轉發評論
- `POST /api/threads/posts/{content_id}/like` - 對貼文按讚/取消按讚
- `POST /api/threads/comments/{content_id}/like` - 對評論按讚/取消按讚

### AI 功能

- `POST /api/threads/posts/{post_id}/factCheck` - AI 事實查核貼文
- `POST /api/threads/comments/{comment_id}/factCheck` - AI 事實查核評論

### 系統監控

- `GET /healthz` - 健康檢查

## 🔧 開發環境設置

### 使用 Docker（推薦）

```bash
# 開發環境
docker-compose -f docker-compose-local-dev.yml up

# 本地生產環境測試
docker-compose -f docker-compose-local-prod.yml up
```

### 本地開發

```bash
# 安裝依賴
poetry install

# 設置環境變數
cp .env.example .env

# 運行遷移
python manage.py migrate

# 啟動開發服務器
python manage.py runserver
```

## 📊 資料庫設計

### 核心實體

- **User**: 用戶資料（擴展 Django AbstractUser）
- **Post**: 貼文（繼承 ContentItem）
- **Comment**: 評論（繼承 ContentItem，支援巢狀結構）
- **Follow**: 關注關係
- **LikePost/LikeComment**: 按讚記錄

### 設計特色

- 使用 Generic Foreign Key 支援轉發功能
- 快取計數器欄位提升查詢效能
- 支援巢狀評論結構
- 完整的索引優化

## 🔄 異步任務

使用 Celery 處理背景任務：

- `flush_comment_counts`: 定期刷新評論計數
- `flush_repost_counts`: 定期刷新轉發計數

## 🚧 開發中項目

### 基礎設施整合
- [ ] **Celery 和 Redis 完整整合**
  - [ ] 優化背景任務處理機制
  - [ ] 實現任務監控和錯誤處理
  - [ ] 設置任務重試和失敗處理策略
  - [ ] 整合 Celery Beat 定時任務

### CI/CD 部署
- [ ] **完善 CI/CD 流程**
  - [ ] GitHub Actions 自動化測試
  - [ ] Docker 映像建構和推送到 AWS ECR
  - [ ] 自動化部署到 AWS ECS/EC2
  - [ ] 環境變數和密鑰管理
  - [ ] 藍綠部署策略

### 功能開發
- [ ] 關注/取消關注功能
- [ ] 用戶個人資料頁面
- [ ] 通知系統
- [ ] 圖片上傳功能
- [ ] 搜尋功能
- [ ] 私訊功能

## 🔮 未來優化項目

### 架構優化

- [ ] 引入依賴注入容器（如 dependency-injector）
- [ ] 實現 Domain Events 事件驅動架構
- [ ] 加入 API 版本控制
- [ ] 實現 CQRS 模式分離讀寫操作

### 效能優化

- [ ] 資料庫查詢優化（N+1 問題）
- [ ] Redis 快取策略優化
- [ ] CDN 整合
- [ ] 資料庫分片

### 功能增強

- [ ] 即時通訊（WebSocket）
- [ ] 推播通知
- [ ] 內容推薦系統
- [ ] 多語言支援
- [ ] 內容審核系統

### 監控與維運

- [ ] 完整的日誌系統
- [ ] 效能監控（APM）
- [ ] 錯誤追蹤系統
- [ ] 自動化測試覆蓋率提升

## 📝 API 文檔

開發環境下可訪問：

- Swagger UI: `http://localhost:8000/api/docs/`
- API Schema: `http://localhost:8000/api/schema/`

## 🧪 測試

```bash
# 運行測試
python manage.py test

# 運行特定測試
python manage.py test threads.tests.test_celery_tasks
```

## 📄 授權

此專案為個人學習專案，僅供參考使用。

---

**架構優勢**:

- ✅ 高可測試性
- ✅ 業務邏輯與技術實現分離
- ✅ 易於維護和擴展
- ✅ 統一的錯誤處理機制
- ✅ 支援異步任務處理
