from threads.domain.entities import Post as DomainPost
from threads.domain.entities import Comment as DomainComment
from threads.models import Post as DatabasePost
from threads.models import Comment as DatabaseComment
from threads.models import LikePost as DatabaseLikePost
from threads.models import LikeComment as DatabaseLikeComment



from django.db.models import F
from django.contrib.contenttypes.models import ContentType
from threads.common.exceptions import EntityOperationFailed
from django.db.models import Exists, OuterRef




class ContentBaseRepository:

    def _decode_orm_post(self, db_post:DatabasePost) -> DomainPost:
        return DomainPost(
            id=db_post.id,
            author_id=db_post.author_id,
            content=db_post.content,
            created_at=db_post.created_at,
            updated_at=db_post.updated_at,
            likes_count=db_post.likes_count,
            comments_count=db_post.comments_count,
            reposts_count=db_post.reposts_count,
            is_repost=db_post.is_repost,
            repost_of=db_post.repost_of_content_item_id,
            repost_of_content_type= (
                db_post.repost_of_content_type.model if db_post.repost_of_content_type else None
            ),
            is_liked = getattr(db_post, 'is_liked', False)
        )
    
    def _decode_orm_comment(self, db_comment:DatabaseComment) -> DomainComment:
        return DomainComment(
            id=db_comment.id,
            author_id=db_comment.author_id,
            content=db_comment.content,
            created_at=db_comment.created_at,
            updated_at=db_comment.updated_at,
            likes_count=db_comment.likes_count,
            comments_count=db_comment.comments_count,
            reposts_count=db_comment.reposts_count,
            is_repost=db_comment.is_repost,
            repost_of=db_comment.repost_of_content_item_id,
            repost_of_content_type=(
                db_comment.repost_of_content_type.model
                if db_comment.repost_of_content_type else None
            ),
            parent_post_id=db_comment.parent_post.id,
            parent_comment_id=db_comment.parent_comment.id if db_comment.parent_comment else None,
            is_liked = getattr(db_comment, 'is_liked', False)

        )
    
    @staticmethod
    def get_content_type_from_literal(content_type_literal:str) -> ContentType:
        mapping ={
            "post":DatabasePost,
            "comment":DatabaseComment
        }
        model = mapping.get(content_type_literal)
        if model is None:
            raise ValueError("不支援的ContentType")
        return ContentType.objects.get_for_model(model)

    def adjust_reposts_count(self, repost_of: int, repost_of_content_type:str, delta:int):
        databases = {
            "post": DatabasePost,
            "comment": DatabaseComment
        }
        
        model = databases.get(repost_of_content_type)
        if model is None:
            raise EntityOperationFailed("不支援的轉發來源類型")
    
        model.objects.filter(id=repost_of).update(
            reposts_count = F("reposts_count") + delta
        )
    
    def adjust_comments_count(self, parent_post_id:int, parent_comment_id:int, delta:int):
        
        if parent_comment_id:
           DatabaseComment.objects.filter(id=parent_comment_id).update(
              comments_count = F("comments_count") + delta 
           )
        DatabasePost.objects.filter(id=parent_post_id).update(
            comments_count = F("comments_count") + delta  
        )


    def _annotate_is_liked_for_content(self, content_type:str, auth_user_id:int):
        databases = {
            "post": (DatabaseLikePost, "post"),
            "comment": (DatabaseLikeComment, "comment"),
        }
        model_info = databases.get(content_type)
        
        if model_info is None:
            raise EntityOperationFailed("不支援的內容類型")
        
        model, content_type_field = model_info
        
        return Exists(model.objects.filter(
            user=auth_user_id,
            **{content_type_field:OuterRef('pk')}
        ))