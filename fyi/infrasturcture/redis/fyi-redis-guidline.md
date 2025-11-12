# Redis 實作指南

## 🎯 Redis 核心用途

### 1. **記憶體資料庫**
Redis 是一個開源的記憶體資料結構儲存系統，主要用於快取、會話管理和即時資料處理。

**核心特性**：
- **高性能**: 基於記憶體操作，速度極快
- **資料結構豐富**: 支援字串、列表、集合、有序集合、雜湊等
- **持久化**: 支援 RDB 和 AOF 兩種持久化方式
- **分散式**: 支援主從複製和叢集模式

### 2. **主要使用場景**
```python
# 快取
redis_client.setex("user:123", 300, json.dumps(user_data))

# 計數器
redis_client.incr("post:456:likes")

# 會話管理
redis_client.setex(f"session:{session_id}", 3600, user_id)

# 限流
redis_client.incr(f"rate_limit:{user_id}:api")
```

## 🔄 與訂閱者模式的關係

### **Redis Pub/Sub 實現訂閱者模式**

#### 1. **發布-訂閱機制**
```python
# 發布者（Publisher）
def publish_post_created(post_id, author_id):
    message = {
        "event": "post_created",
        "post_id": post_id,
        "author_id": author_id,
        "timestamp": datetime.now().isoformat()
    }
    redis_client.publish("post_events", json.dumps(message))

# 訂閱者（Subscriber）
def subscribe_to_post_events():
    pubsub = redis_client.pubsub()
    pubsub.subscribe("post_events")
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            data = json.loads(message['data'])
            handle_post_event(data)

def handle_post_event(data):
    if data['event'] == 'post_created':
        # 通知關注者
        notify_followers(data['author_id'], data['post_id'])
        # 更新推薦系統
        update_recommendations(data['post_id'])
        # 更新搜尋索引
        update_search_index(data['post_id'])
```

#### 2. **多頻道訂閱**
```python
# 訂閱多個事件頻道
def subscribe_to_multiple_channels():
    pubsub = redis_client.pubsub()
    pubsub.subscribe("post_events", "user_events", "comment_events")
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            channel = message['channel'].decode()
            data = json.loads(message['data'])
            
            if channel == "post_events":
                handle_post_event(data)
            elif channel == "user_events":
                handle_user_event(data)
            elif channel == "comment_events":
                handle_comment_event(data)
```

## 🚀 在 Threads 專案中的實作建議

### **第一階段：基礎快取策略**

#### 1. **用戶資料快取**
```python
# cache.py
class UserCache:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.cache_ttl = 300  # 5分鐘
    
    def get_user(self, user_id):
        cache_key = f"user:{user_id}"
        cached_data = self.redis.get(cache_key)
        
        if cached_data:
            return json.loads(cached_data)
        
        # 從資料庫查詢
        user = User.objects.get(id=user_id)
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "followers_count": user.followers_count,
            "followings_count": user.followings_count,
            "posts_count": user.posts_count
        }
        
        # 快取資料
        self.redis.setex(cache_key, self.cache_ttl, json.dumps(user_data))
        return user_data
    
    def invalidate_user(self, user_id):
        cache_key = f"user:{user_id}"
        self.redis.delete(cache_key)
```

#### 2. **貼文列表快取**
```python
class PostCache:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.cache_ttl = 60  # 1分鐘
    
    def get_hot_posts(self, user_id, limit=20):
        cache_key = f"hot_posts:{user_id}:{limit}"
        cached_posts = self.redis.get(cache_key)
        
        if cached_posts:
            return json.loads(cached_posts)
        
        # 從資料庫查詢熱門貼文
        posts = Post.objects.filter(
            created_at__gte=timezone.now() - timedelta(days=7)
        ).order_by('-likes_count')[:limit]
        
        posts_data = [self._serialize_post(post) for post in posts]
        
        # 快取資料
        self.redis.setex(cache_key, self.cache_ttl, json.dumps(posts_data))
        return posts_data
    
    def invalidate_hot_posts(self):
        # 清除所有熱門貼文快取
        for key in self.redis.scan_iter(match="hot_posts:*"):
            self.redis.delete(key)
```

### **第二階段：即時功能實現**

#### 1. **即時計數器**
```python
class RealTimeCounters:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def increment_likes(self, content_id, content_type):
        key = f"{content_type}:{content_id}:likes"
        self.redis.incr(key)
        
        # 發布事件
        self.publish_counter_update(content_id, content_type, "likes")
    
    def decrement_likes(self, content_id, content_type):
        key = f"{content_type}:{content_id}:likes"
        self.redis.decr(key)
        
        # 發布事件
        self.publish_counter_update(content_id, content_type, "likes")
    
    def publish_counter_update(self, content_id, content_type, counter_type):
        message = {
            "event": "counter_update",
            "content_id": content_id,
            "content_type": content_type,
            "counter_type": counter_type,
            "value": self.redis.get(f"{content_type}:{content_id}:{counter_type}")
        }
        self.redis.publish("counter_events", json.dumps(message))
```

