from rest_framework import serializers
from threads.domain.enum import ContentTypeEnum
class PostSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    author_id = serializers.IntegerField()
    # author_name = serializers.CharField()
    content = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%dT%H:%M:%S")    
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%dT%H:%M:%S")

    likes_count = serializers.IntegerField()
    comments_count = serializers.IntegerField()
    reposts_count = serializers.IntegerField()

    is_liked = serializers.BooleanField()
    is_repost = serializers.BooleanField()
    repost_of = serializers.IntegerField()
    # repost_of_content_type = serializers.ChoiceField(
    #     choices=ContentTypeEnum,
    #     allow_null = True,
    #     required = False,
    # )
    repost_of_content_type = serializers.SerializerMethodField()

    def get_repost_of_content_type(self, obj):
        mapping = {
            4: "post",     # 假設 ContentType id=4 對應 post
            2: "comment"   # 假設 ContentType id=2 對應 comment
        }
        return mapping.get(obj.repost_of_content_type, None)

class CreatePostSerializer(serializers.Serializer):
    author_id = serializers.IntegerField()
    author_name = serializers.CharField()  # ✅ 新增這行
    content = serializers.CharField()