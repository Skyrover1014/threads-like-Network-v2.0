
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated


from .comment_baseView import CommentBaseView
from ...serializers.comment_serializer import CommentSerializer, CreateChildCommentSerializer

from threads.infrastructure.repository.comment_repository import CommentRepositoryImpl
from threads.use_cases.commands.create_comment import CreateComment
from threads.use_cases.queries.get_child_comments_by_comment_id import GetChildCommentsByCommentId


from threads.interface.util.dev_tool import extend_schema_view, extend_schema, OpenApiResponse, OpenApiExample
# from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiExample, OpenApiRequest
from threads.interface.serializers.message_serializer import MessageSerializer


@extend_schema_view(
    get=extend_schema(
        summary="取得子留言列表",
        description="可用 offset、limit 分頁，example: urls後面寫?offset=0&limit=5",        
        responses={
            200: OpenApiResponse(
                description="使用者成功讀取子留言列表",
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
        summary="撰寫新子留言",
        description="需要在特定留言底下，進行留言，需要輸入author_id, content和 parent_post_id，即可創建新子留言，留言內容不可為白",
        request=CreateChildCommentSerializer,
        examples=[OpenApiExample(name="撰寫子留言",value={"author_id":"1","content": "我想要建立子留言","parent_post_id":"1"},summary="模擬輸入參數，創建新的子留言")],
        responses={
            201:OpenApiResponse(
                description="使用者新增完子留言，導向留言列表",
                response=MessageSerializer
            ),
            400:OpenApiResponse(
                description="欲新增留言不符合規範",
                response=MessageSerializer,
            ),
            404:OpenApiResponse(
                description="欲留言的母貼文或母留言並不存在，或已被刪除",
                response=MessageSerializer,
            ),
            500:OpenApiResponse(
                description="伺服器內部錯誤",
                response=MessageSerializer,
            )
        },
    )
)
@extend_schema(tags=["Child Comments"])
class ChildCommentListCreateView(CommentBaseView):
    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id):
        serializers = CreateChildCommentSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)

        author_id = serializers.validated_data["author_id"]
        content = serializers.validated_data["content"]
        parent_post_id = serializers.validated_data["parent_post_id"]

        try:
            comment = CreateComment(CommentRepositoryImpl()).execute(author_id, content, parent_post_id, comment_id)
        except Exception as e:
            return self._handler_exception(e)
        return Response({"message": "Comment created successfully"}, status=status.HTTP_200_OK)

    def get(self, request, comment_id):
        
        auth_user_id = request.user.id
        offset = int(request.query_params.get("offset", 0))
        limit = int(request.query_params.get("limit", 10))

        try: 
            domain_child_comments = GetChildCommentsByCommentId(CommentRepositoryImpl()).execute(auth_user_id=auth_user_id, comment_id=comment_id, offset=offset, limit=limit)
        except Exception as e:
            return self._handler_exception(e)
        
        serializers = CommentSerializer(domain_child_comments, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)
