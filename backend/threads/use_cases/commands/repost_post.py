from threads.domain.entities import Post as DomainPost
from threads.domain.entities import Comment as DomainComment
from threads.domain.repository import PostRepository, CommentRepository
from typing import Literal, Optional, Union, NamedTuple

from django.db import transaction


class RepostResult(NamedTuple):
    repost: DomainPost
    original: Union[DomainPost, DomainComment]

class CreateRePost:
    def __init__(self, post_repository: PostRepository, comment_repository: Optional[CommentRepository] = None):
        self.post_repository = post_repository
        self.comment_repository = comment_repository
    
    def execute(self, author_id:int, content:str, is_repost:bool, repost_of:int, repost_of_content_type: Literal["post", "comment"] ) -> RepostResult:
        try:
            repost_entity = DomainPost(
                id=None, author_id=author_id, content=content, 
                is_repost=is_repost, 
                repost_of_content_type=repost_of_content_type,
                repost_of = repost_of ) 
        except ValueError as e:
            raise
        with transaction.atomic():
            created_repost = self.post_repository.repost_post(repost_entity)

            if repost_of_content_type == "post":
                original = self.post_repository.get_post_by_id(repost_of)
            elif repost_of_content_type == "comment":
                original = self.comment_repository.get_comment_by_id(repost_of)
            else:
                raise ValueError("Unsupported content type!")
        return RepostResult(repost=created_repost, original=original)
