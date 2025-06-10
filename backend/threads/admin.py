
# Register your models here.
# threads/infrastructure/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from threads.models import User, Post, Comment

@admin.register(User)
class UserModelAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'is_staff')
    search_fields = ('username', 'email')
    readonly_fields = ('date_joined', 'last_login')

class PostModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'content', 'created_at', 'updated_at', 'likes_count', 'comments_count', 'reposts_count', 'is_repost', 'repost_of_content_type', 'repost_of_content_item_id')
    search_fields = ('author__username', 'content')
    list_filter = ('created_at', 'updated_at')

class CommentModelAdmin(admin.ModelAdmin):
    list_display = ('id', 'author', 'content', 'created_at', 'updated_at', 'likes_count', 'comments_count', 'reposts_count', 'is_repost', 'repost_of_content_type', 'repost_of_content_item_id', 'parent_post', 'parent_comment')
    search_fields = ('author__username', 'content')
    list_filter = ('created_at', 'updated_at')

admin.site.register(Post, PostModelAdmin)
admin.site.register(Comment, CommentModelAdmin)