#### 2. **線上用戶追蹤**
```python
class OnlineUsersTracker:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def user_online(self, user_id):
        # 使用有序集合追蹤線上用戶
        self.redis.zadd("online_users", {user_id: time.time()})
        
        # 發布用戶上線事件
        self.publish_user_status(user_id, "online")
    
    def user_offline(self, user_id):
        # 移除線上用戶
        self.redis.zrem("online_users", user_id)
        
        # 發布用戶下線事件
        self.publish_user_status(user_id, "offline")
    
    def get_online_users(self, limit=100):
        # 獲取最近活躍的用戶
        now = time.time()
        online_users = self.redis.zrevrangebyscore(
            "online_users", now, now - 300, 0, limit
        )
        return [int(user_id) for user_id in online_users]
    
    def publish_user_status(self, user_id, status):
        message = {
            "event": "user_status_change",
            "user_id": user_id,
            "status": status,
            "timestamp": time.time()
        }
        self.redis.publish("user_events", json.dumps(message))
```

### **第三階段：進階功能**

#### 1. **API 限流**
```python
class RateLimiter:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def is_allowed(self, user_id, endpoint, limit=100, window=3600):
        key = f"rate_limit:{user_id}:{endpoint}"
        current = self.redis.incr(key)
        
        if current == 1:
            self.redis.expire(key, window)
        
        return current <= limit
    
    def get_remaining_requests(self, user_id, endpoint, limit=100):
        key = f"rate_limit:{user_id}:{endpoint}"
        current = int(self.redis.get(key) or 0)
        return max(0, limit - current)
```

#### 2. **分散式鎖**
```python
class DistributedLock:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def acquire_lock(self, lock_name, timeout=10):
        identifier = str(uuid.uuid4())
        end = time.time() + timeout
        
        while time.time() < end:
            if self.redis.set(f"lock:{lock_name}", identifier, nx=True, ex=timeout):
                return identifier
            time.sleep(0.001)
        
        return False
    
    def release_lock(self, lock_name, identifier):
        pipe = self.redis.pipeline(True)
        
        while True:
            try:
                pipe.watch(f"lock:{lock_name}")
                if pipe.get(f"lock:{lock_name}") == identifier:
                    pipe.multi()
                    pipe.delete(f"lock:{lock_name}")
                    pipe.execute()
                    return True
                pipe.unwatch()
                break
            except redis.WatchError:
                pass
        
        return False
```

## ⚙️ Redis 配置建議

### **Docker Compose 配置**
```yaml
# docker-compose.yml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru

volumes:
  redis_data:
```

### **Django 設定**
```python
# settings.py
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Redis 連接池
import redis
from django.conf import settings

redis_pool = redis.ConnectionPool.from_url(settings.REDIS_URL)
redis_client = redis.Redis(connection_pool=redis_pool)
```

### **快取配置**
```python
# settings.py
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': REDIS_URL,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# 會話儲存
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
```

## 📊 監控和維護

### **Redis 監控**
```python
class RedisMonitor:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def get_memory_usage(self):
        info = self.redis.info('memory')
        return {
            'used_memory': info['used_memory'],
            'used_memory_human': info['used_memory_human'],
            'maxmemory': info.get('maxmemory', 0)
        }
    
    def get_key_count(self):
        return self.redis.dbsize()
    
    def get_slow_queries(self):
        return self.redis.slowlog_get(10)
    
    def clear_expired_keys(self):
        return self.redis.execute_command('MEMORY', 'PURGE')
```

### **快取統計**
```python
class CacheStats:
    def __init__(self, redis_client):
        self.redis = redis_client
    
    def get_hit_rate(self):
        info = self.redis.info('stats')
        hits = info['keyspace_hits']
        misses = info['keyspace_misses']
        total = hits + misses
        
        if total == 0:
            return 0
        
        return hits / total
    
    def get_top_keys(self, pattern="*", limit=10):
        keys = []
        for key in self.redis.scan_iter(match=pattern):
            ttl = self.redis.ttl(key)
            keys.append({
                'key': key.decode(),
                'ttl': ttl,
                'type': self.redis.type(key).decode()
            })
        
        return sorted(keys, key=lambda x: x['ttl'], reverse=True)[:limit]
```

## 🎯 最佳實踐

### **1. 快取策略**
- **Cache-Aside**: 應用程式負責快取管理
- **Write-Through**: 同時寫入快取和資料庫
- **Write-Behind**: 先寫快取，後寫資料庫

### **2. 記憶體管理**
- 設定適當的 `maxmemory` 限制
- 使用 `allkeys-lru` 或 `volatile-lru` 策略
- 定期監控記憶體使用情況

### **3. 資料一致性**
- 使用分散式鎖確保原子操作
- 實現快取失效策略
- 使用版本號處理並發更新

### **4. 效能優化**
- 使用 Pipeline 批量操作
- 避免大鍵值對
- 合理設定過期時間

### **5. 安全考量**
- 設定密碼認證
- 限制網路訪問
- 定期備份重要資料
