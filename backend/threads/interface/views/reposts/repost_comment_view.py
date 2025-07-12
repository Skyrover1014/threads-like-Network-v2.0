from rest_framework.permissions import IsAuthenticated
from .repost_baseView import RepostBaseView


from threads.interface.serializers.repost_serializer import RepostSerializer, RepostResponseSerializer
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiExample, OpenApiRequest
from threads.interface.serializers.message_serializer import MessageSerializer

@extend_schema_view(
    post=extend_schema(
        summary="轉發留言",
        description="轉發留言或子留言，成新貼文或是留言或子留言，不同轉發行為會有不通欄位需輸入，請參考example",
        request=RepostSerializer,
        examples=[
            OpenApiExample(name="轉發留言成貼文",value={"author_id":1, "content":"我想要轉發一篇留言成貼文","target_type":"post"},summary="只需要設定target_type為post"),
            OpenApiExample(name="轉發留言成留言",value={"author_id":1, "content":"我想要轉發一篇留言成留言","target_type":"comment","target_post":1},summary="需要多輸入target_post，指定要在哪篇貼文留言"),
            OpenApiExample(name="轉發留言成子留言",value={"author_id":1, "content":"我想要轉發一篇留言成子留言","target_type":"comment","target_post":1, "target_comment":1},summary="需要同時輸入target_post和 target_comment，指定要在哪篇貼文的留言，留下子留言"),
        ],
        responses={
            201:OpenApiResponse(
                description="使用者成功轉發內容",
                response=RepostResponseSerializer
            ),
            400:OpenApiResponse(
                description="新建立的內容不符合規範",
                response=MessageSerializer,
            ),
            404:OpenApiResponse(
                description="欲轉發留言並不存在",
                response=MessageSerializer,
            ),
            500:OpenApiResponse(
                description="伺服器內部錯誤",
                response=MessageSerializer,
            )
        },
    )
)
@extend_schema(tags=["Repost"])
class RepostCommentView(RepostBaseView):
    permission_classes = [IsAuthenticated]
 
    def post(self, request, comment_id):
        return self._handler_post(
            request =request,
            repost_of= comment_id,
            repost_of_content_type='comment'
        )