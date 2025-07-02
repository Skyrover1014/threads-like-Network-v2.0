from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated



from ..Serializers.post_serializer import PostSerializer
from .post_baseView import PostBaseView

from threads.repositories import PostRepositoryImpl
from threads.use_cases.queries.get_post_by_id import GetPostById
from threads.use_cases.commands.update_post import UpdatePost
from threads.use_cases.commands.delete_post import DeletePost


class PostDetailView(PostBaseView):
    permission_classes = [IsAuthenticated]

    def _get_post_by_id(self, request, post_id):
        return  GetPostById(PostRepositoryImpl()).execute(post_id, request.user.id)   

    def get(self, request, post_id):
        try:
            domain_post =  self._get_post_by_id(request, post_id)
        except Exception as e:
            return self._handler_exception(e)
        serializers = PostSerializer(domain_post)
        return Response(serializers.data, status=status.HTTP_200_OK)
    
    def patch(self, request, post_id):
        try:
            old_domain_post = self._get_post_by_id(request, post_id)
        except Exception as e:
            return self.handler_exception(e)
        
        serializers = PostSerializer(old_domain_post, data=request.data, partial = True)
        serializers.is_valid(raise_exception=True)
        data = serializers.validated_data

        try:
            old_domain_post.update_content(data.get("content",old_domain_post.content), request.user.id)
        except Exception as e:
            return self._handler_exception(e)
        
        updated = UpdatePost(PostRepositoryImpl()).execute(old_domain_post)
        return Response(PostSerializer(updated).data, status=status.HTTP_200_OK)
    
    def delete(self, request, post_id):
        try:
            target_domain_post = self._get_post_by_id(request, post_id) 
        except Exception as e:
            return self._handler_exception(e) 
        try: 
            target_domain_post.verify_deletable_by(request.user.id)
        except Exception as e:
            return self._handler_exception(e)

        DeletePost(PostRepositoryImpl()).execute(target_domain_post)
        return Response({"message":"Post deleted successfully"},status=status.HTTP_204_NO_CONTENT)
