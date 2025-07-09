from typing import Optional, List, Union, Literal
from datetime import datetime
from threads.domain.entities import Like as DomainLike, User as DomainUser
from threads.domain.entities import Post as DomainPost
from threads.domain.entities import Comment as DomainComment



from threads.domain.repository import UserRepository, PostRepository, CommentRepository, LikeRepository
from threads.models import User as DatabaseUser
from threads.models import Post as DatabasePost
from threads.models import Comment as DatabaseComment
from threads.models import LikePost as DatabaseLikePost
from threads.models import LikeComment as DatabaseLikeComment


from django.db import IntegrityError, DatabaseError, OperationalError,transaction
from threads.common.exceptions import EntityAlreadyExists, EntityOperationFailed, EntityDoesNotExist
from django.db.models import Exists, OuterRef, F
from django.contrib.contenttypes.models import ContentType

class BaseRepository:

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

class UserRepositoryImpl(UserRepository):
    def create_user(self, user: DomainUser) -> DomainUser:
        try:
            db_user = DatabaseUser.objects.create(
                username=user.username,
                email=user.email,
                hashed_password=user.hashed_password
            )
        except IntegrityError :
            raise EntityAlreadyExists("使用者名稱或信箱已存在")
        except DatabaseError as e:
            raise EntityOperationFailed("資料庫操作失敗")
        
        return self._decode_orm_user(db_user)
    
    def get_user_by_id(self, user_id: int) -> Optional[DomainUser]:
        try:
            db_user = DatabaseUser.objects.get(id=user_id)
        except DatabaseUser.DoesNotExist:
            raise EntityDoesNotExist("使用者不存在")
        except DatabaseError :
            raise EntityOperationFailed("資料庫操作失敗")
        return self._decode_orm_user(db_user)
        
    def update_user(self, user: DomainUser) -> DomainUser:
        try:
            db_user = DatabaseUser.objects.get(id=user.id)
        except DatabaseUser.DoesNotExist:
            raise EntityDoesNotExist("使用者不存在")
        except DatabaseError :
            raise EntityOperationFailed("資料庫操作失敗")
        
        db_user.username = user.username
        db_user.email = user.email
        db_user.hashed_password = user.hashed_password

        try:
            db_user.save()
        except IntegrityError :
            raise EntityAlreadyExists("使用者名稱或信箱已存在")
        except DatabaseError :
            raise EntityOperationFailed("資料庫操作失敗")
        
        return self._decode_orm_user(db_user)
        
    def delete_user(self, user_id: int) -> None:
        try:
            db_user = DatabaseUser.objects.get(id=user_id)
        except DatabaseUser.DoesNotExist:   
            raise EntityDoesNotExist("使用者不存在")
        except DatabaseError :
            raise EntityOperationFailed("資料庫操作失敗")
        
        try:    
            db_user.delete()
        except DatabaseError :
            raise EntityOperationFailed("資料庫操作失敗")
        
    def get_followers_count_by_user_id(self, user_id:int) -> int:
        try:
            return DatabaseUser.objects.get(id=user_id).followers_count
        except DatabaseUser.DoesNotExist:
            raise EntityDoesNotExist("使用者不存在")
        except DatabaseError :
            raise EntityOperationFailed("資料庫操作失敗")
        
    def get_followings_count_by_user_id(self, user_id:int) -> int:
        try:
            return DatabaseUser.objects.get(id=user_id).followings_count
        except DatabaseUser.DoesNotExist:
            raise EntityDoesNotExist("使用者不存在")
        except DatabaseError :
            raise EntityOperationFailed("資料庫操作失敗")
    
    def get_posts_count_by_user_id(self, user_id:int) -> int:
        try:
            return DatabaseUser.objects.get(id=user_id).posts_count
        except DatabaseUser.DoesNotExist:
            raise EntityDoesNotExist("使用者不存在")
        except DatabaseError :
            raise EntityOperationFailed("資料庫操作失敗")

    def get_following_user_ids(self, user_id: int) -> List[int]:
        try:
            db_user = DatabaseUser.objects.get(id=user_id)
        except DatabaseUser.DoesNotExist:
            raise EntityDoesNotExist("使用者不存在")
        except DatabaseError :
            raise EntityOperationFailed("資料庫操作失敗")
        followings = db_user.followings.all()
        following_ids = followings.values_list("following_id", flat=True)
        return list(following_ids)


    def _decode_orm_user(self, db_user: DatabaseUser) -> DomainUser:
        return DomainUser(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
        )

