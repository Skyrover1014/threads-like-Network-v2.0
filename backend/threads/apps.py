from django.apps import AppConfig


class ThreadsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'threads'

    def ready(self):
        # noqa: F401
        import threads.infrastructure.signals 
        print("NetworkConfig.ready() called, signals loaded!")