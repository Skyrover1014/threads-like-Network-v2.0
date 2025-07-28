from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from threads.infrastructure.repository.like_repository import LikeRepositoryImpl

from ...serializers.like_serializer import LikeSerializer
from .like_baseView import LikeBaseView

from threads.use_cases.queries.get_like_by_id import GetLikeById
from threads.use_cases.commands.create_like import CreateLike
from threads.use_cases.commands.delete_like import DeleteLike

from threads.interface.util.dev_tool import extend_schema_view, extend_schema, OpenApiResponse, OpenApiExample
# from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiExample, OpenApiRequest
from threads.interface.serializers.message_serializer import MessageSerializer

@extend_schema_view(
    get=extend_schema(
        summary="讀取單一貼文/留言的個人按讚紀錄",
        description="可以對單一貼文/留言進行按讚或是取消按讚",        
        responses={
            200: OpenApiResponse(
                description="使用者成功讀取貼文/留言按讚紀錄",
                response=LikeSerializer
            ),
            404:OpenApiResponse(
                description="欲讀取貼文/留言按讚紀錄並不存在 或是目標貼文/留言不存在",
                response=MessageSerializer,
            ), 
            500:OpenApiResponse(
                description="伺服器內部錯誤",
                response=MessageSerializer,
            ) 
        }
    ),
    post=extend_schema(
        summary="按讚該貼文或留言",
        description="無需要輸入任何參數，只需要按下 post 按鈕",
        request=LikeSerializer,
        examples=[OpenApiExample(name="按讚內容",value={},summary="模擬不需要輸入參數，就可按讚內容")],
        responses={
            201:OpenApiResponse(
                description="使用者成功新增按讚紀錄",
                response=MessageSerializer
            ),
            404:OpenApiResponse(
                description="欲讀取貼文/留言按讚紀錄並不存在 或是目標貼文/留言不存在",
                response=MessageSerializer,
            ),
            406:OpenApiResponse(
                description="已有按讚紀錄，不可重複按讚，須先刪除按讚紀錄",
                response=MessageSerializer,
            ),
            500:OpenApiResponse(
                description="伺服器內部錯誤",
                response=MessageSerializer,
            )
        },
    ),
    delete=extend_schema(
        summary="刪掉按讚紀錄",
        responses={
            204:None,
            403:OpenApiResponse(
                description="無權限刪除紀錄",
                response=MessageSerializer,
            ),
            404:OpenApiResponse(
                description="欲讀取貼文/留言按讚紀錄並不存在 或是目標貼文/留言不存在",
                response=MessageSerializer,
            ),
            500:OpenApiResponse(
                description="伺服器內部錯誤",
                response=MessageSerializer,
            )
        }
    )
)
@extend_schema(tags=["Like"])
class LikeContentView(LikeBaseView):
    permission_classes=[IsAuthenticated]

    def get (self, request, content_id,content_type):

        user_id = request.user.id
        try:
            domain_like = GetLikeById(LikeRepositoryImpl()).execute(user_id, content_id, content_type)
        except Exception as e:
            return self._handler_exception(e)
        
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
        except Exception as e:
            return self._handler_exception(e)
        return Response({"message": "Liked Successfully"}, status=status.HTTP_201_CREATED)
    
    def delete (self, request, content_id, content_type):
        user_id = request.user.id
        try:
            delete_lke = DeleteLike(LikeRepositoryImpl()).execute(user_id, content_id, content_type, deleter=request.user.id)
        except Exception as e:
           return self._handler_exception(e)
        return Response(status=status.HTTP_204_NO_CONTENT)
 
        