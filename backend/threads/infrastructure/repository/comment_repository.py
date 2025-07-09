from threads.domain.entities import Comment as DomainComment
from threads.domain.repository import CommentRepository


from threads.models import User as DatabaseUser
from threads.models import Post as DatabasePost
from threads.models import Comment as DatabaseComment

from threads.infrastructure.repository.content_base_repository import ContentBaseRepository


from django.db import DatabaseError, transaction
from threads.common.exceptions import EntityOperationFailed, EntityDoesNotExist
from typing import Optional, List



class CommentRepositoryImpl(CommentRepository, ContentBaseRepository):
    def get_comment_by_id(self, comment_id: int, auth_user_id: int) -> Optional[DomainComment]:
        try:
            db_comment = DatabaseComment.objects.annotate(
                is_liked = self._annotate_is_liked_for_content("comment", auth_user_id)
            ).get(id = comment_id)
        except DatabaseComment.DoesNotExist:
            raise EntityDoesNotExist("留言不存在")
        except DatabaseError:
            raise EntityOperationFailed("資料庫操作失敗")
        return self._decode_orm_comment(db_comment)
    
    def create_comment(self, comment: DomainComment) -> DomainComment:
        with transaction.atomic():
            try:
                db_comment = DatabaseComment.objects.create(
                    author_id = comment.author_id,
                    content = comment.content,
                    parent_post_id = comment.parent_post_id,
                    parent_comment_id = comment.parent_comment_id
                )
                self.adjust_comments_count(parent_post_id=comment.parent_post_id, parent_comment_id=comment.parent_comment_id, delta= 1)

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
                self.adjust_comments_count(parent_post_id=comment.parent_post_id, parent_comment_id=comment.parent_comment_id, delta= -1)
                db_comment = DatabaseComment.objects.get(id = comment.id)
                db_comment.delete()
            except DatabaseComment.DoesNotExist:
                raise EntityDoesNotExist("留言不存在")
            except DatabaseError:
                raise EntityOperationFailed("資料庫操作失敗")
        return None
    
      #組裝貼文的留言
    def get_comments_by_post_id(self, auth_user_id:int, post_id:int, offset:int, limit:int) -> List[DomainComment]:
        db_comments =DatabaseComment.objects.filter(parent_post_id= post_id).annotate(
            is_liked = self._annotate_is_liked_for_content("comment", auth_user_id)
        ).order_by('created_at')[offset:offset+limit]
        return [self._decode_orm_comment(db_comment) for db_comment in db_comments]
    
    def get_all_child_comments_by_comment_id(self, auth_user_id:int, comment:DomainComment, offset:int, limit:int) -> List[DomainComment]:
        try:
            db_comments = DatabaseComment.objects.filter(parent_comment_id = comment.id).annotate(
                is_liked = self._annotate_is_liked_for_content("comment", auth_user_id)
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
                self.adjust_comments_count(parent_post_id=comment.parent_post_id, parent_comment_id=comment.parent_comment_id, delta= 1)


            except DatabasePost.DoesNotExist:
                raise EntityDoesNotExist("轉發的貼文不存在")
            except DatabaseError :
                raise EntityOperationFailed("資料庫操作失敗")
        return self._decode_orm_comment(db_comment)

    