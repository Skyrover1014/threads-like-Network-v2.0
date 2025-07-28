from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny

from .user_baseView import UserBaseView
from ...serializers.user_serializer import RegisterUserSerializer

from threads.infrastructure.repository.user_repository import UserRepositoryImpl
from threads.use_cases.commands.register_user import RegisterUser
    
from threads.interface.util.dev_tool import extend_schema_view, extend_schema, OpenApiResponse, OpenApiExample

# from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiResponse, OpenApiExample, OpenApiRequest
from threads.interface.serializers.message_serializer import MessageSerializer
@extend_schema_view(
    post=extend_schema(
        summary="註冊為新用戶",
        description="註冊用戶",
        request=RegisterUserSerializer,
        examples=[OpenApiExample(name="註冊用戶",value={"username": "Allen", "email":"allen@example.com", "password":123341,"confirmation":123341},summary="這個範例模擬註冊為新用戶")],
        responses={
            201: OpenApiResponse(
                description="成功註冊為新用戶",
                response=MessageSerializer
            ),
            400:OpenApiResponse(
                description="使用者名稱可包含字母和數字，可輸入3-50個字元",
                response=MessageSerializer,
             ),
            406:OpenApiResponse(
                description="使用者名稱/信箱重複",
                response=MessageSerializer,
            ), 
            500:OpenApiResponse(
                description="伺服器內部錯誤",
                response=MessageSerializer,
            )
        },
    )
)
@extend_schema(tags=["Users"])
class UserCreateView(UserBaseView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        username = serializer.validated_data['username']
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']

        try:
            user = RegisterUser(UserRepositoryImpl()).execute(username, email, password)
        except Exception as e:
            return self._handler_exception(e)
        
        return Response({"message": "User created successfully."}, status=status.HTTP_201_CREATED)
    
    