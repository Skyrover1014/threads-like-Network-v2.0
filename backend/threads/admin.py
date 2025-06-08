
# Register your models here.
# threads/infrastructure/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from threads.models import User

@admin.register(User)
class UserModelAdmin(UserAdmin):
    list_display = ('id', 'username', 'email', 'is_staff')
    search_fields = ('username', 'email')
    readonly_fields = ('date_joined', 'last_login')