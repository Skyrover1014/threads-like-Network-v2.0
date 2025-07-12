from rest_framework import serializers
from threads.domain.enum import ContentTypeEnum


class LikeSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    content_item_id = serializers.IntegerField()
    content_type = serializers.ChoiceField(
        choices=ContentTypeEnum,
        allow_null = False,
        required = True
    )