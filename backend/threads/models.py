from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db.models import Q
# Create your models here.
class User(AbstractUser):
    username = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    hashed_password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    followers_count = models.PositiveIntegerField(default=0)
    followings_count = models.PositiveIntegerField(default=0)
    posts_count = models.PositiveIntegerField(default=0) 

    def __str__(self):
        return self.username
    
    class Meta:
        db_table = 'app_user'
        ordering = ['-created_at']

class Follow(models.Model):
    follower = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followings')
    following = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'app_follow'
        ordering = ['-created_at']
        unique_together = ('follower', 'following')
        indexes = [
            models.Index(fields=['follower', 'following']),
        ]



class ContentItem(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    

    likes_count = models.PositiveIntegerField(default=0)
    comments_count = models.PositiveIntegerField(default=0)
    reposts_count = models.PositiveIntegerField(default=0)

    is_repost = models.BooleanField(default=False)

    class Meta:
        abstract = True 
        db_table = 'app_content_item'
        ordering = ['-created_at']


CONTENT_TYPE_LIMIT = (
    Q(app_label='threads', model='post') |
    Q(app_label='threads', model='comment')
)


class Post(ContentItem):
    repost_of_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, limit_choices_to=CONTENT_TYPE_LIMIT)
    repost_of_content_item_id = models.PositiveIntegerField(null=True, blank=True)
    repost_of_content_object = GenericForeignKey('repost_of_content_type', 'repost_of_content_item_id')
    class Meta:
        db_table = 'app_post'
        ordering = ['-created_at']
        indexes =[
            models.Index(fields=['repost_of_content_type','repost_of_content_item_id'])
        ]
class Comment(ContentItem):
    repost_of_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, limit_choices_to=CONTENT_TYPE_LIMIT)
    repost_of_content_item_id = models.PositiveIntegerField(null=True, blank=True)
    repost_of_content_object = GenericForeignKey('repost_of_content_type', 'repost_of_content_item_id')

    parent_post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='post_comments')
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='comment_comments')

    class Meta:
        db_table = 'app_comment'
        ordering = ['-created_at']
        indexes =[
            models.Index(fields=['repost_of_content_type','repost_of_content_item_id'])
        ]



class LikePost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='like_post_counts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'app_like'
        ordering = ['-created_at']
        unique_together = ('user', 'post') 

class LikeComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes_comments')
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='like_comment_counts')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'app_like_comment'
        ordering = ['-created_at']
        unique_together = ('user', 'comment') 
         