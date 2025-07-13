from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from ...serializers.post_serializer import PostSerializer, CreatePostSerializer
from .post_baseView import PostBaseView
from threads.infrastructure.repository.user_repository import UserRepositoryImpl
from threads.infrastructure.repository.post_repository import PostRepositoryImpl


from threads.use_cases.queries.get_profile_posts import GetProfilePost
from threads.use_cases.queries.get_followings_posts import GetFollowingsPost
from threads.use_cases.queries.get_all_posts import GetAllPost
from threads.use_cases.queries.get_following_user_ids import GetFollowingUserIds
from threads.use_cases.commands.create_post import CreatePost

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiExample, OpenApiRequest
from threads.interface.serializers.message_serializer import MessageSerializer


@extend_schema_view(

    get=extend_schema(
        summary="取得貼文列表",
        description="支援 author_id、following 篩選，可用 offset、limit 分頁，example: urls後面寫?author_id=1&following=true&offset=0&limit=5",        
        responses={
            200: OpenApiResponse(
                description="使用者成功讀取貼文列表",
                response=PostSerializer(many=True)
            ),
            404:OpenApiResponse(
                description="欲讀取列表並不存在",
                response=MessageSerializer,
            ), 
            500:OpenApiResponse(
                description="伺服器內部錯誤",
                response=MessageSerializer,
            ) 
        }
    ),
    post=extend_schema(
        summary="撰寫新貼文",
        description="只需要輸入作者id和貼文content，即可創建新貼文，貼文內容不可為白",
        request=CreatePostSerializer,
        examples=[OpenApiExample(name="撰寫貼文",value={"author_id":"1","content": "我想要建立貼文"},summary="這個範例模擬使用者只需要輸入 author_id 和 content 欄位，其餘欄位保留原書")],
        responses={
            201:OpenApiResponse(
                description="使用者新增完貼文，導向貼文列表",
                response=MessageSerializer
            ),
            400:OpenApiResponse(
                description="欲新增貼文不符合規範",
                response=MessageSerializer,
            ), 
            500:OpenApiResponse(
                description="伺服器內部錯誤",
                response=MessageSerializer,
            )
        },
    )
)
@extend_schema(tags=["Posts"]) 
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
        author_name = serializers.validated_data["author_name"]
        content = serializers.validated_data["content"]

        try:
            post = CreatePost(PostRepositoryImpl()).execute(author_id, author_name, content)
        except Exception as e:
                return self._handler_exception(e)
        
        return Response({"message": "Post created successfully"}, status=status.HTTP_201_CREATED)