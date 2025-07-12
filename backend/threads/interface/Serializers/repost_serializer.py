from rest_framework import serializers
from threads.domain.enum import ContentTypeEnum


class RepostSerializer(serializers.Serializer):
    author_id = serializers.IntegerField()
    content = serializers.CharField()
    target_type = serializers.ChoiceField(
        # choices=[('post','post'),('comment','comment')],
        choices=ContentTypeEnum
    )
    target_post = serializers.IntegerField(allow_null=True, required = False)
    target_comment = serializers.IntegerField(allow_null=True, required = False)


class RepostResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    repost = serializers.DictField()     # 用 DictField 接任何 serializer 的輸出
    original = serializers.DictField()