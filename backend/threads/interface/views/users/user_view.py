from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny


from .user_baseView import UserBaseView
from ...serializers.user_serializer import UserSerializer, RegisterUserSerializer


from threads.infrastructure.repository.user_repository import UserRepositoryImpl

from threads.use_cases.commands.register_user import RegisterUser
from threads.use_cases.queries.get_user_profile import GetUserProfile

from threads.interface.util.dev_tool import extend_schema_view, extend_schema, OpenApiResponse
# from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse
from threads.interface.serializers.message_serializer import MessageSerializer
@extend_schema_view(
    get=extend_schema(
        summary="讀取單一用戶",
        description="用戶profile",
        responses={
            200: OpenApiResponse(
                description="使用者成功讀取Profile",
                response=UserSerializer
            ),
            404:OpenApiResponse(
                description="欲讀取用戶頁面並不存在",
                response=MessageSerializer,
            ), 
            500:OpenApiResponse(
                description="伺服器內部錯誤",
                response=MessageSerializer,
            ) 
        }
    )
)
@extend_schema(tags=["User"])
class UserDetailView(UserBaseView):
    permission_classes = [AllowAny]

    def get(self, request, user_id):
        try:
            domain_user = GetUserProfile(UserRepositoryImpl()).execute(user_id)
            serializers = UserSerializer(domain_user)
        except Exception as e:
            return self._handler_exception(e)
        return Response(serializers.data, status=status.HTTP_200_OK)
