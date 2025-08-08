from django.db.models.signals import post_save, post_delete, m2m_changed
from django.dispatch import receiver
from threads.models import Comment,Post
from threads.infrastructure.cache import redis_client
from threads.tasks import flush_comment_counts, flush_repost_counts
import threading
from django.db import transaction

import logging
logger = logging.getLogger(__name__)
_thread_locals = threading.local()

def _ensure_flush_scheduled():
    """同一交易僅排程一次 Celery 任務"""
    if not getattr(_thread_locals, "flush_scheduled", False):
        transaction.on_commit(lambda: flush_comment_counts.delay())
        _thread_locals.flush_scheduled = True


@receiver(post_save, sender=Comment)
def increment_comment_count(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.parent_post_id:
        post_key = f"post:{instance.parent_post_id}"
        logger.info(f"[Signal] 新增留言，post:{instance.parent_post_id}")
        redis_client.hincrby(post_key, "comments_count", 1)

    if instance.parent_comment_id:
        comment_key = f"comment:{instance.parent_comment_id}"
        logger.info(f"[Signal] 新增子留言，comment:{instance.parent_comment_id}")
        redis_client.hincrby(comment_key, "comments_count", 1)
        
    _ensure_flush_scheduled()

@receiver(post_delete, sender=Comment)
def decrement_comment_count(sender, instance, **kwargs):
    if instance.parent_post_id:
        key = f"post:{instance.parent_post_id}"
        logger.info(f"[Signal] 刪除留言，post:{instance.parent_post_id}")
        redis_client.hincrby(key, "comments_count", -1)

    if instance.parent_comment_id:
        comment_key = f"comment:{instance.parent_comment_id}"
        logger.info(f"[Signal] 刪除子留言，comment:{instance.parent_comment_id}")
        redis_client.hincrby(comment_key, "comments_count", -1)
    
    _ensure_flush_scheduled()


@receiver(post_save, sender=Post)
def increment_post_reposts_count(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.is_repost:
        key = f"{instance.repost_of_content_type.model}:{instance.repost_of_content_item_id}"
        redis_client.hincrby(key, "reposts_count", 1)
    flush_repost_counts.delay()

@receiver(post_save, sender=Comment)
def increment_comment_reposts_count(sender, instance, created, **kwargs):
    if not created:
        return
    if instance.is_repost:
        key = f"{instance.repost_of_content_type.model}:{instance.repost_of_content_item_id}"
        redis_client.hincrby(key, "reposts_count", 1)
    flush_repost_counts.delay()

@receiver(post_delete, sender=Post)
def decrement_post_reposts_count(sender, instance, **kwargs):
    if instance.is_repost:
        key = f"{instance.repost_of_content_type.model}:{instance.repost_of_content_item_id}"
        redis_client.hincrby(key, "reposts_count", -1)
    flush_repost_counts.delay()

@receiver(post_delete, sender=Comment)
def decrement_comment_reposts_count(sender, instance, **kwargs):
    if instance.is_repost:
        key = f"{instance.repost_of_content_type.model}:{instance.repost_of_content_item_id}"
        redis_client.hincrby(key, "reposts_count", -1)
    flush_repost_counts.delay()