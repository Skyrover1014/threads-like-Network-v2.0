from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from threads.interface.util.error_response import error_response
# 
from threads.use_cases.queries.get_comment_by_id import GetCommentById
from threads.infrastructure.repository.comment_repository import CommentRepositoryImpl

from threads.common.base_exception import BaseAppException
from threads.common.exceptions.use_case_exceptions import InvalidObject, UnauthorizedAction, NotFound, AlreadyExist, ServiceUnavailable


class CommentBaseView(APIView):

    def _get_comment_by_id(self, request, comment_id):
        return  GetCommentById(CommentRepositoryImpl()).execute(comment_id, request.user.id)   

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

    def _get_status(self, e):
        if isinstance(e, InvalidObject):
            return status.HTTP_400_BAD_REQUEST
        elif isinstance(e, UnauthorizedAction):
            return status.HTTP_403_FORBIDDEN
        elif isinstance(e, NotFound):
            return status.HTTP_404_NOT_FOUND
        elif isinstance(e, AlreadyExist):
            return status.HTTP_406_NOT_ACCEPTABLE
        elif isinstance(e, ServiceUnavailable):
            return status.HTTP_500_INTERNAL_SERVER_ERROR
        return status.HTTP_500_INTERNAL_SERVER_ERROR 