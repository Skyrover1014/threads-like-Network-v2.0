# core/tasks.py
from celery import shared_task
from django.db.models import F
from threads.infrastructure.cache import redis_client

from celery.utils.log import get_task_logger
logger = get_task_logger(__name__)
from redis.lock import Lock

LOCK_KEY = "lock:flush_comment_counts"

@shared_task
def add(x, y):
    return x + y



@shared_task
def flush_comment_counts():
    from threads.models import Post, Comment

    with redis_client.lock(LOCK_KEY, timeout=10):
    # 找出所有有計數的 post key
        for key in redis_client.scan_iter(match="post:*"):
            logger.info("Flush sees key %s", key)
            post_id = key.decode().split(":", 1)[1]
            delta = int(redis_client.hget(key, "comments_count") or 0)
            if delta:
                Post.objects.filter(id=post_id).update(
                    comments_count=F("comments_count") + delta
                )
                # 重置或刪除計數欄位
                redis_client.hdel(key, "comments_count")
        
        # 處理留言(model Comment)的 comments_count 增量
        for key in redis_client.scan_iter(match="comment:*"):
            logger.info("Flush sees key %s", key)
            comment_id = key.decode().split(":", 1)[1]
            delta = int(redis_client.hget(key, "comments_count") or 0)
            if delta:
                Comment.objects.filter(id=comment_id).update(
                    comments_count=F("comments_count") + delta
                )
                redis_client.hdel(key, "comments_count")

@shared_task
def flush_repost_counts():
    from threads.models import Post, Comment

    with redis_client.lock(LOCK_KEY, timeout=10):
        for key in redis_client.scan_iter(match="post:*"):
            post_id = key.decode().split(":", 1)[1]
            delta = int(redis_client.hget(key, "reposts_count") or 0)
            if delta:
                Post.objects.filter(id=post_id).update(
                    reposts_count = F("reposts_count") + delta
                )
                redis_client.hdel(key, "reposts_count")
        
        for key in redis_client.scan_iter(match="comment:*"):
            comment_id = key.decode().split(":", 1)[1]
            delta = int(redis_client.hget(key, "reposts_count") or 0)
            if delta:
                Comment.objects.filter(id=comment_id).update(
                    reposts_count = F("reposts_count") + delta
                )
                redis_client.hdel(key, "reposts_count")
