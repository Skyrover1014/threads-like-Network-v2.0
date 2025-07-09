
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated


from .comment_baseView import CommentBaseView
from ..serializers.comment_serializer import CommentSerializer, CreateChildCommentSerializer

from threads.infrastructure.repository.comment_repository import CommentRepositoryImpl
from threads.use_cases.commands.create_comment import CreateComment
from threads.use_cases.queries.get_child_comments_by_comment_id import GetChildCommentsByCommentId



class ChildCommentListCreateView(CommentBaseView):
    permission_classes = [IsAuthenticated]

    def post(self, request, comment_id):
        serializers = CreateChildCommentSerializer(data=request.data)
        serializers.is_valid(raise_exception=True)

        author_id = serializers.validated_data["author_id"]
        content = serializers.validated_data["content"]
        parent_post_id = serializers.validated_data["parent_post_id"]

        try:
            comment = CreateComment(CommentRepositoryImpl()).execute(author_id, content, parent_post_id, comment_id)
        except Exception as e:
            return self._handler_exception(e)
        return Response({"message": "Comment created successfully"}, status=status.HTTP_200_OK)

    def get(self, request, comment_id):
        
        try:
            domain_comment = self._get_comment_by_id(request,comment_id)
        except Exception as e:
            return self._handler_exception(e)
        
        auth_user_id = request.user.id
        offset = int(request.query_params.get("offset", 0))
        limit = int(request.query_params.get("limit", 10))

        try: 
            domain_child_comments = GetChildCommentsByCommentId(CommentRepositoryImpl()).execute(auth_user_id, domain_comment, offset, limit)
        except Exception as e:
            return self._handler_exception(e)
        
        serializers = CommentSerializer(domain_child_comments, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)
