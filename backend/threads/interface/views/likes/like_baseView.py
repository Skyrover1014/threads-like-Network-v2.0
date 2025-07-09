from rest_framework.views import APIView
from rest_framework import status

from threads.interface.util.error_response import error_response
from threads.common.exceptions import EntityAlreadyExists, EntityOperationFailed, EntityDoesNotExist



class LikeBaseView(APIView):
    def _handler_exception(self, e):
        if isinstance(e, EntityDoesNotExist):
            return error_response(message=e, type_name="EntityDoesNotExist", 
                                  code=status.HTTP_404_NOT_FOUND, source="LikeRepositoryImpl.get_like_by_id")
        elif isinstance(e, EntityOperationFailed):
            return error_response(message=e, type_name="EntityOperationFailed",
                                  code=status.HTTP_500_INTERNAL_SERVER_ERROR, source="Model.Like")
        elif isinstance(e, ValueError):
            return error_response(message=e, type_name="ValueError",
                                  code=status.HTTP_400_BAD_REQUEST, source="Entity.ContentItem.validate")
        elif isinstance(e, PermissionError):
            return error_response(message=e, type_name="PermissionError",
                                  code=status.HTTP_403_FORBIDDEN, source="Entity.ContentItem.validate")
        elif isinstance(e, EntityAlreadyExists):
            return error_response(message=e, type_name="EntityAlreadyExists", 
                                  code=status.HTTP_406_NOT_ACCEPTABLE, source="LikeRepositoryImpl")
        else:
            return error_response(message=e, type_name=type(e).__name__, code=500)
