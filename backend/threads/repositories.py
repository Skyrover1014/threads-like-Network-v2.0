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
    
    def get_post_by_id(self, post_id:int, auth_user_id: int) -> Optional[DomainPost]:
        try:
            db_post = DatabasePost.objects.annotate(
                is_liked = Exists(DatabaseLikePost.objects.filter(
                    user=auth_user_id,
                    post=OuterRef('pk')
                ))).get(id=post_id)
        except DatabasePost.DoesNotExist:
            raise EntityDoesNotExist("貼文不存在")
        except DatabaseError :
            raise EntityOperationFailed("資料庫操作失敗")
        return self._decode_orm_post(db_post)
    
    def update_post(self, post: DomainPost) -> Optional[DomainPost]:
        try:
            db_post = DatabasePost.objects.get(id=post.id)
        except DatabasePost.DoesNotExist:
            raise EntityDoesNotExist("貼文不存在")
        db_post.content = post.content
        db_post.updated_at = post.updated_at
        db_post.save()
        return self._decode_orm_post(db_post)
    
    def delete_post(self, post: DomainPost) -> None:
        
        with transaction.atomic():
            if post.is_repost == True:
                # original_post = DatabasePost.objects.filter(id=post.repost_of).update(
                #     reposts_count = F("reposts_count") - 1
                # )
                self.adjust_reposts_count(post.repost_of, post.repost_of_content_type, delta= -1)
            try:
                db_post = DatabasePost.objects.get(id=post.id)
            except DatabasePost.DoesNotExist:
                raise EntityDoesNotExist("貼文不存在")
            db_post.delete()
        return None
    
    #組裝貼文的留言
    def get_comments_by_post_id(self, auth_user_id:int, post_id:int, offset:int, limit:int) -> List[DomainComment]:
        db_comments =DatabaseComment.objects.filter(parent_post_id= post_id).annotate(
            is_like = Exists(DatabaseLikeComment.objects.filter(
                user = auth_user_id,
                comment=OuterRef('pk')
            ))
        ).order_by('created_at')[offset:offset+limit]
        return [self._decode_orm_comment(db_comment) for db_comment in db_comments]

    #組裝Home-Page貼文列表
    def get_all_posts(self,auth_user_id:int ,offset:int ,limit:int) -> List[DomainPost]:
        try:
            db_posts = DatabasePost.objects.all().annotate(
                is_liked = Exists(DatabaseLikePost.objects.filter(
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
        return [self._decode_orm_post(db_post) for db_post in db_posts]
    
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
        return [self._decode_orm_post(db_post) for db_post in db_posts]
    

    #轉發貼文
    def repost_post(self, post:DomainPost) -> DomainPost:
        try:
            repost_of_content_type = BaseRepository.get_content_type_from_literal(post.repost_of_content_type)
        except ValueError as e:
            raise EntityOperationFailed("轉換 ContentType 失敗") from e
        
        with transaction.atomic():
            try:
                db_post = DatabasePost.objects.create(
                    author_id=post.author_id,
                    content=post.content,
                    is_repost= post.is_repost,
                    repost_of_content_type= repost_of_content_type,
                    repost_of_content_item_id= post.repost_of
                )
                # db_original_post = DatabasePost.objects.filter(id=post.repost_of).update(
                #     reposts_count= F('reposts_count') + 1
                # )
                self.adjust_reposts_count(post.repost_of, post.repost_of_content_type, delta= 1)
            except DatabasePost.DoesNotExist:
                raise EntityDoesNotExist("轉發的貼文不存在")
            except DatabaseError :
                raise EntityOperationFailed("資料庫操作失敗")
        return self._decode_orm_post(db_post)

class CommentRepositoryImpl(CommentRepository, BaseRepository):
    def get_comment_by_id(self, comment_id: int, auth_user_id: int) -> Optional[DomainComment]:
        try:
            db_comment = DatabaseComment.objects.annotate(
                is_liked = Exists(DatabaseLikeComment.objects.filter(
                    user = auth_user_id,
                    comment = OuterRef('pk')
                ))
            ).get(id = comment_id)
        except DatabaseComment.DoesNotExist:
            raise EntityDoesNotExist("留言不存在")
        except DatabaseError:
            raise EntityOperationFailed("資料庫操作失敗")
        return self._decode_orm_comment(db_comment)
    
    def create_comment(self, comment: DomainComment) -> DomainComment:
        try:
            db_comment = DatabaseComment.objects.create(
                author_id = comment.author_id,
                content = comment.content,
                parent_post_id = comment.parent_post_id,
                parent_comment_id = comment.parent_comment_id
            )
        except DatabaseUser.DoesNotExist:
            raise EntityDoesNotExist("使用者不存在")
        except DatabasePost.DoesNotExist:
            raise EntityDoesNotExist("貼文不存在")
        except DatabaseComment.DoesNotExist:
            raise EntityDoesNotExist("留言不存在")
        except DatabaseError:
            raise EntityOperationFailed("資料庫操作失敗")
        return self._decode_orm_comment(db_comment)

    def update_comment(self, comment: DomainComment) -> Optional[DomainComment]:
        try:
            db_comment = DatabaseComment.objects.get(id = comment.id)
        except DatabaseComment.DoesNotExist:
            raise EntityDoesNotExist("留言不存在")
        except DatabaseError:
            raise EntityOperationFailed("資料庫操作失敗")
        db_comment.content = comment.content
        db_comment.updated_at = comment.updated_at
        db_comment.save()
        return self._decode_orm_comment(db_comment)
    
    def delete_comment(self, comment: DomainComment) -> None:    
        with transaction.atomic():
            if comment.is_repost == True:
                self.adjust_reposts_count(comment.repost_of, comment.repost_of_content_type, delta= -1)
            try:
                db_comment = DatabaseComment.objects.get(id = comment.id)
                db_comment.delete()
            except DatabaseComment.DoesNotExist:
                raise EntityDoesNotExist("留言不存在")
            except DatabaseError:
                raise EntityOperationFailed("資料庫操作失敗")
        return None
    
    def get_all_child_comments_by_comment_id(self, auth_user_id:int, comment:DomainComment, offset:int, limit:int) -> List[DomainComment]:
        try:
            db_comments = DatabaseComment.objects.filter(parent_comment_id = comment.id).annotate(
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
        return [self._decode_orm_comment(db_comment) for db_comment in db_comments]
        
    def repost_comment(self, comment: DomainComment) -> DomainComment:

        try:
            repost_of_content_type = self.get_content_type_from_literal(comment.repost_of_content_type)
        except ValueError as e:
            raise EntityOperationFailed("轉換 ContentType 失敗") from e
        
        with transaction.atomic():
            try:
                db_comment = DatabaseComment.objects.create(
                    author_id=comment.author_id,
                    content=comment.content,
                    is_repost= comment.is_repost,
                    repost_of_content_type= repost_of_content_type,
                    repost_of_content_item_id= comment.repost_of,
                    parent_post_id=comment.parent_post_id,
                    parent_comment_id = comment.parent_comment_id
                )
                self.adjust_reposts_count(comment.repost_of, comment.repost_of_content_type, delta=1)

            except DatabasePost.DoesNotExist:
                raise EntityDoesNotExist("轉發的貼文不存在")
            except DatabaseError :
                raise EntityOperationFailed("資料庫操作失敗")
        return self._decode_orm_comment(db_comment)


class LikeRepositoryImpl(LikeRepository):
    def create_like(self, like: DomainLike) -> DomainLike:
        if like.content_type == "post":
            try:
                with transaction.atomic():
                    db_like = DatabaseLikePost.objects.create(
                        user_id = like.user_id,
                        post_id = like.content_item_id
                    )
                    db_post = DatabasePost.objects.filter(id=like.content_item_id).update(
                        likes_count=F('likes_count') + 1  
                    )
            except IntegrityError:
                raise EntityAlreadyExists("已經按讚過了")
            except DatabasePost.DoesNotExist:
                raise EntityDoesNotExist("貼文不存在")
            except DatabaseError :
                raise EntityOperationFailed("資料庫操作失敗")
        else:
            try:
                 with transaction.atomic():
                    db_like = DatabaseLikeComment.objects.create(
                        user_id = like.user_id,
                        comment_id = like.content_item_id
                    )
                    db_comment = DatabaseComment.objects.get(id=like.content_item_id)
                    db_comment.likes_count += 1
                    db_comment.save()
            except IntegrityError:
                raise EntityAlreadyExists("已經按讚過了")
            except DatabaseComment.DoesNotExist:
                raise EntityDoesNotExist("Comment 不存在")
            except DatabaseError :
                raise EntityOperationFailed("資料庫操作失敗")
        return self._decode_orm_like(db_like) 
    
    def delete_like(self, like: DomainLike) -> None:
        if like.content_type == "post":
            try:
                with transaction.atomic():
                    db_like = DatabaseLikePost.objects.get(id = like.id)
                    db_like.delete()
                    db_post = DatabasePost.objects.filter(id=like.content_item_id).update(
                        likes_count=F('likes_count') - 1  
                    )
            except DatabaseLikePost.DoesNotExist:
                raise EntityDoesNotExist("Post Like 不存在")
            except DatabaseError:
                raise EntityOperationFailed("資料庫操作失敗")
        else:
            try:
                with transaction.atomic():
                    db_like = DatabaseLikeComment.objects.get(id = like.id)
                    db_like.delete()
                    db_comment = DatabaseComment.objects.filter(id=like.content_item_id).update(
                        likes_count=F('likes_count') - 1  
                    )
            except DatabaseLikeComment.DoesNotExist:
                raise EntityDoesNotExist("Comment Like 不存在")
            except DatabaseError:
                raise EntityOperationFailed("資料庫操作失敗") 
        return None
    
    def get_like_by_id(self, user_id:int, content_id: int, content_type: Literal['post','comment']) -> Optional[DomainLike]:
        if content_type == 'post':
            try:
                db_like = DatabaseLikePost.objects.get( user_id = user_id, post_id = content_id)
            except DatabaseLikePost.DoesNotExist:
                raise EntityDoesNotExist("Post Like 紀錄不存在")
            except DatabaseError :
                raise EntityOperationFailed("資料庫操作失敗")
        else: 
            try:
                db_like = DatabaseLikeComment.objects.get(user_id=user_id, comment_id = content_id)
            except DatabaseLikeComment.DoesNotExist:
                raise EntityDoesNotExist("Comment Like 紀錄不存在")
            except DatabaseError :
                raise EntityOperationFailed("資料庫操作失敗")
        return self._decode_orm_like(db_like)
    

        
        
    def _decode_orm_like(self, db_like: Union[DatabaseLikePost, DatabaseLikeComment]) -> DomainLike:
        if isinstance(db_like, DatabaseLikePost):
            return DomainLike(
                id = db_like.id,
                user_id=db_like.user.id,
                content_item_id=db_like.post.id,
                content_type="post"
            )
        elif isinstance(db_like, DatabaseLikeComment):
            return DomainLike(
                id = db_like.id,
                user_id=db_like.user.id,
                content_item_id=db_like.comment.id,
                content_type="comment"
            )
        else:
            raise EntityOperationFailed("不支援的 Like 實體型別")
        
