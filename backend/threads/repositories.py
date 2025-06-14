from typing import Optional, List
from datetime import datetime
from threads.domain.entities import User as DomainUser
from threads.domain.entities import Post as DomainPost
from threads.domain.entities import Comment as DomainComment



from threads.domain.repository import UserRepository, PostRepository, CommentRepository
from threads.models import User as DatabaseUser
from threads.models import Post as DatabasePost
from threads.models import Comment as DatabaseComment
from threads.models import LikePost as DatabaseLikePost
from threads.models import LikeComment as DatabaseLikeComment


from django.db import IntegrityError, DatabaseError, OperationalError,transaction
from threads.common.exceptions import EntityAlreadyExists, EntityOperationFailed, EntityDoesNotExist
from django.db.models import Exists, OuterRef
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
            is_like = getattr(db_post, 'is_liked', False)
        )
    
    def _decode_orm_comment(self, db_comment:DatabaseComment) -> DomainComment:
        return DomainComment(
            id=db_comment.id,
            author=db_comment.author_id,
            content=db_comment.content,
            created_at=db_comment.created_at,
            updated_at=db_comment.updated_at,
            likes_count=db_comment.likes_count,
            comments_count=db_comment.comments_count,
            reposts_count=db_comment.reposts_count,
            is_repost=db_comment.is_repost,
            repost_of=db_comment.repost_of_content_item_id,
            repost_of_content_type=db_comment.repost_of_content_type,
            parent_post=db_comment.parent_post.id,
            parent_comment=db_comment.parent_comment.id if db_comment.parent_comment else None,
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

    def _decode_orm_user(self, db_user: DatabaseUser) -> DomainUser:
        return DomainUser(
            id=db_user.id,
            username=db_user.username,
            email=db_user.email,
            hashed_password=db_user.hashed_password,
        )

class PostRepositoryImpl(PostRepository, BaseRepository):
    #基本創建貼文、更新貼文和刪除貼文
    def create_post(self, post: DomainPost) -> DomainPost:
        if not DatabaseUser.objects.filter(id=post.author_id).exists():
            raise EntityDoesNotExist("使用者不存在")
        try:
            db_post = DatabasePost.objects.create(
                author_id=post.author_id,
                content=post.content,
            )
        except DatabaseError :
            raise EntityOperationFailed("資料庫操作失敗")
        return self._decode_orm_post(db_post)
    
    def get_post_by_id(self, post_id:int) -> Optional[DomainPost]:
        try:
            db_post = DatabasePost.objects.get(id=post_id)
        except DatabasePost.DoesNotExist:
            raise EntityDoesNotExist("貼文不存在")
        except DatabaseError :
            raise EntityOperationFailed("資料庫操作失敗")
        return self._decode_orm_post(db_post)
    
    def update_post(self, post: DomainPost) -> DomainPost:
        try:
            db_post = DatabasePost.objects.get(id=post.id)
        except DatabasePost.DoesNotExist:
            raise EntityDoesNotExist("貼文不存在")
        db_post.content = post.content
        db_post.updated_at = post.updated_at
        db_post.save()
        return self._decode_orm_post(db_post)
    
    def delete_post(self,user_id:int, post_id:int) -> None:

        try:
            db_post = DatabasePost.objects.get(id=post.id)
        except DatabasePost.DoesNotExist:
            raise EntityDoesNotExist("貼文不存在")
        db_post.delete()
        return None
    
    #組裝貼文的留言
    def get_comments_by_post_id(self, auth_user_id:int, post_id:int,offset:int,limit:int) -> List[DomainComment]:
        db_comments = self.get_post_by_id(post_id).post_comments.all().annotate(
            is_like = Exists(DatabaseLikeComment.objects.filter(
                user = auth_user_id,
                comment=OuterRef('pk')
            ))
        ).order_by('created_at')[offset:offset+limit]
        return [BaseRepository._decode_orm_comment(db_comment) for db_comment in db_comments]

    #組裝Home-Page貼文列表
    def get_all_posts(self,auth_user_id:int ,offset:int ,limit:int) -> List[DomainPost]:
        try:
            db_posts = DatabasePost.objects.all().annotate(
                is_like = Exists(DatabaseLikePost.objects.filter(
                    user=auth_user_id,
                    post=OuterRef('pk')
                ))
            ).order_by('created_at')[offset:offset+limit]
        except DatabaseError:
            raise EntityOperationFailed("資料庫操作失敗")
        return [self._decode_orm_post(db_post) for db_post in db_posts]

    #組裝Profile-Page貼文列表
    def get_posts_by_author_id(self, auth_user_id:int, author_id:int, offset:int, limit:int) -> List[DomainPost]:
        try:
            db_posts = DatabasePost.objects.filter(author=author_id).annotate(
                 is_like = Exists(DatabaseLikePost.objects.filter(
                    user=auth_user_id,
                    post=OuterRef('pk')
                ))
            ).order_by('created_at')[offset:offset+limit]
        except DatabaseUser.DoesNotExist:
            raise EntityDoesNotExist("使用者不存在")
        except DatabaseError :
            raise EntityOperationFailed("資料庫操作失敗")
        return [BaseRepository._decode_orm_post(db_post) for db_post in db_posts]
    
    # 組裝追蹤對象們的貼文列表
    def get_posts_by_following_ids(self, auth_user_id:int,following_ids:List[int],offset:int,limit:int) -> List[DomainPost]:
        try:
            db_posts = DatabasePost.objects.filter(author__in=following_ids).annotate(
                 is_like = Exists(DatabaseLikePost.objects.filter(
                    user=auth_user_id,
                    post=OuterRef('pk')
                ))
            ).order_by('created_at')[offset:offset+limit]
        except DatabaseUser.DoesNotExist:
            raise EntityDoesNotExist("使用者不存在")
        except DatabaseError :
            raise EntityOperationFailed("資料庫操作失敗")
        return [BaseRepository._decode_orm_post(db_post) for db_post in db_posts]
    

    #轉發貼文
    def repost_post(self, post:DomainPost) -> DomainPost:
        try:
            repost_of_content_type = BaseRepository.get_content_type_from_literal(post.repost_of_content_type)
        except ValueError as e:
            raise EntityOperationFailed("轉換 ContentType 失敗") from e
        
        try:
            db_post = DatabasePost.objects.create(
                author=post.author_id,
                content=post.content,
                is_repost= post.is_repost,
                repost_of_content_type= repost_of_content_type,
                repost_of_content_item_id= post.repost_of
            )
        except DatabasePost.DoesNotExist:
            raise EntityDoesNotExist("轉發的貼文不存在")
        except DatabaseError :
            raise EntityOperationFailed("資料庫操作失敗")
        return BaseRepository._decode_orm_post(db_post)

class CommentRepositoryImpl(CommentRepository):
    def get_comment_by_id(self, comment_id: int) -> Optional[DomainComment]:
        try:
            db_comment = DatabaseComment.objects.get(id = comment_id)
        except DatabaseComment.DoesNotExist:
            raise EntityDoesNotExist("留言不存在")
        except DatabaseError:
            raise EntityOperationFailed("資料庫操作失敗")
        return BaseRepository._decode_orm_comment(db_comment)
    
    def create_comment(self, comment: DomainComment) -> DomainComment:
        try:
            db_comment = DatabaseComment.objects.create(
                author = comment.author_id,
                content = comment.content,
                parent_post = comment.parent_post_id,
                parent_comment = comment.parent_comment_id
            )
        except DatabaseUser.DoesNotExist:
            raise EntityDoesNotExist("使用者不存在")
        except DatabasePost.DoesNotExist:
            raise EntityDoesNotExist("貼文不存在")
        except DatabaseComment.DoesNotExist:
            raise EntityDoesNotExist("留言不存在")
        except DatabaseError:
            raise EntityOperationFailed("資料庫操作失敗")
        return BaseRepository._decode_orm_comment(db_comment)

    def  update_comment(self, user_id: int, comment: DomainComment) -> DomainComment:
        try:
            db_comment = DatabaseComment.objects.get(id = comment.id)
            if db_comment.author_id == user_id:
                db_comment.content = comment.content
                db_comment.save()
            else:
                raise EntityOperationFailed("無權限更新貼文")
        except DatabaseComment.DoesNotExist:
            raise EntityDoesNotExist("留言不存在")
        except DatabaseError:
            raise EntityOperationFailed("資料庫操作失敗")
        return BaseRepository._decode_orm_comment(db_comment)
    
    def delete_comment(self, user_id: int, comment_id: int) -> None:
        try:
            db_comment = DatabaseComment.objects.get(id = comment_id)
            if db_comment.author_id == user_id: 
                db_comment.delete()
            else:
                raise EntityOperationFailed("無權限更新貼文")
        except DatabaseComment.DoesNotExist:
            raise EntityDoesNotExist("留言不存在")
        except DatabaseError:
            raise EntityOperationFailed("資料庫操作失敗")
        return None
    
    def get_all_child_comments(self, auth_user_id:int, comment:DomainComment, offset:int, limit:int) -> List[DomainComment]:
        try:
            db_comments = DatabaseComment.objects.filter(parent_comment = comment).annotate(
                is_like = Exists(DatabaseLikeComment.objects.filter(
                    user = auth_user_id,
                    comment = OuterRef('pk')
                ))
            ).order_by("-created_at")[offset:offset+limit]
        except DatabaseUser.DoesNotExist:
                raise EntityDoesNotExist("使用者不存在")
        except DatabaseComment.DoesNotExist:
                raise EntityDoesNotExist("留言不存在")
        except DatabaseError :
            raise EntityOperationFailed("資料庫操作失敗")
        return [BaseRepository._decode_orm_comment(db_comment) for db_comment in db_comments]
        
    def repost_comment(self, comment: DomainComment) -> DomainComment:

        try:
            repost_of_content_type = BaseRepository.get_content_type_from_literal(comment.repost_of_content_type)
        except ValueError as e:
            raise EntityOperationFailed("轉換 ContentType 失敗") from e
        
        try:
            db_comment = DatabaseComment.objects.create(
                author=comment.author_id,
                content=comment.content,
                is_repost= comment.is_repost,
                repost_of_content_type= repost_of_content_type,
                repost_of_content_item_id= comment.repost_of
            )
        except DatabasePost.DoesNotExist:
            raise EntityDoesNotExist("轉發的貼文不存在")
        except DatabaseError :
            raise EntityOperationFailed("資料庫操作失敗")
        return BaseRepository._decode_orm_post(db_comment)

