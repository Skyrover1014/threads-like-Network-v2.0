from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated

from threads.infrastructure.like_repository import LikeRepositoryImpl

from ..Serializers.like_serializer import LikeSerializer
from .like_baseView import LikeBaseView

from threads.use_cases.queries.get_like_by_id import GetLikeById
from threads.use_cases.commands.create_like import CreateLike
from threads.use_cases.commands.delete_like import DeleteLike

class LikeContentView(LikeBaseView):
    permission_classes=[IsAuthenticated]

    def get (self, request, content_id,content_type):

        user_id = request.user.id
        try:
            domain_like = GetLikeById(LikeRepositoryImpl()).execute(user_id, content_id, content_type)
        except Exception as e:
            return self._handler_exception(e)
        
        serializers = LikeSerializer(domain_like)
        return Response(serializers.data, status=status.HTTP_200_OK)
        
    def post(self, request, content_id, content_type):
       
        data = {
            'user_id': request.user.id,
            'content_item_id': content_id,
            'content_type': content_type
        }

        serializers = LikeSerializer(data=data)
        serializers.is_valid(raise_exception=True)

        user_id = serializers.validated_data['user_id']
        content_id = serializers.validated_data['content_item_id']
        content_type = serializers.validated_data['content_type']

        try:
            like = CreateLike(LikeRepositoryImpl()).execute(user_id, content_id, content_type)
        except Exception as e:
            return self._handler_exception(e)
        return Response({"message": "Liked Successfully"}, status=status.HTTP_201_CREATED)
    
    def delete (self, request, content_id, content_type):

        user_id = request.user.id
        try:
            domain_like = GetLikeById(LikeRepositoryImpl()).execute(user_id, content_id, content_type)
        except Exception as e:
            return self._handler_exception(e)

        try: 
            domain_like.verify_deletable_by(request.user.id)
        except Exception as e:
            return self._handler_exception(e)
        try:
            delete_lke = DeleteLike(LikeRepositoryImpl()).execute(domain_like)
        except Exception as e:
           return self._handler_exception(e)
        return Response({"message":"Like deleted successfully"},status=status.HTTP_204_NO_CONTENT)
 
        