from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny


from .user_baseView import UserBaseView
from ...serializers.user_serializer import UserSerializer, RegisterUserSerializer


from threads.infrastructure.repository.user_repository import UserRepositoryImpl

from threads.use_cases.commands.register_user import RegisterUser
from threads.use_cases.queries.get_user_profile import GetUserProfile




class UserDetailView(UserBaseView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        domain_user = GetUserProfile(UserRepositoryImpl()).execute(user_id)
        serializers = UserSerializer(domain_user)
        return Response(serializers.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        if not serializer.is_valid():
            error_msgs = []
            for field, msgs in serializer.errors.items():
                error_msgs.extend(msgs)
            return Response({'error': error_msgs}, status=status.HTTP_400_BAD_REQUEST)

        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        register_user = RegisterUser(UserRepositoryImpl())
        try:
            user = register_user.execute(username, email, password)
        except Exception as e:
            return self._handler_exception(e)
        return Response({"message": "User created successfully."}, status=status.HTTP_201_CREATED)
    
    