from rest_framework.permissions import IsAuthenticated
from .repost_baseView import RepostBaseView


class RepostPostView(RepostBaseView):
    permission_classes = [IsAuthenticated]
 
    def post(self, request, post_id):
        return self._handler_post(
            request= request,
            repost_of= post_id,
            repost_of_content_type='post'
        )
       