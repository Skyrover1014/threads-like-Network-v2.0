
# Register your models here.
# threads/infrastructure/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from threads.models import User, Post, Comment, Follow, LikePost, LikeComment

@admin.register(User)
class UserModelAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'is_staff', 'followers_count', 'followings_count', 'posts_count')
    search_fields = ('username', 'email')
    readonly_fields = ('date_joined', 'last_login')

class PostModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'content', 'created_at', 'updated_at', 'likes_count', 'comments_count', 'reposts_count', 'is_repost', 'repost_of_content_type', 'repost_of_content_item_id')
    search_fields = ('author__username',)
    list_filter = ('created_at', 'updated_at')

class CommentModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'content', 'created_at', 'updated_at', 'likes_count', 'comments_count', 'reposts_count', 'is_repost', 'repost_of_content_type', 'repost_of_content_item_id', 'parent_post', 'parent_comment')
    search_fields = ('author__username',)
    list_filter = ('created_at', 'updated_at')

class FollowModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'follower', 'following', 'created_at')
    search_fields = ('follower__username', 'following__username')
    list_filter = ('created_at',)
class LikePostModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post', 'created_at')
    search_fields = ('user', 'post')
    list_filter = ('created_at',)
class LikeCommentModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'comment', 'created_at')
    search_fields = ('user', 'comment')




admin.site.register(Post, PostModelAdmin)
admin.site.register(Comment, CommentModelAdmin)
admin.site.register(Follow, FollowModelAdmin)
admin.site.register(LikePost, LikePostModelAdmin)
admin.site.register(LikeComment, LikeCommentModelAdmin)