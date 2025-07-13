from threads.domain.entities import Comment as DomainComment
from threads.domain.repository import CommentRepository


from threads.models import User as DatabaseUser
from threads.models import Post as DatabasePost
from threads.models import Comment as DatabaseComment

from threads.infrastructure.repository.content_base_repository import ContentBaseRepository


from django.db import DatabaseError, transaction
from threads.common.exceptions.repository_exceptions import EntityDoesNotExist, EntityOperationFailed, InvalidEntityInput, InvalidOperation
from typing import Optional, List



class CommentRepositoryImpl(CommentRepository, ContentBaseRepository):
    def get_comment_by_id(self, comment_id: int, auth_user_id: int) -> Optional[DomainComment]:
        try:
            db_comment = DatabaseComment.objects.annotate(
                is_liked = self._annotate_is_liked_for_content("comment", auth_user_id)
            ).get(id = comment_id)
        except DatabaseComment.DoesNotExist:
            raise EntityDoesNotExist(message="留言不存在")
        except DatabaseError:
            raise EntityOperationFailed(message="資料庫操作失敗")
        except EntityOperationFailed as e:
            raise
        
        try:
            return self._decode_orm_comment(db_comment)
        except InvalidEntityInput as e:
            raise
    
    def create_comment(self, comment: DomainComment) -> DomainComment:
        if not DatabaseUser.objects.filter(id=comment.author_id).exists():
            raise EntityDoesNotExist(message="使用者不存在")
        if comment.parent_post_id and not DatabasePost.objects.filter(id=comment.parent_post_id).exists():
            raise EntityDoesNotExist(message="貼文不存在")
        if comment.parent_comment_id and not DatabaseComment.objects.filter(id=comment.parent_comment_id).exists():
            raise EntityDoesNotExist(message="留言不存在")
        
        with transaction.atomic():
            try:
                db_comment = DatabaseComment.objects.create(
                    author_id = comment.author_id,
                    content = comment.content,
                    parent_post_id = comment.parent_post_id,
                    parent_comment_id = comment.parent_comment_id
                )
            except DatabaseError:
                raise EntityOperationFailed(message="資料庫操作失敗")
            
            try:
                self.adjust_comments_count(parent_post_id=comment.parent_post_id, parent_comment_id=comment.parent_comment_id, delta= 1)
            except InvalidOperation as e:
                raise
        try:
            return self._decode_orm_comment(db_comment)
        except InvalidEntityInput as e:
            raise

    def update_comment(self, comment: DomainComment) -> Optional[DomainComment]:
        db_comment = DatabaseComment.objects.get(id = comment.id)
        db_comment.content = comment.content
        db_comment.updated_at = comment.updated_at

        try:
            db_comment.save()
        except DatabaseError:
            raise EntityOperationFailed(message="資料庫操作失敗")
        
        try:
            return self._decode_orm_comment(db_comment)
        except InvalidEntityInput as e:
            raise
    
    def delete_comment(self, comment: DomainComment) -> None:    
        with transaction.atomic():
            if comment.is_repost == True:
                try:
                    self.adjust_reposts_count(comment.repost_of, comment.repost_of_content_type, delta= -1)
                except InvalidOperation as e:
                    raise
                except InvalidEntityInput as e:
                    raise
                
            try:
                self.adjust_comments_count(parent_post_id=comment.parent_post_id, parent_comment_id=comment.parent_comment_id, delta= -1)
            except InvalidOperation as e:
                raise
            
            db_comment = DatabaseComment.objects.get(id = comment.id)
            try:
                db_comment.delete()
            except DatabaseError:
                raise EntityOperationFailed(message="資料庫操作失敗")
        return None
    
    #組裝貼文的留言
    def get_comments_by_post_id(self, auth_user_id:int, post_id:int, offset:int, limit:int) -> List[DomainComment]:
        if post_id and not DatabasePost.objects.filter(id=post_id).exists():
            raise EntityDoesNotExist(message="貼文不存在")
        try:
            db_comments = DatabaseComment.objects.filter(parent_post_id= post_id).annotate(
                is_liked = self._annotate_is_liked_for_content("comment", auth_user_id)
            ).order_by('created_at')[offset:offset+limit]
        except DatabaseError:
            raise EntityOperationFailed(message="資料庫操作失敗")
        except InvalidEntityInput as e:
            raise
        try:
            return [self._decode_orm_comment(db_comment) for db_comment in db_comments]
        except InvalidEntityInput as e:
            raise
    
    def get_all_child_comments_by_comment_id(self, auth_user_id:int, comment:DomainComment, offset:int, limit:int) -> List[DomainComment]:
        try:
            db_comments = DatabaseComment.objects.filter(parent_comment_id = comment.id).annotate(
                is_liked = self._annotate_is_liked_for_content("comment", auth_user_id)
            ).order_by("-created_at")[offset:offset+limit]
        except DatabaseError :
            raise EntityOperationFailed(message="資料庫操作失敗")
        except InvalidEntityInput as e:
            raise

        try:
            return [self._decode_orm_comment(db_comment) for db_comment in db_comments]
        except InvalidEntityInput as e:
            raise
        
    def repost_comment(self, comment: DomainComment) -> DomainComment:
        try:
            repost_of_content_type = self.get_content_type_from_literal(comment.repost_of_content_type)
        except ValueError as e:
            raise InvalidOperation(message="轉換 ContentType 失敗") from e
       
        with transaction.atomic():
            db_comment = DatabaseComment.objects.create(
                author_id=comment.author_id,
                content=comment.content,
                is_repost= comment.is_repost,
                repost_of_content_type= repost_of_content_type,
                repost_of_content_item_id= comment.repost_of,
                parent_post_id=comment.parent_post_id,
                parent_comment_id = comment.parent_comment_id
            )
            
            try:
                self.adjust_comments_count(parent_post_id=comment.parent_post_id, parent_comment_id=comment.parent_comment_id, delta= 1)
            except InvalidEntityInput as e:
                raise

            try:
                self.adjust_reposts_count(comment.repost_of, comment.repost_of_content_type, delta=1)
            except InvalidEntityInput as e:
                raise
            except InvalidOperation as e:
                raise
        try:
            return self._decode_orm_comment(db_comment)
        except InvalidEntityInput as e:
            raise

    