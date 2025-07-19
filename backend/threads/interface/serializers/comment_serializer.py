from rest_framework import serializers
from threads.domain.enum import ContentTypeEnum

class CommentSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    author_id = serializers.IntegerField()
    author_name = serializers.CharField()
    content = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%dT%H:%M:%S")    
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%dT%H:%M:%S")

    likes_count = serializers.IntegerField()
    comments_count = serializers.IntegerField()
    reposts_count = serializers.IntegerField()

    is_liked = serializers.BooleanField()
    is_repost = serializers.BooleanField()
    repost_of = serializers.IntegerField(allow_null = True, required = False)
    repost_of_content_type = serializers.ChoiceField(
        choices=ContentTypeEnum,
        allow_null = True,
        required = False,
    )
    parent_post_id = serializers.IntegerField()
    parent_comment_id = serializers.IntegerField(allow_null = True, required = False)



class CreateCommentSerializer(serializers.Serializer):
    author_id = serializers.IntegerField()
    content = serializers.CharField()

class CreateChildCommentSerializer(serializers.Serializer):
    author_id = serializers.IntegerField()
    content = serializers.CharField()
    parent_post_id = serializers.IntegerField()