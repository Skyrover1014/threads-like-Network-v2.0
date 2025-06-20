from django.urls import path
from .interface.views import RegisterUserView, GetUserProfileView
from .interface.views import PostListCreateView, PostDetailView
from .interface.views import RepostView, LikeContentView

urlpatterns = [
    path('users/', RegisterUserView.as_view(), name='user_register'),
    path('users/<int:user_id>/', GetUserProfileView.as_view(), name='user_profile'),
    path('posts/', PostListCreateView.as_view(), name="posts_list_create"),
    path('posts/<int:post_id>', PostDetailView.as_view(), name="post_edit_delete"),
    path('posts/<int:post_id>/repost', RepostView.as_view(), name="post_repost"),
    path('posts/<int:content_id>/like',LikeContentView.as_view(), {"content_type": "post"}),
    path('comments/<int:content_id>/like', LikeContentView.as_view(), {"content_type": "comment"})
]