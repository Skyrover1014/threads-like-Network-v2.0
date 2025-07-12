
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated


from .comment_baseView import CommentBaseView
from ...serializers.comment_serializer import CommentSerializer

from threads.infrastructure.repository.comment_repository import CommentRepositoryImpl
from threads.use_cases.queries.get_comment_by_id import GetCommentById
from threads.use_cases.commands.update_comment import UpdateComment
from threads.use_cases.commands.delete_comment import DeleteComment

from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiExample, OpenApiRequest
from threads.interface.serializers.message_serializer import MessageSerializer

@extend_schema_view(
    get=extend_schema(
        summary="讀取單一留言",
        description="可以對單一留言進行CRUD操作的更新與刪除",        
        responses={
            200: OpenApiResponse(
                description="使用者成功讀取留言",
                response=CommentSerializer
            ),
            404:OpenApiResponse(
                description="欲讀取留言並不存在",
                response=MessageSerializer,
            ), 
            500:OpenApiResponse(
                description="伺服器內部錯誤",
                response=MessageSerializer,
            ) 
        }
    ),
    patch=extend_schema(
        summary="更新單一留言",
        description="只需要輸入留言 content, 不可輸入空白貼文，非作者無權限修改",
        request=CommentSerializer,
        examples=[OpenApiExample(name="更新留言",value={"content": "我想更新留言"},summary="模擬輸入參數，更新留言")],
        responses={
            201:OpenApiResponse(
                description="使用者成功更新留言，並且取得更新後的留言",
                response=CommentSerializer
            ),
            403:OpenApiResponse(
                description="無權限更新貼文",
                response=MessageSerializer,
            ),
            404:OpenApiResponse(
                description="欲更新留言不存在",
                response=MessageSerializer,
            ),
            500:OpenApiResponse(
                description="伺服器內部錯誤",
                response=MessageSerializer,
            )
        },
    ),
    delete=extend_schema(
        summary="刪掉單一留言",
        responses={
            204:None,
            403:OpenApiResponse(
                description="無權限刪除留言",
                response=MessageSerializer,
            ),
            404:OpenApiResponse(
                description="欲刪除留言並不存在",
                response=MessageSerializer,
            ),
            500:OpenApiResponse(
                description="伺服器內部錯誤",
                response=MessageSerializer,
            )
        }
    )
)
@extend_schema(tags=["Comment"])
class CommentDetailView(CommentBaseView):
    permission_classes = [IsAuthenticated]


    def get(self, request, comment_id):
        try:
            domain_comment = self._get_comment_by_id(request,comment_id)
        except Exception as e:
            return self._handler_exception(e)
        serializers = CommentSerializer(domain_comment)
        return Response(serializers.data, status=status.HTTP_200_OK)
    
    def patch(self, request, comment_id):
        # try:
        #     old_domain_comment = self._get_comment_by_id(request, comment_id)
        # except Exception as e:
        #     return self._handler_exception(e)
        
        serializers = CommentSerializer(data=request.data, partial = True)
        serializers.is_valid(raise_exception=True)
        new_data = serializers.validated_data

        # try:
        #     old_domain_comment.update_content(new_data.get("content", old_domain_comment.content), request.user.id)
        # except Exception as e:
        #     return self._handler_exception(e)
        try:
            updated = UpdateComment(CommentRepositoryImpl()).execute(user_id=request.user.id,comment_id=comment_id, new_data=new_data)
        except Exception as e:
            return self._handler_exception(e)
        return Response(CommentSerializer(updated).data, status=status.HTTP_200_OK)

    def delete(self, request, comment_id):
        # try:
        #     target_domain_comment = self._get_comment_by_id(request, comment_id)
        # except Exception as e:
        #     return self._handler_exception(e)
        
        # try:
        #     target_domain_comment.verify_deletable_by(request.user.id)
        # except Exception as e:
        #     return self._handler_exception(e)
        try:
            DeleteComment(CommentRepositoryImpl()).execute(request.user.id, comment_id)
        except Exception as e:
            return self._handler_exception(e)
        
        return Response(status=status.HTTP_204_NO_CONTENT)

        

        
         