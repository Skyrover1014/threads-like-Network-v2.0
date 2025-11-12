# Celery 實作指南

## 🎯 Celery 核心用途

### 1. **非同步任務處理**
Celery 是一個分散式任務佇列，主要用於處理耗時的操作，避免阻塞主要的 Web 請求流程。

**核心概念**：
- **Producer（生產者）**: 發送任務到佇列
- **Broker（代理）**: 儲存任務的訊息佇列（如 Redis、RabbitMQ）
- **Worker（工作者）**: 執行任務的進程
- **Result Backend（結果後端）**: 儲存任務執行結果

### 2. **分散式系統架構**
```python
# 任務定義
@shared_task
def process_large_data(data):
    # 耗時操作
    return processed_data

# 任務調用
task = process_large_data.delay(data)
result = task.get()  # 同步等待結果
```

## 🔄 與訂閱者模式的關係

### **訂閱者模式在 Celery 中的體現**

#### 1. **事件驅動架構**
```python
# 事件發布者（Producer）
@shared_task
def publish_user_registered_event(user_id):
    # 發布用戶註冊事件
    send_task('notify_followers', args=[user_id])
    send_task('send_welcome_email', args=[user_id])
    send_task('update_recommendations', args=[user_id])

# 事件訂閱者（Subscribers）
@shared_task
def notify_followers(user_id):
    # 通知關注者
    pass

@shared_task
def send_welcome_email(user_id):
    # 發送歡迎郵件
    pass
```

#### 2. **多訂閱者模式**
```python
# 一個事件觸發多個訂閱者
@shared_task
def post_created_event(post_id):
    # 發布貼文創建事件
    chain(
        update_user_stats.s(post_id),
        notify_followers.s(post_id),
        update_search_index.s(post_id),
        generate_recommendations.s(post_id)
    ).apply_async()
```

## 🚀 在 Threads 專案中的實作建議

### **第一階段：基礎任務處理**

#### 1. **AI 事實查核非同步化**
```python
# tasks.py
@shared_task(bind=True, max_retries=3)
def fact_check_content(self, content_id, content_type, content_text):
    try:
        # 調用 OpenAI API
        result = openai_client.fact_check(content_text)
        
        # 更新資料庫
        update_fact_check_result(content_id, result)
        
        # 發送通知
        notify_fact_check_complete.delay(content_id, result)
        
    except Exception as exc:
        # 重試機制
        raise self.retry(exc=exc, countdown=60)

# views.py
def fact_check_post(request, post_id):
    post = get_post(post_id)
    fact_check_content.delay(post_id, "post", post.content)
    return Response({"message": "事實查核已開始處理"})
```

#### 2. **計數器批量更新**
```python
@shared_task
def batch_update_counters():
    """定期批量更新計數器"""
    # 更新評論計數
    for key in redis_client.scan_iter(match="post:*"):
        post_id = key.decode().split(":", 1)[1]
        delta = int(redis_client.hget(key, "comments_count") or 0)
        if delta:
            Post.objects.filter(id=post_id).update(
                comments_count=F("comments_count") + delta
            )
            redis_client.hdel(key, "comments_count")
```

### **第二階段：事件驅動架構**

#### 1. **用戶註冊事件**
```python
@shared_task
def user_registered_event(user_id):
    """用戶註冊後觸發的事件鏈"""
    chain(
        send_welcome_email.s(user_id),
        create_default_follows.s(user_id),
        generate_initial_recommendations.s(user_id),
        update_user_statistics.s(user_id)
    ).apply_async()

# 在用戶註冊後調用
def register_user(user_data):
    user = create_user(user_data)
    user_registered_event.delay(user.id)
    return user
```

#### 2. **貼文互動事件**
```python
@shared_task
def post_liked_event(post_id, user_id):
    """貼文被按讚後的事件處理"""
    group(
        update_post_stats.s(post_id),
        notify_post_author.s(post_id, user_id),
        update_user_recommendations.s(user_id),
        log_interaction.s("like", post_id, user_id)
    ).apply_async()
```

### **第三階段：進階功能**

#### 1. **圖片處理管道**
```python
@shared_task
def process_image_pipeline(image_id):
    """圖片處理管道"""
    chain(
        validate_image.s(image_id),
        compress_image.s(image_id),
        generate_thumbnails.s(image_id),
        update_image_metadata.s(image_id),
        notify_processing_complete.s(image_id)
    ).apply_async()
```

#### 2. **搜尋索引更新**
```python
@shared_task
def update_search_index(content_id, content_type):
    """更新搜尋索引"""
    content = get_content(content_id, content_type)
    
    # 更新 Elasticsearch
    es_client.index(
        index="content",
        id=content_id,
        body={
            "content": content.text,
            "author": content.author_name,
            "created_at": content.created_at,
            "type": content_type
        }
    )
```

## ⚙️ Celery 配置建議

### **settings.py 配置**
```python
# Celery 配置
CELERY_BROKER_URL = os.environ.get("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.environ.get("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

# 任務配置
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TIMEZONE = TIME_ZONE
CELERY_ENABLE_UTC = True

# 重試配置
CELERY_TASK_RETRY_DELAY = 60  # 重試間隔
CELERY_TASK_MAX_RETRIES = 3   # 最大重試次數

# 任務路由
CELERY_TASK_ROUTES = {
    'threads.tasks.fact_check_content': {'queue': 'ai_queue'},
    'threads.tasks.process_image': {'queue': 'image_queue'},
    'threads.tasks.*': {'queue': 'default'},
}
```

### **Docker Compose 配置**
```yaml
# docker-compose.yml
services:
  celery-worker:
    build: .
    command: celery -A core worker -l info
    volumes:
      - .:/app
    depends_on:
      - redis
      - postgres
    environment:
      - CELERY_BROKER_URL=redis://redis:6379/0

  celery-beat:
    build: .
    command: celery -A core beat -l info
    volumes:
      - .:/app
    depends_on:
      - redis
```

## 📊 監控和除錯

### **任務監控**
```python
# 任務狀態檢查
def check_task_status(task_id):
    from celery.result import AsyncResult
    result = AsyncResult(task_id)
    return {
        "status": result.status,
        "result": result.result,
        "traceback": result.traceback
    }
```

### **錯誤處理**
```python
@shared_task(bind=True)
def robust_task(self, data):
    try:
        # 任務邏輯
        return process_data(data)
    except Exception as exc:
        # 記錄錯誤
        logger.error(f"Task failed: {exc}")
        # 重試或發送告警
        if self.request.retries < 3:
            raise self.retry(countdown=60)
        else:
            send_alert.delay(f"Task {self.request.id} failed permanently")
```

## 🎯 最佳實踐

1. **任務設計原則**
   - 保持任務小而專注
   - 避免長時間運行的任務
   - 使用適當的重試策略

2. **錯誤處理**
   - 實現完整的錯誤處理機制
   - 使用死信佇列處理失敗任務
   - 記錄詳細的錯誤日誌

3. **效能優化**
   - 使用任務路由分離不同類型的任務
   - 實現任務優先級
   - 監控佇列長度和處理時間

4. **測試策略**
   - 使用 `CELERY_TASK_ALWAYS_EAGER` 進行單元測試
   - 實現整合測試驗證任務流程
   - 使用模擬器測試錯誤情況
