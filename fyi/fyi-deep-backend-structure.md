# Django DRF + CQRS + Clean Architecture 深度分層與實作總結

---

## 1. 架構核心原則
- **DRF**：負責 API 輸入/輸出（ViewSet/Serializer）。
- **CQRS**：Command（寫）和 Query（讀）分開設計。
- **Clean Architecture**：分層明確，interface/use_case/domain/infrastructure 各自獨立。

---

## 2. 推薦目錄結構
```
network/
  ├── domain/         # 業務邏輯（純 Python class）
  ├── use_cases/      # Command/Query 用例
  ├── infrastructure/ # ORM models, repository pattern
  ├── interface/      # API 介面（views, serializers）
  ├── urls.py
  └── ...（Django 標準檔案）
```
- **中大型專案建議**：每個物件（如 Post、Comment）一個檔案，維護、擴展、測試更容易。

---

## 3. 各層責任
- **domain/**：純業務規則與驗證，不依賴 Django/ORM。
- **use_cases/**：Command/Query 用例，調用 domain 驗證與 repository。
- **infrastructure/**：Django ORM models、資料存取實作（repository）。
- **interface/**：API 入口（ViewSet）、序列化（Serializer），只負責 request/response。

---

## 4. 互動流程圖
```
[ 前端/用戶 ]
      │
      ▼
[ interface/views.py (ViewSet) ]
      │  1. 收到 HTTP request
      │  2. 解析資料、驗證權限
      │  3. 呼叫 UseCase
      ▼
[ use_cases/xxx_use_case.py ]
      │  4. 執行商業邏輯
      │  5. 呼叫 Domain 驗證
      │  6. 呼叫 Repository 存取資料
      ▼
[ domain/xxx.py ]
      │  7. 驗證業務規則
      ▼
[ infrastructure/repository/xxx_repository.py ]
      │  8. 用 ORM 存取資料庫
      ▼
[ infrastructure/models/xxx.py ]
      │  9. ORM 定義資料結構
      ▼
[ 資料庫 ]
```

---

## 5. 各層差異與職責
- **Model**：定義資料結構，對應資料表。
- **Repository**：封裝資料存取邏輯，讓上層不用直接碰 ORM。
- **ViewSet**：API 入口，處理 HTTP request/response，只呼叫 use_case，不直接碰資料存取。

---

## 6. Swagger 文件整合
- 推薦用 drf-yasg。
- 在 core/urls.py 加入：
  ```python
  path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
  path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
  ```
- 只要 interface 層用 DRF 標準寫法，Swagger 會自動產生互動式 API 文件。
- 文件網址：`/swagger/`、`/redoc/`

---

## 7. 實作順序建議
1. 先寫 domain 層（業務規則 class）
2. 再寫 infrastructure 層（ORM model, repository）
3. 再寫 use_case 層（command/query 用例）
4. 最後寫 interface 層（serializer, viewset, url）

---

## 8. 參考
- `fyi-drf-deep-instructure.md`：DRF 功能全覽與實作細節
- `fyi-refractor-backend-instructure.md`：分層原則與目錄設計

---

如需具體範例或進階應用，請參考上述文件或提出需求！ 