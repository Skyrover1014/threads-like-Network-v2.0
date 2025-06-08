# Django REST Framework（DRF）深度結構與應用總結

## 1. DRF 的影響範疇
- **API 建立與維護**：快速建立 RESTful API，支援前後端分離。
- **資料序列化**：將 Django model instance 轉換成 JSON 等格式，或反序列化。
- **認證與授權**：多種認證（Session、Token、OAuth），可自訂權限。
- **瀏覽器友善 API 介面**：內建可互動的 API 瀏覽器。
- **高度擴充性**：所有元件都可自訂，適合複雜專案。
- **生態系豐富**：大量第三方套件支援進階需求。

## 2. DRF 可實作的功能
- CRUD API（Create/Read/Update/Delete）
- 認證與授權（登入、API 金鑰、OAuth2、角色權限）
- 檔案上傳/下載（支援 base64 編碼）
- 分頁、排序、過濾（自動化，支援 query string）
- 巢狀資源（Nested Resources）
- 自訂 API 輸出格式
- API 文件自動生成（Swagger/OpenAPI）
- 異步任務觸發（與 Celery 等整合）
- 多語系支援
- API 測試與模擬

## 3. 你現有程式碼與 DRF 功能對照

| 你現在的 function         | DRF 對應做法                | 建議 |
|--------------------------|-----------------------------|------|
| create_post, update_post | ViewSet + Serializer        | ✅   |
| load_post                | ViewSet + 分頁/過濾/排序    | ✅   |
| like_post                | ViewSet + @action           | ✅   |
| profile                  | ViewSet/Serializer          | ✅   |
| follow                   | ViewSet + @action           | ✅   |
| change_profile_image     | Serializer + FileField      | ✅   |
| register, login, logout  | APIView 或第三方套件        | ✅   |
| require_method, parse_json| DRF 內建自動處理           | ✅   |

- 你目前大多數功能都可以用 DRF 實作，且會更簡潔、彈性更高。
- 分頁、排序、過濾等功能，DRF 只需簡單設定即可自動化，無需手動寫邏輯。
- 認證與授權可用 DRF 內建 permission_classes，或自訂權限類別。
- 註冊、登入、登出可用第三方套件（如 djoser、dj-rest-auth）。
- 上傳檔案可用 Serializer 的 FileField 處理。

## 4. DRF 實作範例（以 Post 為例）
```python
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.pagination import PageNumberPagination

class PostPagination(PageNumberPagination):
    page_size = 10

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    pagination_class = PostPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['poster']
    ordering_fields = ['created_time']
```
這樣即可自動支援分頁、排序、過濾。

## 5. 結論
- DRF 幾乎涵蓋現代 Web API 所需所有功能。
- 用 DRF 可大幅簡化程式碼、提升維護性與彈性。
- 建議逐步將現有 API 遷移到 DRF 標準做法。

---
如需針對某個功能的 DRF 實作範例，請隨時提出！ 