from rest_framework import serializers
from backend.threads.domain.entities import User as DomainUser

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = DomainUser
        fields = ['id', 'username', 'email', 'created_at', 'updated_at']
