from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .user_baseView import UserBaseView
from ...serializers.user_serializer import RegisterUserSerializer

from threads.infrastructure.repository.user_repository import UserRepositoryImpl
from threads.use_cases.commands.register_user import RegisterUser
    

class UserCreateView(UserBaseView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = RegisterUser(UserRepositoryImpl()).execute(username, email, password)
        except Exception as e:
            return self._handler_exception(e)
        
        return Response({"message": "User created successfully."}, status=status.HTTP_201_CREATED)
    
    