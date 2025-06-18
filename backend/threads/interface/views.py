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
from threads.use_cases.queries.get_profile_posts import GetProfilePost
from threads.use_cases.queries.get_following_user_ids import GetFollowingUserIds
from threads.use_cases.queries.get_followings_posts import GetFollowingsPost
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
    
class PostListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        auth_user_id = request.query_params.get("auth_user_id")
        author_id = request.query_params.get("author_id")
        following = request.query_params.get("following") == "true"
        offset = int(request.query_params.get("offset", 0))
        limit = int(request.query_params.get("limit", 10))
        
        repo = PostRepositoryImpl()

        if author_id:
            try:
                domain_posts = GetProfilePost(repo).execute(auth_user_id, author_id, offset, limit)
            except EntityDoesNotExist as e:
                return Response({'error':str(e)}, status=status.HTTP_404_NOT_FOUND)
            except EntityOperationFailed as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        elif following:
            try:
                following_ids = GetFollowingUserIds(UserRepositoryImpl()).execute(auth_user_id)
            except EntityDoesNotExist as e:
                return Response({'error':str(e)}, status=status.HTTP_404_NOT_FOUND)
            except EntityOperationFailed as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            try:
                domain_posts = GetFollowingsPost(repo).execute(auth_user_id, following_ids, offset, limit)
            except EntityDoesNotExist as e:
                return Response({'error':str(e)}, status=status.HTTP_404_NOT_FOUND)
            except EntityOperationFailed as e:
                return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            try:
                domain_posts = GetAllPost(repo).execute(auth_user_id, offset, limit)
            except EntityOperationFailed as e:
                return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
         
        serializers = PostSerializer(domain_posts, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializers = CreatePostSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
       
        author_id = serializers.validated_data["author_id"]
        content = serializers.validated_data["content"]

        try:
            post = CreatePost(PostRepositoryImpl()).execute(author_id,content)
        except ValueError as e:
            return Response({'error':str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except EntityOperationFailed as e:
            return Response({'error':str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except EntityDoesNotExist as e:
            return Response({'error':str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        print(post)
        return Response({"message": "Post created successfully"}, status=status.HTTP_200_OK)




class PostDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, post_id):
        try:
            domain_post =  GetPostById(PostRepositoryImpl()).execute(post_id)
        except EntityDoesNotExist as e:
            return Response({'error':str(e)}, status=status.HTTP_404_NOT_FOUND)
        except EntityOperationFailed as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        
        
        serializers = PostSerializer(domain_post)
        return Response(serializers.data, status=status.HTTP_200_OK)
    
    def patch(self, request, post_id):
        try:
            old_domain_post = GetPostById(PostRepositoryImpl()).execute(post_id)
        except EntityDoesNotExist as e:
            return Response({'error':str(e)}, status=status.HTTP_404_NOT_FOUND) 
        except EntityOperationFailed as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        serializers = PostSerializer(old_domain_post, data=request.data, partial = True)
        serializers.is_valid(raise_exception=True)
        data = serializers.validated_data

        try:
            old_domain_post.update_content(data.get("content",old_domain_post.content), request.user.id)
        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        
        updated = UpdatePost(PostRepositoryImpl()).execute(old_domain_post)
        return Response(PostSerializer(updated).data, status=status.HTTP_200_OK)
    
    def delete(self, request, post_id):
        try:
            target_domain_post = GetPostById(PostRepositoryImpl()).execute(post_id)
        except EntityDoesNotExist as e:
            return Response({'error':str(e)}, status=status.HTTP_404_NOT_FOUND) 
        except EntityOperationFailed as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST) 
        try: 
            target_domain_post.verify_deletable_by(request.user.id)
        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)

        DeletePost(PostRepositoryImpl()).execute(target_domain_post)
        return Response({"message":"Post deleted successfully"},status=status.HTTP_204_NO_CONTENT)
