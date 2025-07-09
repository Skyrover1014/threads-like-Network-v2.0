from django.urls import path

from .interface.views.users.users_view import UserCreateView
from .interface.views.users.user_view import UserDetailView

from .interface.views.posts.posts_view import PostListCreateView
from .interface.views.posts.post_view import PostDetailView

from .interface.views.comments.post_comments_view import CommentListCreateView
from .interface.views.comments.comment_view  import CommentDetailView
from .interface.views.comments.child_comment_view import ChildCommentListCreateView


from .interface.views.reposts.repost_post_view import RepostPostView
from .interface.views.reposts.repost_comment_view import RepostCommentView
from .interface.views.likes.like_view import LikeContentView

from .interface.util.ask_gpt import AskGPTView

urlpatterns = [
    path('users/', UserCreateView.as_view(), name='user_register'),
    path('users/<int:user_id>/', UserDetailView.as_view(), name='user_profile'),
    
    # posts 列表跟新增
    path('posts/', PostListCreateView.as_view(), name="posts_list_create"),
    
    # post 基本CRUD
    path('posts/<int:post_id>', PostDetailView.as_view(), name="post_edit_delete"),

    # comments列表跟新增
    path('posts/<int:post_id>/comments',CommentListCreateView.as_view(), name="post_comments_list_create"),
    
    # comment 基本CRUD
    path('comments/<int:comment_id>', CommentDetailView.as_view(), name="comment_edit_delete"),

    # child comments列表跟新增
    path('comments/<int:comment_id>/child_comments', ChildCommentListCreateView.as_view(), name="create_child_comment"),

    # content 轉發
    path('posts/<int:post_id>/repost', RepostPostView.as_view(), name="post_repost"),
    path('comments/<int:comment_id>/repost', RepostCommentView.as_view(), name="comment_repost"),

    # content 按讚與取消
    path('posts/<int:content_id>/like',LikeContentView.as_view(), {"content_type": "post"}),
    path('comments/<int:content_id>/like', LikeContentView.as_view(), {"content_type": "comment"}),

    path('gpt/', AskGPTView.as_view(), name="test_api")
]