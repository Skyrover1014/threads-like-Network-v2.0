from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from threads.infrastructure.external.openai_client import OpenAIClient

class AskGPTView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        prompt = request.data.get("prompt")
        if not prompt:
            return Response({"error": "Missing prompt"}, status=status.HTTP_400_BAD_REQUEST)
        
        openai_client  = OpenAIClient()
        result = openai_client.ask_with_web_search(prompt)
        return Response({"response":result })