from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from rest_framework.permissions import AllowAny, IsAuthenticated

from threads.repositories import UserRepositoryImpl, PostRepositoryImpl
from threads.use_cases.commands.register_user import RegisterUser
from threads.use_cases.queries.get_user_profile import GetUserProfile
from threads.use_cases.queries.get_all_posts import GetAllPost
from threads.use_cases.commands.create_post import CreatePost
from threads.use_cases.queries.get_post_by_id import GetPostById
from threads.use_cases.commands.update_post import UpdatePost
from threads.use_cases.commands.delete_post import DeletePost


from .serializers import UserSerializer, RegisterUserSerializer, PostSerializer, CreatePostSerializer
from threads.common.exceptions import EntityAlreadyExists, EntityOperationFailed, EntityDoesNotExist




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
    

class GetAllPostView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, auth_user_id, offset, limit):
        domain_posts = GetAllPost(PostRepositoryImpl()).execute(auth_user_id, offset, limit)
        serializers = PostSerializer(domain_posts, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)
    
class CreateNewPostView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializers = CreatePostSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
       
        author_id = serializers.validated_data["author_id"]
        content = serializers.validated_data["content"]

        create_post = CreatePost(PostRepositoryImpl())

        try:
            post = create_post.execute(author_id,content)
        except ValueError as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except EntityOperationFailed as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except EntityDoesNotExist as e:
            return Response({'error':str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        print(post)
        return Response({"message": "Post created successfully"}, status=status.HTTP_200_OK)


class EditPostView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, post_id):
        old_domain_post = GetPostById(PostRepositoryImpl()).execute(post_id)
        serializers = PostSerializer(old_domain_post, data=request.data, partial = True)
        serializers.is_valid(raise_exception=True)

        data = serializers.validated_data
        old_domain_post.update_content(data.get("content",old_domain_post.content), request.user.id)
        updated = UpdatePost(PostRepositoryImpl()).execute(old_domain_post)
        return Response(PostSerializer(updated).data, status=status.HTTP_200_OK)


class DeletePostView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, post_id):
        target_domain_post = GetPostById(PostRepositoryImpl()).execute(post_id)
        target_domain_post.verify_deletable_by(request.user.id)

        DeletePost(PostRepositoryImpl()).execute(target_domain_post)

        return Response({"message":"Post deleted successfully"},status=status.HTTP_204_NO_CONTENT)

        