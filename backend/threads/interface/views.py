from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from rest_framework.permissions import AllowAny, IsAuthenticated

from threads.repositories import UserRepositoryImpl, PostRepositoryImpl, CommentRepositoryImpl, LikeRepositoryImpl

from threads.use_cases.commands.register_user import RegisterUser
from threads.use_cases.queries.get_user_profile import GetUserProfile
from threads.use_cases.queries.get_all_posts import GetAllPost
from threads.use_cases.queries.get_profile_posts import GetProfilePost
from threads.use_cases.queries.get_following_user_ids import GetFollowingUserIds
from threads.use_cases.queries.get_followings_posts import GetFollowingsPost
from threads.use_cases.commands.create_post import CreatePost
from threads.use_cases.queries.get_post_by_id import GetPostById
from threads.use_cases.commands.update_post import UpdatePost
from threads.use_cases.commands.delete_post import DeletePost
from threads.use_cases.commands.repost_content import CreateRePost
from threads.use_cases.commands.create_like import CreateLike
from threads.use_cases.commands.delete_like import DeleteLike
from threads.use_cases.queries.get_like_by_id import GetLikeById
from threads.use_cases.queries.get_comment_by_id import GetCommentById


from .serializers import UserSerializer, RegisterUserSerializer, LikeSerializer
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


class LikeContentView(APIView):
    permission_classes=[IsAuthenticated]

    def get (self, request, content_id,content_type):

        user_id = request.user.id
        try:
            domain_like = GetLikeById(LikeRepositoryImpl()).execute(user_id, content_id, content_type)
        except EntityDoesNotExist as e:
            return Response({'error':str(e)}, status=status.HTTP_404_NOT_FOUND)
        except EntityOperationFailed as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        serializers = LikeSerializer(domain_like)
        return Response(serializers.data, status=status.HTTP_200_OK)
        

    def post(self, request, content_id, content_type):
       
        data = {
            'user_id': request.user.id,
            'content_item_id': content_id,
            'content_type': content_type
        }

        serializers = LikeSerializer(data=data)
        serializers.is_valid(raise_exception=True)

        user_id = serializers.validated_data['user_id']
        content_id = serializers.validated_data['content_item_id']
        content_type = serializers.validated_data['content_type']

        try:
            like = CreateLike(LikeRepositoryImpl()).execute(user_id, content_id, content_type)
        except EntityDoesNotExist as e:
            return Response({'error':str(e)}, status=status.HTTP_404_NOT_FOUND) 
        except EntityOperationFailed as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except EntityAlreadyExists as e:
            return Response({'error':str(e)}, status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response({"message": "Liked Successfully"}, status=status.HTTP_201_CREATED)
    
    def delete (self, request, content_id, content_type):

        user_id = request.user.id
        try:
            domain_like = GetLikeById(LikeRepositoryImpl()).execute(user_id, content_id, content_type)
        except EntityDoesNotExist as e:
            return Response({'error':str(e)}, status=status.HTTP_404_NOT_FOUND)
        except EntityOperationFailed as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try: 
            domain_like.verify_deletable_by(request.user.id)
        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        try:
            delete_lke = DeleteLike(LikeRepositoryImpl()).execute(domain_like)
        except EntityDoesNotExist as e:
           return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except EntityOperationFailed as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"message":"Like deleted successfully"},status=status.HTTP_204_NO_CONTENT)
 
        