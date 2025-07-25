from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from threads.interface.util.error_response import error_response
from threads.common.base_exception import BaseAppException
from threads.common.exceptions.use_case_exceptions import InvalidObject, UnauthorizedAction, NotFound, AlreadyExist, ServiceUnavailable


from ...serializers.repost_serializer import RepostSerializer
from ...serializers.post_serializer import PostSerializer
from ...serializers.comment_serializer import CommentSerializer

from threads.infrastructure.repository.comment_repository import CommentRepositoryImpl
from threads.infrastructure.repository.post_repository import PostRepositoryImpl

from threads.use_cases.commands.repost_content import CreateRePost
from threads.use_cases.commands.repost_content import RepostTarget

import traceback



class RepostBaseView(APIView):
    def _handler_exception(self, e):
        if isinstance(e, BaseAppException):
            response_data = e.to_response()
            return error_response(message=response_data["message"],type_name=response_data["type"], code=self._get_status(e)
            )
        elif isinstance(e, ValueError):
            return error_response(message=str(e), type_name="ValueError",
                code=status.HTTP_400_BAD_REQUEST
            )
        else:
            return error_response(
                message="系統內部錯誤，請稍後再試", type_name=type(e).__name__,
                code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
        # else:
        #     print("[Unhandled Exception]:", traceback.format_exc())
        #     return error_response(
        #         message="系統內部錯誤，請稍後再試",
        #         type_name=type(e).__name__,
        #         code=status.HTTP_500_INTERNAL_SERVER_ERROR
        #      )

    def _get_status(self, e):
        if isinstance(e, InvalidObject):
            return status.HTTP_400_BAD_REQUEST
        elif isinstance(e, NotFound):
            return status.HTTP_404_NOT_FOUND
        elif isinstance(e, ServiceUnavailable):
            return status.HTTP_500_INTERNAL_SERVER_ERROR
        return status.HTTP_500_INTERNAL_SERVER_ERROR
    
    def _handler_post(self, request, repost_of, repost_of_content_type ):
        serializers = RepostSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)
       
        author_id = serializers.validated_data["author_id"]
        content = serializers.validated_data["content"]
        target_type = serializers.validated_data["target_type"]
        target_post = serializers.validated_data.get("target_post")
        target_comment = serializers.validated_data.get("target_comment") 
        
        repost_of = repost_of
        repost_of_content_type = repost_of_content_type
        
        try:
            target = RepostTarget(
                target_type=target_type,
                target_post_id=target_post,
                target_comment_id=target_comment
            )

            repost_set = CreateRePost(PostRepositoryImpl(), CommentRepositoryImpl()).execute(
                author_id, content, repost_of, repost_of_content_type, target)
        except Exception as e:
            return self._handler_exception(e) 
        
        
        content_serializers= {
            "post": PostSerializer,
            "comment": CommentSerializer
        }

        repost = content_serializers[target_type](repost_set.repost).data
        original = content_serializers[repost_of_content_type](repost_set.original).data
        response_data = {
            "message": "Post created successfully",
            "repost": repost,
            "original": original
        }

        return Response(response_data, status=status.HTTP_201_CREATED)