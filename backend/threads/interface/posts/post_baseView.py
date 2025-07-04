from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from threads.interface.util.error_response import error_response
from threads.common.exceptions import EntityAlreadyExists, EntityOperationFailed, EntityDoesNotExist





class PostBaseView(APIView):
   def _handler_exception(self, e):
        if isinstance(e, EntityDoesNotExist):
            return error_response(message=e, type_name="EntityDoesNotExist", 
                                  code=status.HTTP_404_NOT_FOUND, source="PostRepositoryImpl.get_post_by_id")
        elif isinstance(e, EntityOperationFailed):
            return error_response(message=e, type_name="EntityOperationFailed",
                                  code=status.HTTP_500_INTERNAL_SERVER_ERROR, source="Model.Comment")
        elif isinstance(e, ValueError):
            return error_response(message=e, type_name="ValueError",
                                  code=status.HTTP_400_BAD_REQUEST, source="Entity.ContentItem.validate")
        elif isinstance(e, PermissionError):
            return error_response(message=e, type_name="PermissionError",
                                  code=status.HTTP_403_FORBIDDEN, source="Entity.ContentItem.validate")
        else:
            return error_response(message=e, type_name=type(e).__name__, code=500)
         