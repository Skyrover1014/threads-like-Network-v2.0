from threads.domain.repository import PostRepository
from threads.domain.entities import Post as DomainPost
from threads.domain.entities import Comment as DomainComment
from threads.models import Post as DatabasePost
from threads.models import User as DatabaseUser
from threads.models import Comment as DatabaseComment
from threads.infrastructure.repository.content_base_repository import ContentBaseRepository


from threads.common.exceptions import EntityDoesNotExist, EntityOperationFailed
from django.db import DatabaseError,transaction
from typing import Optional, List
    

class PostRepositoryImpl(PostRepository, ContentBaseRepository):
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
                is_liked = self._annotate_is_liked_for_content("post", auth_user_id)
            ).get(id=post_id)
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
                self.adjust_reposts_count(post.repost_of, post.repost_of_content_type, delta= -1)
            try:
                db_post = DatabasePost.objects.get(id=post.id)
            except DatabasePost.DoesNotExist:
                raise EntityDoesNotExist("貼文不存在")
            db_post.delete()
        return None
    
    
    #組裝Home-Page貼文列表
    def get_all_posts(self,auth_user_id:int ,offset:int ,limit:int) -> List[DomainPost]:
        try:
            db_posts = DatabasePost.objects.all().annotate(
                is_liked = self._annotate_is_liked_for_content("post", auth_user_id)
            ).order_by('created_at')[offset:offset+limit]
        except DatabaseError:
            raise EntityOperationFailed("資料庫操作失敗")
        return [self._decode_orm_post(db_post) for db_post in db_posts]

    #組裝Profile-Page貼文列表
    def get_posts_by_author_id(self, auth_user_id:int, author_id:int, offset:int, limit:int) -> List[DomainPost]:
        try:
            db_posts = DatabasePost.objects.filter(author=author_id).annotate(
                is_liked = self._annotate_is_liked_for_content("post", auth_user_id)
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
                is_liked = self._annotate_is_liked_for_content("post", auth_user_id)
            ).order_by('created_at')[offset:offset+limit]
        except DatabaseUser.DoesNotExist:
            raise EntityDoesNotExist("使用者不存在")
        except DatabaseError :
            raise EntityOperationFailed("資料庫操作失敗")
        return [self._decode_orm_post(db_post) for db_post in db_posts]
    

    #轉發貼文
    def repost_post(self, post:DomainPost) -> DomainPost:
        try:
            repost_of_content_type = self.get_content_type_from_literal(post.repost_of_content_type)
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
                self.adjust_reposts_count(post.repost_of, post.repost_of_content_type, delta= 1)
            except DatabasePost.DoesNotExist:
                raise EntityDoesNotExist("轉發的貼文不存在")
            except DatabaseError :
                raise EntityOperationFailed("資料庫操作失敗")
        return self._decode_orm_post(db_post)