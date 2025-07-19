from threads.domain.repository import LikeRepository
from threads.domain.entities import Like as DomainLike


from django.db import IntegrityError, DatabaseError,transaction
from threads.common.base_exception import DomainValidationError
from threads.common.exceptions.repository_exceptions import EntityAlreadyExists, EntityDoesNotExist, EntityOperationFailed,InvalidEntityInput, InvalidOperation

from threads.models import Post as DatabasePost
from threads.models import LikePost as DatabaseLikePost
from threads.models import Comment as DatabaseComment
from threads.models import LikeComment as DatabaseLikeComment


from typing import Optional, List, Union, Literal
from django.db.models import F

class LikeBaseRepository:
    
    def _decode_orm_like(self, db_like: Union[DatabaseLikePost, DatabaseLikeComment]) -> DomainLike:
        if isinstance(db_like, DatabaseLikePost):
            try:
                return DomainLike(
                    id = db_like.id,
                    user_id=db_like.user.id,
                    content_item_id=db_like.post.id,
                    content_type="post"
                )
            except DomainValidationError as e:
                raise InvalidEntityInput(message=e.message)
            except TypeError as e:
                raise InvalidEntityInput(message=f"封裝 Like 失敗: {str(e)}")
        else:
            try:
                return DomainLike(
                    id = db_like.id,
                    user_id=db_like.user.id,
                    content_item_id=db_like.comment.id,
                    content_type="comment"
                )
            except DomainValidationError as e:
                raise InvalidEntityInput(message=e.message)
            except TypeError as e:
                raise InvalidEntityInput(message=f"封裝 Like 失敗: {str(e)}")
    
    def check_target_content_exists(self, content_type: str, content_id:int):
        target_databases = {
            "post": DatabasePost,
            "comment": DatabaseComment
        }

        if content_type not in target_databases:
            raise InvalidEntityInput(message=f"Unsupported content type: {content_type}")
        target_db = target_databases[content_type]

        if not target_db.objects.filter(id=content_id).exists():
            raise EntityDoesNotExist(message=f"{content_type} 不存在")
        
    def switch_like_db(self, content_type:str):
        like_model_map = {
            "post": (DatabaseLikePost, "post_id"),
            "comment": (DatabaseLikeComment, "comment_id")
        }
        like_model, target_field = like_model_map[content_type]
        return like_model, target_field
    
    def adjust_likes_count(self, content_type:str, content_id:int, delta:int ):
        if not isinstance(delta, int):
            raise InvalidOperation (message=f"快取更新必需是整數1/-1，但收到的是 {type(delta).__name__}")
    
        target_databases = {
            "post": DatabasePost,
            "comment": DatabaseComment
        }
        model = target_databases[content_type]
        
        if model is None:
            raise InvalidEntityInput(message="不支援的內容類型")
        
        try:
            model.objects.filter(id=content_id).update(
                likes_count=F('likes_count') + delta    
            )
        except DatabaseError as e:
            raise InvalidOperation(message="錯誤的快取變動")
    
    
   

class LikeRepositoryImpl(LikeRepository, LikeBaseRepository):
    def create_like(self, like: DomainLike) -> DomainLike:
        try:
            self.check_target_content_exists(like.content_type, like.content_item_id)
        except EntityDoesNotExist as e:
            raise

        like_model, target_field  = self.switch_like_db(like.content_type)
        like_kwargs = {
            "user_id":like.user_id,
            target_field:like.content_item_id
        }
        try:
            with transaction.atomic():
                db_like = like_model.objects.create(**like_kwargs)
                self.adjust_likes_count(like.content_type, like.content_item_id,1)
        except IntegrityError:
                raise EntityAlreadyExists(message="已經按讚過了")
        except DatabaseError :
            raise EntityOperationFailed(message="資料庫操作失敗")
        except InvalidEntityInput as e:
            raise
        except InvalidOperation as e:
            raise
       
        try: 
            db_like = (like_model.objects.select_related('user',like.content_type)
                       .get(**like_kwargs))
        except DatabaseError :
            raise EntityOperationFailed(message="資料庫操作失敗")
        
        try:
            return self._decode_orm_like(db_like)
        except InvalidEntityInput as e:
            raise
    
    def delete_like(self, like: DomainLike) -> None:
        like_model, _ = self.switch_like_db(like.content_type)

        try:
            with transaction.atomic():
                deleted_rows, _ = like_model.objects.filter(id=like.id).delete()
                if not deleted_rows:
                    raise EntityDoesNotExist("Like 不存在")
                self.adjust_likes_count(like.content_type, like.content_item_id, -1)
        except DatabaseError as e:
            raise EntityOperationFailed(message="資料庫操作失敗")
        except InvalidEntityInput as e:
            raise
        except InvalidOperation as e:
            raise
        return None
    
    def get_like_by_id(self, user_id:int, content_id: int, content_type: Literal['post','comment']) -> Optional[DomainLike]:
        try:
            self.check_target_content_exists(content_type, content_id)
        except EntityDoesNotExist as e:
            raise

        like_model, target_field = self.switch_like_db(content_type)
        like_kwargs = {
            "user_id": user_id,
            target_field: content_id
        }
        try:
            db_like = (like_model.objects
                       .select_related('user',content_type)
                       .get(**like_kwargs))
        except like_model.DoesNotExist:
            return None
        except DatabaseError :
            raise EntityOperationFailed(message="資料庫操作失敗") 
        try:
            return self._decode_orm_like(db_like)
        except InvalidEntityInput as e:
            raise
    

        
        
    