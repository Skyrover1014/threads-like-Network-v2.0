from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from threads.interface.util.error_response import error_response
from threads.common.exceptions import  EntityOperationFailed, EntityDoesNotExist

from threads.interface.serializers.fact_check_serializer import FactCheckSerializer
from threads.infrastructure.external.openai_client import OpenAIClient





class FactCheckBaseView(APIView):
    def _handler_exception(self, e):
        if isinstance(e, EntityDoesNotExist):
            return error_response(message=e, type_name="EntityDoesNotExist", 
                                  code=status.HTTP_404_NOT_FOUND, source="Post/CommentRepositoryImpl.get_post/comment_by_id")
        elif isinstance(e, EntityOperationFailed):
            return error_response(message=e, type_name="EntityOperationFailed",
                                  code=status.HTTP_500_INTERNAL_SERVER_ERROR, source="Model.Post/Comment")
        elif isinstance(e, ValueError):
            return error_response(message=e, type_name="ValueError",
                                  code=status.HTTP_400_BAD_REQUEST, source="Entity.ContentItem.validate")
        else:
            return error_response(message=e, type_name=type(e).__name__, code=500)
        
    def _handler_post(self, request):
        serializers = FactCheckSerializer(data= request.data)
        serializers.is_valid(raise_exception=True)

        content = serializers.validated_data["content"]
        prompt = serializers.validated_data.get("prompt")

        if not content:
            return Response({"error": "Missing Post or Comment"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not prompt:
            target = content
        else:
            target = {
                "content":content,
                "prompt":prompt
            }
        
        openai_client  = OpenAIClient()
        result = openai_client.fact_check(target)
        return Response({"response":result })
    
       
         