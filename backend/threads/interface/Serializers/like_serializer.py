from rest_framework import serializers


class LikeSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    content_item_id = serializers.IntegerField()
    content_type = serializers.ChoiceField(
        choices=[('post','post'),('comment','comment')],
        allow_null = False,
        required = True
    )