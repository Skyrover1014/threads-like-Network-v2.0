from threads.domain.entities import Post as DomainPost
from threads.domain.entities import Comment as DomainComment
from threads.models import Post as DatabasePost
from threads.models import Comment as DatabaseComment
from threads.models import LikePost as DatabaseLikePost
from threads.models import LikeComment as DatabaseLikeComment



from django.db.models import F
from django.contrib.contenttypes.models import ContentType
from threads.common.base_exception import DomainValidationError
from threads.common.exceptions.repository_exceptions import InvalidEntityInput, InvalidOperation, EntityOperationFailed
from django.db.models import Exists, OuterRef
from django.db import DatabaseError


from functools import lru_cache




class ContentBaseRepository:

    def _decode_orm_post(self, db_post:DatabasePost) -> DomainPost:
        try:
            return DomainPost(
                id=db_post.id,
                author_id=db_post.author_id,
                author_name=db_post.author.username,
                content=db_post.content,
                created_at=db_post.created_at,
                updated_at=db_post.updated_at,
                likes_count=db_post.likes_count,
                comments_count=db_post.comments_count,
                reposts_count=db_post.reposts_count,
                is_repost=db_post.is_repost,
                repost_of=db_post.repost_of_content_item_id,
                # repost_of_content_type= (
                #     db_post.repost_of_content_type.model if db_post.repost_of_content_type else None
                # ),
                repost_of_content_type = db_post.repost_of_content_type_id,
                is_liked = getattr(db_post, 'is_liked', False)
            )
        except DomainValidationError as e:
            raise InvalidEntityInput(message="Post 資料不符合規則")
        except TypeError as e:
            raise InvalidEntityInput(message=f"封裝 Post 失敗: {str(e)}")
    
    def _decode_orm_comment(self, db_comment:DatabaseComment) -> DomainComment:
        try:
            return DomainComment(
                id=db_comment.id,
                author_id=db_comment.author_id,
                author_name=db_comment.author.username,
                content=db_comment.content,
                created_at=db_comment.created_at,
                updated_at=db_comment.updated_at,
                likes_count=db_comment.likes_count,
                comments_count=db_comment.comments_count,
                reposts_count=db_comment.reposts_count,
                is_repost=db_comment.is_repost,
                repost_of=db_comment.repost_of_content_item_id,
                # repost_of_content_type=(
                #     db_comment.repost_of_content_type.model
                #     if db_comment.repost_of_content_type else None
                # ),
                repost_of_content_type= db_comment.repost_of_content_type_id,
                parent_post_id=db_comment.parent_post.id,
                parent_comment_id=db_comment.parent_comment.id if db_comment.parent_comment else None,
                is_liked = getattr(db_comment, 'is_liked', False)
            )
        except DomainValidationError as e:
            raise InvalidEntityInput(message="Comment 資料不符合規則")
        except TypeError as e:
            raise InvalidEntityInput(message=f"封裝 Comment 失敗: {str(e)}")
    
    @staticmethod
    @lru_cache(maxsize=8)
    def get_content_type_from_literal(content_type_literal:str) -> ContentType:
        mapping ={
            "post":DatabasePost,
            "comment":DatabaseComment
        }
        model = mapping.get(content_type_literal)
        if model is None:
            raise ValueError("不支援的ContentType")
        return ContentType.objects.get_for_model(model)



    def adjust_reposts_count(self, repost_of: int, repost_of_content_type:int, delta:int):
        if not isinstance(delta, int):
            raise InvalidOperation (message=f"快取更新必需是整數1/-1，但收到的是 {type(delta).__name__}")
        
        databases = {
            "post": DatabasePost,
            "comment": DatabaseComment
        }

        # content_type_map = {
        #     4: "comment",
        #     2: "post"
        # }
        # print(f"轉發類型1{repost_of_content_type}",flush=True)
        model = databases.get(repost_of_content_type)
        print(f"轉發類型2{model}",flush=True)
        
        if model is None:
            raise InvalidEntityInput(message="不支援的轉發來源類型")
        try:
            model.objects.filter(id=repost_of).update(
                reposts_count = F("reposts_count") + delta
            )
        except DatabaseError as e:
            raise InvalidOperation(message="錯誤的快取變動")

    def adjust_comments_count(self, parent_post_id:int, parent_comment_id:int, delta:int):
        if not isinstance(delta, int):
            raise InvalidOperation (message=f"快取更新必需是整數1/-1，但收到的是 {type(delta).__name__}")
        
        try:
            if parent_comment_id:
                DatabaseComment.objects.filter(id=parent_comment_id).update(
                    comments_count = F("comments_count") + delta 
                )
            DatabasePost.objects.filter(id=parent_post_id).update(
                comments_count = F("comments_count") + delta  
            )
        except DatabaseError as e:
            raise InvalidOperation(message="錯誤的快取變動")

    def _annotate_is_liked_for_content(self, content_type:str, auth_user_id:int):
        databases = {
            "post": (DatabaseLikePost, "post"),
            "comment": (DatabaseLikeComment, "comment"),
        }
        model_info = databases.get(content_type)
        
        if model_info is None:
            raise InvalidEntityInput(message="不支援的內容類型")
        
        model, content_type_field = model_info
        
        return Exists(model.objects.filter(
            user=auth_user_id,
            **{content_type_field:OuterRef('pk')}
        ))