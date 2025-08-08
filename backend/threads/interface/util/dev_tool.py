from django.conf import settings

if settings.DEBUG:
    from drf_spectacular.utils import (
        extend_schema,
        extend_schema_view,
        OpenApiResponse,
        OpenApiExample,
        OpenApiRequest
    )
else:
    def extend_schema_view(**kwargs): return lambda cls: cls
    def extend_schema(**kwargs): return lambda obj: obj
    OpenApiResponse = lambda *args, **kwargs: None
    OpenApiExample = lambda *args, **kwargs: None
    OpenApiRequest = lambda *args, **kwargs: None