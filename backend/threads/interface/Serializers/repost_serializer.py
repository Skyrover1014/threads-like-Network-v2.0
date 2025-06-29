from rest_framework import serializers

class RepostSerializer(serializers.Serializer):
    author_id = serializers.IntegerField()
    content = serializers.CharField()
    target_type = serializers.ChoiceField(
        choices=[('post','post'),('comment','comment')]
    )
    target_post = serializers.IntegerField(allow_null=True, required = False)
    target_comment = serializers.IntegerField(allow_null=True, required = False)