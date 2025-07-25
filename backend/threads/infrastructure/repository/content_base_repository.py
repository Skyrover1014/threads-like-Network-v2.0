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

    _content_type_literals = {}
    _content_type_ids = {}

    @classmethod
    @lru_cache(maxsize=8)
    def get_content_type_from_literal(cls, content_type_literal: str) -> ContentType:
        if content_type_literal not in cls._content_type_literals:
            cls._content_type_literals = {
                "post": ContentType.objects.get_for_model(DatabasePost),
                "comment": ContentType.objects.get_for_model(DatabaseComment)
            }
        try:
            return cls._content_type_literals[content_type_literal]
        except KeyError:
            raise ValueError("不支援的 ContentType")

    @staticmethod
    @lru_cache(maxsize=8)
    def get_content_type_from_ids(content_type_id:int) -> ContentType:
        CONTENT_TYPE_IDS = {
            ContentType.objects.get_for_model(DatabasePost).id: "post",
            ContentType.objects.get_for_model(DatabaseComment).id: "comment"
        }
        try:
            return CONTENT_TYPE_IDS[content_type_id]
        except KeyError:
            raise InvalidEntityInput(f"找不到 ContentType，id={content_type_id}")

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
                repost_of_content_type=(
                    self.get_content_type_from_ids(db_post.repost_of_content_type_id)
                    if db_post.is_repost == True else None
                ),
                is_liked = getattr(db_post, 'is_liked', False)
            )
        except DomainValidationError as e:
            raise InvalidEntityInput(message="Post 資料不符合規則")
        except TypeError as e:
            raise InvalidEntityInput(message=f"封裝 Post 失敗: {str(e)}")
    
    def _decode_orm_comment(self, db_comment:DatabaseComment) -> DomainComment:
        print(f"content_type_id:{db_comment.repost_of_content_type_id}", flush=True)
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
                repost_of_content_type=(
                    self.get_content_type_from_ids(db_comment.repost_of_content_type_id)
                    if db_comment.is_repost == True else None
                ),
                parent_post_id=db_comment.parent_post.id,
                parent_comment_id=db_comment.parent_comment.id if db_comment.parent_comment else None,
                is_liked = getattr(db_comment, 'is_liked', False)
            )
        except DomainValidationError as e:
            raise InvalidEntityInput(message="Comment 資料不符合規則")
        except TypeError as e:
            raise InvalidEntityInput(message=f"封裝 Comment 失敗: {str(e)}")
    
    def adjust_reposts_count(self, repost_of: int, repost_of_content_type:str, delta:int):
        if not isinstance(delta, int):
            raise InvalidOperation (message=f"快取更新必需是整數1/-1，但收到的是 {type(delta).__name__}")
        
        databases = {
            "post": DatabasePost,
            "comment": DatabaseComment
        }

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