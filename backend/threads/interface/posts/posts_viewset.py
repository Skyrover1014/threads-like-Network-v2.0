# views.py
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

from threads.models import Post, Follow
from threads.interface.Serializers.postModel_serializer import PostModelSerializer

class PostViewSet(ModelViewSet):
    serializer_class = PostModelSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        queryset = Post.objects.all().order_by("-created_at")

        author_id = self.request.query_params.get("author_id")
        if author_id:
            return queryset.filter(author__id=author_id)

        following = self.request.query_params.get("following")
        if following == "true":
            following_ids = Follow.objects.filter(follower=user).values_list("following__id", flat=True)
            return queryset.filter(author__id__in=following_ids)

        return queryset

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return Response({"error": "你不能編輯別人的貼文。"}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.author != request.user:
            return Response({"error": "你不能刪除別人的貼文。"}, status=status.HTTP_403_FORBIDDEN)
        return super().destroy(request, *args, **kwargs)