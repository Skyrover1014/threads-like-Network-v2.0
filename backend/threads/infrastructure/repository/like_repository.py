from threads.domain.repository import LikeRepository
from threads.domain.entities import Like as DomainLike

from django.db import IntegrityError, DatabaseError, OperationalError,transaction
from threads.common.exceptions import EntityAlreadyExists, EntityOperationFailed, EntityDoesNotExist

from threads.models import Post as DatabasePost
from threads.models import LikePost as DatabaseLikePost
from threads.models import Comment as DatabaseComment
from threads.models import LikeComment as DatabaseLikeComment


from typing import Optional, List, Union, Literal
from django.contrib.contenttypes.models import ContentType
from django.db.models import F

class LikeBaseRepository:
    
    def _decode_orm_like(self, db_like: Union[DatabaseLikePost, DatabaseLikeComment]) -> DomainLike:
        if isinstance(db_like, DatabaseLikePost):
            return DomainLike(
                id = db_like.id,
                user_id=db_like.user.id,
                content_item_id=db_like.post.id,
                content_type="post"
            )
        else:
            return DomainLike(
                id = db_like.id,
                user_id=db_like.user.id,
                content_item_id=db_like.comment.id,
                content_type="comment"
            )
    
    def check_target_content_exists(self, content_type: str, content_id:int):
        target_databases = {
            "post": DatabasePost,
            "comment": DatabaseComment
        }
        like_databases = {
            "post": DatabaseLikePost,
            "comment": DatabaseLikeComment
        }

        target_db = target_databases[content_type]
        like_db = like_databases[content_type]

        if not target_db.objects.filter(id=content_id).exists():
            raise EntityDoesNotExist(f"{content_type} 不存在")
        
    def switch_like_db(self, content_type:str):
       
        like_model_map = {
            "post": (DatabaseLikePost, "post_id"),
            "comment": (DatabaseLikeComment, "comment_id")
        }

        like_model, target_field = like_model_map[content_type]

        return like_model, target_field
    
    def adjust_likes_count(self, content_type:str, content_id:int, delta:int ):
        target_databases = {
            "post": DatabasePost,
            "comment": DatabaseComment
        }

        model = target_databases[content_type]
        model.objects.filter(id=content_id).update(
            likes_count=F('likes_count') + delta    
        )
    
    
   

class LikeRepositoryImpl(LikeRepository, LikeBaseRepository):
    def create_like(self, like: DomainLike) -> DomainLike:

        self.check_target_content_exists(like.content_type, like.content_item_id)
        
        like_model, target_field  = self.switch_like_db(like.content_type)
        like_kwargs = {
            "user_id":like.user_id,
            target_field:like.content_item_id
        }
        try:
            with transaction.atomic():
                db_like = like_model.objects.create(**like_kwargs)
                self.adjust_likes_count(like.content_type, like.content_item_id, 1)
        except IntegrityError:
                raise EntityAlreadyExists("已經按讚過了")
        except DatabaseError :
            raise EntityOperationFailed("資料庫操作失敗")

        return self._decode_orm_like(db_like)
    
    def delete_like(self, like: DomainLike) -> None:
        
        self.check_target_content_exists(like.content_type, like.content_item_id)
        like_model, _ = self.switch_like_db(like.content_type)

        try:
            with transaction.atomic():
                db_like = like_model.objects.get(id= like.id)
                db_like.delete()
                self.adjust_likes_count(like.content_type, like.content_item_id, -1)
        except DatabaseError:
            raise EntityOperationFailed("資料庫操作失敗")
        
        return None
    
    def get_like_by_id(self, user_id:int, content_id: int, content_type: Literal['post','comment']) -> Optional[DomainLike]:
       
        self.check_target_content_exists(content_type, content_id)
        
        like_model, target_field = self.switch_like_db(content_type)
        like_kwargs = {
            "user_id": user_id,
            target_field: content_id
        }
        
        try:
            db_like = like_model.objects.get(**like_kwargs)
        except DatabaseLikePost.DoesNotExist:
            raise EntityDoesNotExist(f"{content_type} Like 紀錄不存在")
        except DatabaseError :
            raise EntityOperationFailed("資料庫操作失敗") 


        return self._decode_orm_like(db_like)
    

        
        
    