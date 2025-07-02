from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from rest_framework.permissions import AllowAny, IsAuthenticated

from threads.repositories import UserRepositoryImpl

from threads.use_cases.commands.register_user import RegisterUser
from threads.use_cases.queries.get_user_profile import GetUserProfile



from .serializers import UserSerializer, RegisterUserSerializer
from threads.common.exceptions import EntityAlreadyExists, EntityOperationFailed, EntityDoesNotExist
from django.db import IntegrityError



class RegisterUserView(APIView):
    permission_classes = [AllowAny]

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
        except EntityAlreadyExists as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except EntityOperationFailed as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message": "User created successfully."}, status=status.HTTP_201_CREATED)
    
class GetUserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        domain_user = GetUserProfile(UserRepositoryImpl()).execute(user_id)
        serializers = UserSerializer(domain_user)
        return Response(serializers.data, status=status.HTTP_200_OK)