from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from ..Serializers.post_serializer import PostSerializer, CreatePostSerializer
from .post_baseView import PostBaseView
from threads.repositories import PostRepositoryImpl, UserRepositoryImpl

from threads.use_cases.queries.get_profile_posts import GetProfilePost
from threads.use_cases.queries.get_followings_posts import GetFollowingsPost
from threads.use_cases.queries.get_all_posts import GetAllPost
from threads.use_cases.queries.get_following_user_ids import GetFollowingUserIds
from threads.use_cases.commands.create_post import CreatePost



class PostListCreateView(PostBaseView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        auth_user_id = request.user.id
        author_id = request.query_params.get("author_id")
        following = request.query_params.get("following") == "true"
        offset = int(request.query_params.get("offset", 0))
        limit = int(request.query_params.get("limit", 10))
        
        repo = PostRepositoryImpl()

        if author_id:
            try:
                domain_posts = GetProfilePost(repo).execute(auth_user_id, author_id, offset, limit)
            except Exception as e:
                return self._handler_exception(e)
        elif following:
            try:
                following_ids = GetFollowingUserIds(UserRepositoryImpl()).execute(auth_user_id)
            except Exception as e:
                return self._handler_exception(e)
            
            try:
                domain_posts = GetFollowingsPost(repo).execute(auth_user_id, following_ids, offset, limit)
            except Exception as e:
                return self._handler_exception(e)
        else:
            try:
                domain_posts = GetAllPost(repo).execute(auth_user_id, offset, limit)
            except Exception as e:
                return self._handler_exception(e)
         
        serializers = PostSerializer(domain_posts, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)
    
    def post(self, request):
        serializers = CreatePostSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
       
        author_id = serializers.validated_data["author_id"]
        content = serializers.validated_data["content"]

        try:
            post = CreatePost(PostRepositoryImpl()).execute(author_id,content)
        except Exception as e:
                return self._handler_exception(e)
        
        print(post)
        return Response({"message": "Post created successfully"}, status=status.HTTP_200_OK)