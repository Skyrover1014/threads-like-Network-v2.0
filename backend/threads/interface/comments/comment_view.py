
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated


from .comment_baseView import CommentBaseView
from ..serializers.comment_serializer import CommentSerializer

from threads.infrastructure.repository.comment_repository import CommentRepositoryImpl
from threads.use_cases.queries.get_comment_by_id import GetCommentById
from threads.use_cases.commands.update_comment import UpdateComment
from threads.use_cases.commands.delete_comment import DeleteComment


class CommentDetailView(CommentBaseView):
    permission_classes = [IsAuthenticated]


    def get(self, request, comment_id):
        try:
            domain_comment = self._get_comment_by_id(request,comment_id)
        except Exception as e:
            return self._handler_exception(e)
        serializers = CommentSerializer(domain_comment)
        return Response(serializers.data, status=status.HTTP_200_OK)
    
    def patch(self, request, comment_id):
        try:
            old_domain_comment = self._get_comment_by_id(request, comment_id)
        except Exception as e:
            return self._handler_exception(e)
        
        serializers = CommentSerializer(old_domain_comment, data=request.data, partial = True)
        serializers.is_valid(raise_exception=True)
        new_data = serializers.validated_data

        try:
            old_domain_comment.update_content(new_data.get("content", old_domain_comment.content), request.user.id)
        except Exception as e:
            return self._handler_exception(e)
        updated = UpdateComment(CommentRepositoryImpl()).execute(old_domain_comment)
        return Response(CommentSerializer(updated).data, status=status.HTTP_200_OK)

    def delete(self, request, comment_id):
        try:
            target_domain_comment = self._get_comment_by_id(request, comment_id)
        except Exception as e:
            return self._handler_exception(e)
        
        try:
            target_domain_comment.verify_deletable_by(request.user.id)
        except Exception as e:
            return self._handler_exception(e)
        
        DeleteComment(CommentRepositoryImpl()).execute(target_domain_comment)
        return Response({"message":"Comment deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

        

        
         