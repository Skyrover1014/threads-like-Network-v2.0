
from rest_framework import serializers
from threads.models import Post

class PostModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = [
            'id', 'author', 'content', 'created_at', 'updated_at',
            'likes_count', 'comments_count', 'reposts_count',
            'is_repost', 'repost_of_content_type', 'repost_of_content_item_id'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'likes_count', 'comments_count', 'reposts_count']