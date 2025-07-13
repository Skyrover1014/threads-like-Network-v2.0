from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated



from threads.interface.serializers.post_serializer import PostSerializer
from .post_baseView import PostBaseView

from threads.infrastructure.repository.post_repository import PostRepositoryImpl
from threads.use_cases.queries.get_post_by_id import GetPostById
from threads.use_cases.commands.update_post import UpdatePost
from threads.use_cases.commands.delete_post import DeletePost
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiExample, OpenApiRequest
from threads.interface.serializers.message_serializer import MessageSerializer
@extend_schema_view(
    get=extend_schema(
        operation_id="get_single_post",
        summary="讀取單一貼文",
        description="可以對單一貼文進行CRUD操作的更新與刪除",
        responses={
            200: OpenApiResponse(
                description="使用者成功讀取貼文",
                response=PostSerializer
            ),
            404:OpenApiResponse(
                description="欲讀取貼文並不存在",
                response=MessageSerializer,
            ), 
            500:OpenApiResponse(
                description="伺服器內部錯誤",
                response=MessageSerializer,
            ) 
        }
    ),
    patch=extend_schema(
        summary="更新單一貼文",
        description="只需要輸入貼文 content, 不可輸入空白貼文，非作者無權限修改",
        request=PostSerializer(partial=True),
        examples=[OpenApiExample(name="更新貼文",value={"content": "我想要改一下文字"},summary="這個範例模擬使用者只更新 content 欄位，其餘欄位保留原值")],
        responses={
            206: OpenApiResponse(
                description="使用者成功更新貼文，並且取得更新後的貼文",
                response=PostSerializer
            ),
            403:OpenApiResponse(
                description="無權限更新貼文",
                response=MessageSerializer,
             ),
            404:OpenApiResponse(
                description="欲更新貼文並不存在",
                response=MessageSerializer,
            ), 
            500:OpenApiResponse(
                description="伺服器內部錯誤",
                response=MessageSerializer,
            )
        },
    ),
    delete=extend_schema(
        summary="刪掉單一貼文",
        responses={
            204:None,
            403:OpenApiResponse(
                description="無權限刪除貼文",
                response=MessageSerializer,
            ),
            404:OpenApiResponse(
                description="欲刪除貼文並不存在",
                response=MessageSerializer,
            ),
            500:OpenApiResponse(
                description="伺服器內部錯誤",
                response=MessageSerializer,
            )
        }
    )
)
@extend_schema(tags=["Post"]) 
class PostDetailView(PostBaseView):
    permission_classes = [IsAuthenticated]

    def _get_post_by_id(self, request, post_id):
        return  GetPostById(PostRepositoryImpl()).execute(post_id, request.user.id)   

    def get(self, request, post_id):
        try:
            domain_post =  self._get_post_by_id(request, post_id)
        except Exception as e:
            return self._handler_exception(e)
        serializers = PostSerializer(domain_post)
        return Response(serializers.data, status=status.HTTP_200_OK)
    
    def patch(self, request, post_id):
        
        serializers = PostSerializer(data=request.data, partial = True)
        serializers.is_valid(raise_exception=True)
        data = serializers.validated_data

        try:
            updated = UpdatePost(PostRepositoryImpl()).execute(post_id, data, request.user.id)
        except Exception as e:
            return self._handler_exception(e)
        return Response(PostSerializer(updated).data, status=status.HTTP_206_PARTIAL_CONTENT)
    
    def delete(self, request, post_id):
        try:
            DeletePost(PostRepositoryImpl()).execute(user_id=request.user.id, post_id=post_id)
        except Exception as e:
            return self._handler_exception(e)
        return Response(status=status.HTTP_204_NO_CONTENT)