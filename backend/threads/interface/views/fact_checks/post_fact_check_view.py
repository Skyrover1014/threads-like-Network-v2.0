from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from threads.infrastructure.external.openai_client import OpenAIClient
from .base_fact_check_view import FactCheckBaseView
from ...serializers.fact_check_serializer import FactCheckSerializer
from ...serializers.post_serializer import PostSerializer

from threads.use_cases.queries.get_post_by_id import GetPostById
from threads.infrastructure.repository.post_repository import PostRepositoryImpl
from .base_fact_check_view import FactCheckBaseView

from threads.interface.util.dev_tool import extend_schema_view, extend_schema, OpenApiResponse, OpenApiExample
# from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiExample, OpenApiRequest
from threads.interface.serializers.message_serializer import MessageSerializer


@extend_schema_view(
    get=extend_schema(
        summary="取得欲查核的貼文",
        description="content自動攜帶，prompt選填",        
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
    post=extend_schema(
        summary="撰寫事實查核Prompt（選填）",
        description="AI會提供結果摘要，以及對應資料出處，協助使用者判斷是否為事實",
        request=FactCheckSerializer,
        examples=[OpenApiExample(name="撰寫查核問題",value={"content": "原留言內容","prompt":"選填想要詢問的問題"},summary="這個範例模擬使用者進行查核")],
        responses={
            200:OpenApiResponse(
                description="使用者取得查核結果",
                response=MessageSerializer
            ),
            400:OpenApiResponse(
                description="缺少content，或遺失content",
                response=MessageSerializer,
            ), 
            500:OpenApiResponse(
                description="伺服器內部錯誤",
                response=MessageSerializer,
            )
        },
    )
)
@extend_schema(tags=["FactCheck"])
class PostFactCheckView(FactCheckBaseView):
    permission_classes = [IsAuthenticated]
    def get(self, request, post_id):
        try:
            domain_post = GetPostById(PostRepositoryImpl()).execute(post_id, request.user.id) #不應該要 user_id
        except Exception as e:
            return self._handler_exception(e)
        
        serializers = PostSerializer(domain_post)
        return Response(serializers.data, status=status.HTTP_200_OK)


    def post(self, request, post_id):
        return self._handler_post(request)