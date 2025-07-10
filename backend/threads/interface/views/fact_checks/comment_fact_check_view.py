from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from threads.infrastructure.external.openai_client import OpenAIClient
from ...serializers.fact_check_serializer import FactCheckSerializer

from ...serializers.comment_serializer import CommentSerializer
from .base_fact_check_view import FactCheckBaseView
from threads.use_cases.queries.get_comment_by_id import GetCommentById
from threads.infrastructure.repository.comment_repository import CommentRepositoryImpl


class CommentFactCheckView(FactCheckBaseView):
    permission_classes = [IsAuthenticated]
    def get(self, request, comment_id):
        try:
            domain_comment = GetCommentById(CommentRepositoryImpl()).execute(comment_id, request.user.id)
        except Exception as e:
            return self._handler_exception(e)
        
        serializers = CommentSerializer(domain_comment)

        return Response(serializers.data, status=status.HTTP_200_OK)


    def post(self, request, comment_id):
        return self._handler_post(request)

        # serializers = FactCheckSerializer(data= request.data)
        # serializers.is_valid(raise_exception=True)

        # content = serializers.validated_data["content"]
        # prompt = serializers.validated_data.get("prompt")

        # if not content:
        #     return Response({"error": "Missing Post or Comment"}, status=status.HTTP_400_BAD_REQUEST)
        
        # if not prompt:
        #     target = content
        # else:
        #     target = {
        #         "content":content,
        #         "prompt":prompt
        #     }
        
        # openai_client  = OpenAIClient()
        # result = openai_client.fact_check(target)
        # return Response({"response":result })
    