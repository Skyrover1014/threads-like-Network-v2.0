import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
app = Celery('core')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


# Beat 排程：每分鐘執行一次 flush_comment_counts
app.conf.beat_schedule = {
    # "flush-comment-counts-every-minute": {
    #     "task": "threads.tasks.flush_comment_counts",
    #     "schedule": 10000.0,
    # },
}


