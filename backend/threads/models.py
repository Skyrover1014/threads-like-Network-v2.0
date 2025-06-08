from django.contrib.auth.models import AbstractUser
from django.db import models

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