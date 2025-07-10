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
    