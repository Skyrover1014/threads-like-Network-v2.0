from django.urls import path
from .interface.views import RegisterUserView, GetUserProfileView

urlpatterns = [
    path('register/', RegisterUserView.as_view(), name='register'),
    path('profile/<int:user_id>/', GetUserProfileView.as_view(), name='profile'),
]