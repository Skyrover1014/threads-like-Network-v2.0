from django.urls import path
from .interface.views import RegisterUserView, GetUserProfileView
from .interface.views import GetAllPostView, CreateNewPostView, EditPostView, DeletePostView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('profile/<int:user_id>/', GetUserProfileView.as_view(), name='profile'),
    path('posts/<int:auth_user_id>/<int:offset>/<int:limit>', GetAllPostView.as_view(), name='all_posts'),
    path('new_post/', CreateNewPostView.as_view(), name='create_post'),
    path('post/<int:post_id>', EditPostView.as_view(),name="edit_post"),
    path('post/delete/<int:post_id>', DeletePostView.as_view(), name="delete_post")
]