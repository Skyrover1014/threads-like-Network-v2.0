from rest_framework import serializers


class UserSerializer(serializers.Serializer):
   id = serializers.IntegerField()
   username = serializers.CharField()
   email = serializers.EmailField()
   

class RegisterUserSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.CharField()
    password = serializers.CharField(write_only=True)
    confirmation = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['password'] != data['confirmation']:
            raise serializers.ValidationError("Password and confirmation do not match.")
        return data