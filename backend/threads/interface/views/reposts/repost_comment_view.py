from rest_framework.permissions import IsAuthenticated
from .repost_baseView import RepostBaseView


class RepostCommentView(RepostBaseView):
    permission_classes = [IsAuthenticated]
 
    def post(self, request, comment_id):
        return self._handler_post(
            request =request,
            repost_of= comment_id,
            repost_of_content_type='comment'
        )