
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated


from .comment_baseView import CommentBaseView
from ...serializers.comment_serializer import CommentSerializer, CreateCommentSerializer

from threads.infrastructure.repository.comment_repository import CommentRepositoryImpl
from threads.use_cases.commands.create_comment import CreateComment
from threads.use_cases.queries.get_comments_by_post_id import GetCommentsByPostId


from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiExample, OpenApiRequest
from threads.interface.serializers.message_serializer import MessageSerializer


@extend_schema_view(
    get=extend_schema(
        summary="取得留言列表",
        description="可用 offset、limit 分頁，example: urls後面寫?offset=0&limit=5",        
        responses={
            200: OpenApiResponse(
                description="使用者成功讀取留言列表",
                response=CommentSerializer(many=True)
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
        summary="撰寫新留言",
        description="需要在特定貼文底下，進行留言，需要輸入author_id 和 content，即可創建新子留言，留言內容不可為白",
        request=CreateCommentSerializer,
        examples=[OpenApiExample(name="撰寫留言",value={"author_id":"1","content": "我想要建立留言"},summary="模擬輸入參數，創建新的留言")],
        responses={
            201:OpenApiResponse(
                description="使用者新增完留言，導向留言列表",
                response=MessageSerializer
            ),
            400:OpenApiResponse(
                description="欲新增留言不符合規範",
                response=MessageSerializer,
            ),
            404:OpenApiResponse(
                description="欲留言的母貼文並不存在，或已被刪除",
                response=MessageSerializer,
            ),
            500:OpenApiResponse(
                description="伺服器內部錯誤",
                response=MessageSerializer,
            )
        },
    )
)
@extend_schema(tags=["Comments"])
class CommentListCreateView(CommentBaseView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        serializers = CreateCommentSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)

        author_id = serializers.validated_data["author_id"]
        content = serializers.validated_data["content"]

        try:
            comment = CreateComment(CommentRepositoryImpl()).execute(author_id=author_id, content=content, parent_post_id=post_id, parent_comment_id=None)
        except Exception as e:
            return self._handler_exception(e)
        return Response({"message": "Comment created successfully"}, status=status.HTTP_200_OK)
    
    def get(self, request, post_id):

        auth_user_id = request.user.id
        offset = int(request.query_params.get("offset", 0))
        limit = int(request.query_params.get("limit", 10))

        repo = CommentRepositoryImpl()
        try:
            domain_comments = GetCommentsByPostId(repo).execute(auth_user_id, post_id, offset, limit)
        except Exception as e:
            return self._handler_exception(e)
        
        
        serializers = CommentSerializer(domain_comments, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)
    