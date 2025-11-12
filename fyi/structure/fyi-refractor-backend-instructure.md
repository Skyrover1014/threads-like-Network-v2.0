# FYI: Refractor Backend Instructure (Django DRF + Clean Architecture + CQRS)

## 1. 技術定位

- **Django REST Framework (DRF)**用於快速建立 RESTful API，支援序列化、權限、驗證等功能。
- **PostgreSQL**關聯式資料庫，Django 透過 ORM 連接。
- **Clean Architecture**強調分層、依賴反轉，讓商業邏輯與框架、資料庫解耦。
- **CQRS**
  Command/Query 分離，讓讀寫邏輯分開，便於擴展與維護。

---

## 2. 專案資料夾建議結構

```
network/
  ├── domain/         # 純商業邏輯物件與驗證（如 post.py）
  ├── use_cases/      # 用例（如 create_post.py, update_post.py）
  ├── infrastructure/ # ORM models, repository pattern
  ├── interface/      # API 介面（views, serializers）
  ├── urls.py
```

---

## 3. 各層責任

- **domain/**
  - 放純 Python class，描述業務物件（如 PostDomain）及其驗證/規則。
  - 不依賴 Django/ORM。
- **use_cases/**
  - 實作商業流程（如 CreatePostUseCase），調用 domain 驗證與 repository。
- **infrastructure/**
  - Django ORM models、資料存取實作（如 PostRepository）。
- **interface/**
  - API 入口（ViewSet、views）、序列化（serializers），只負責 request/response。
- **urls.py**
  - 路由設定。

---

## 4. 驗證邏輯的分層原則

- **domain 層**：
  - 集中所有「業務規則」與「資料驗證」。
  - 例如：內容不能為空、長度限制、權限檢查。
- **interface 層（ViewSet）**：
  - 只呼叫 domain 驗證，把錯誤轉成 API 格式回傳。
  - 不重複寫驗證。

---

## 5. DRF ViewSet + Router 實作

- ViewSet 是 DRF 的 class-based view，配合 Router 可自動產生 CRUD 路由。
- 適合標準 RESTful API，快速開發。

**範例：**

```python
# domain/post.py
class PostDomain:
    def __init__(self, poster_id, content):
        self.poster_id = poster_id
        self.content = content

    def validate(self):
        if not self.content or len(self.content.strip()) == 0:
            raise ValueError("Content cannot be empty")
        if len(self.content) > 500:
            raise ValueError("Content too long")

# interface/views.py
class PostViewSet(viewsets.ModelViewSet):
    ...
    def perform_create(self, serializer):
        content = self.request.data.get('content', '').strip()
        try:
            PostDomain(self.request.user.id, content).validate()
        except ValueError as e:
            raise serializers.ValidationError(str(e))
        serializer.save(poster=self.request.user)
```

---

## 6. 目前重構重點

- **將商業邏輯/驗證抽到 domain 層，ViewSet 只呼叫 domain 驗證。**
- **用 ViewSet + Router 取代 function-based view，簡化 CRUD API。**
- **資料存取邏輯抽到 repository，use_case 層只調用 repository。**
- **API 層只負責 request/response，保持單一職責。**

---

## 7. 參考資源

- [Django REST Framework 官方文件](https://www.django-rest-framework.org/)
- [DRF ViewSet 官方說明](https://www.django-rest-framework.org/api-guide/viewsets/)
- [Clean Architecture 簡介](https://8thlight.com/blog/uncle-bob/2012/08/13/the-clean-architecture.html)
- [CQRS 簡介](https://martinfowler.com/bliki/CQRS.html)

---

**本文件為重構 Django DRF 專案的分層與實作原則備忘，供未來維護與擴展參考。**
