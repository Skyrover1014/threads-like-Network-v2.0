from rest_framework import serializers
from threads.domain.entities import User as DomainUser
from threads.domain.entities import Post as DomainPost

class UserSerializer(serializers.Serializer):
   id = serializers.IntegerField()
   username = serializers.CharField()
   email = serializers.EmailField()
   

class RegisterUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)
    confirmation = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password'] != data['confirmation']:
            raise serializers.ValidationError("Password and confirmation do not match.")
        return data
    

class PostSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    author_id = serializers.IntegerField()
    content = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%dT%H:%M:%S")    
    updated_at = serializers.DateTimeField(read_only=True, format="%Y-%m-%dT%H:%M:%S")

    likes_count = serializers.IntegerField()
    comments_count = serializers.IntegerField()
    reposts_count = serializers.IntegerField()

    is_like = serializers.BooleanField()
    is_repost = serializers.BooleanField()
    repost_of = serializers.IntegerField()
    repost_of_content_type = serializers.ChoiceField(
        choices=[('post','post'),('comment','comment')],
        allow_null = True,
        required = False,
    )

class CreatePostSerializer(serializers.Serializer):
    author_id = serializers.IntegerField()
    content = serializers.CharField()