# class CommentRepositoryImpl(CommentRepository, BaseRepository):
#     def get_comment_by_id(self, comment_id: int, auth_user_id: int) -> Optional[DomainComment]:
#         try:
#             db_comment = DatabaseComment.objects.annotate(
#                 is_liked = Exists(DatabaseLikeComment.objects.filter(
#                     user = auth_user_id,
#                     comment = OuterRef('pk')
#                 ))
#             ).get(id = comment_id)
#         except DatabaseComment.DoesNotExist:
#             raise EntityDoesNotExist("留言不存在")
#         except DatabaseError:
#             raise EntityOperationFailed("資料庫操作失敗")
#         return self._decode_orm_comment(db_comment)
    
#     def create_comment(self, comment: DomainComment) -> DomainComment:
#         with transaction.atomic():
#             try:
#                 db_comment = DatabaseComment.objects.create(
#                     author_id = comment.author_id,
#                     content = comment.content,
#                     parent_post_id = comment.parent_post_id,
#                     parent_comment_id = comment.parent_comment_id
#                 )
#                 self.adjust_comments_count(parent_post_id=comment.parent_post_id, parent_comment_id=comment.parent_comment_id, delta= 1)

#             except DatabaseUser.DoesNotExist:
#                 raise EntityDoesNotExist("使用者不存在")
#             except DatabasePost.DoesNotExist:
#                 raise EntityDoesNotExist("貼文不存在")
#             except DatabaseComment.DoesNotExist:
#                 raise EntityDoesNotExist("留言不存在")
#             except DatabaseError:
#                 raise EntityOperationFailed("資料庫操作失敗")
#         return self._decode_orm_comment(db_comment)

#     def update_comment(self, comment: DomainComment) -> Optional[DomainComment]:
#         try:
#             db_comment = DatabaseComment.objects.get(id = comment.id)
#         except DatabaseComment.DoesNotExist:
#             raise EntityDoesNotExist("留言不存在")
#         except DatabaseError:
#             raise EntityOperationFailed("資料庫操作失敗")
#         db_comment.content = comment.content
#         db_comment.updated_at = comment.updated_at
#         db_comment.save()
#         return self._decode_orm_comment(db_comment)
    
#     def delete_comment(self, comment: DomainComment) -> None:    
#         with transaction.atomic():
#             if comment.is_repost == True:
#                 self.adjust_reposts_count(comment.repost_of, comment.repost_of_content_type, delta= -1)
#             try:
#                 self.adjust_comments_count(parent_post_id=comment.parent_post_id, parent_comment_id=comment.parent_comment_id, delta= -1)
#                 db_comment = DatabaseComment.objects.get(id = comment.id)
#                 db_comment.delete()
#             except DatabaseComment.DoesNotExist:
#                 raise EntityDoesNotExist("留言不存在")
#             except DatabaseError:
#                 raise EntityOperationFailed("資料庫操作失敗")
#         return None
    
#     def get_all_child_comments_by_comment_id(self, auth_user_id:int, comment:DomainComment, offset:int, limit:int) -> List[DomainComment]:
#         try:
#             db_comments = DatabaseComment.objects.filter(parent_comment_id = comment.id).annotate(
#                 is_like = Exists(DatabaseLikeComment.objects.filter(
#                     user = auth_user_id,
#                     comment = OuterRef('pk')
#                 ))
#             ).order_by("-created_at")[offset:offset+limit]
#         except DatabaseUser.DoesNotExist:
#                 raise EntityDoesNotExist("使用者不存在")
#         except DatabaseComment.DoesNotExist:
#                 raise EntityDoesNotExist("留言不存在")
#         except DatabaseError :
#             raise EntityOperationFailed("資料庫操作失敗")
#         return [self._decode_orm_comment(db_comment) for db_comment in db_comments]
        
#     def repost_comment(self, comment: DomainComment) -> DomainComment:

#         try:
#             repost_of_content_type = self.get_content_type_from_literal(comment.repost_of_content_type)
#         except ValueError as e:
#             raise EntityOperationFailed("轉換 ContentType 失敗") from e
        
#         with transaction.atomic():
#             try:
#                 db_comment = DatabaseComment.objects.create(
#                     author_id=comment.author_id,
#                     content=comment.content,
#                     is_repost= comment.is_repost,
#                     repost_of_content_type= repost_of_content_type,
#                     repost_of_content_item_id= comment.repost_of,
#                     parent_post_id=comment.parent_post_id,
#                     parent_comment_id = comment.parent_comment_id
#                 )
#                 self.adjust_reposts_count(comment.repost_of, comment.repost_of_content_type, delta=1)
#                 self.adjust_comments_count(parent_post_id=comment.parent_post_id, parent_comment_id=comment.parent_comment_id, delta= 1)


#             except DatabasePost.DoesNotExist:
#                 raise EntityDoesNotExist("轉發的貼文不存在")
#             except DatabaseError :
#                 raise EntityOperationFailed("資料庫操作失敗")
#         return self._decode_orm_comment(db_comment)

    