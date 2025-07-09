
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated


from .comment_baseView import CommentBaseView
from ..Serializers.comment_serializer import CommentSerializer, CreateCommentSerializer

from threads.infrastructure.repository.comment_repository import CommentRepositoryImpl
from threads.use_cases.commands.create_comment import CreateComment
from threads.use_cases.queries.get_comments_by_post_id import GetCommentsByPostId



class CommentListCreateView(CommentBaseView):
    permission_classes = [IsAuthenticated]

    def post(self, request, post_id):
        serializers = CreateCommentSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)

        author_id = serializers.validated_data["author_id"]
        content = serializers.validated_data["content"]

        try:
            comment = CreateComment(CommentRepositoryImpl()).execute(author_id=author_id, content=content, parent_post_id=post_id, parent_comment_id=None)
        except Exception as e:
            return self._handler_exception(e)
        return Response({"message": "Comment created successfully"}, status=status.HTTP_200_OK)
    
    def get(self, request, post_id):

        auth_user_id = request.user.id
        offset = int(request.query_params.get("offset", 0))
        limit = int(request.query_params.get("limit", 10))

        repo = CommentRepositoryImpl()
        try:
            domain_comments = GetCommentsByPostId(repo).execute(auth_user_id, post_id, offset, limit)
        except Exception as e:
            return self._handler_exception(e)
        
        
        serializers = CommentSerializer(domain_comments, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)
    