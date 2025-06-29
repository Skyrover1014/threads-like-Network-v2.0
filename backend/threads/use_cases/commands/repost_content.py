from threads.domain.entities import Post as DomainPost
from threads.domain.entities import Comment as DomainComment
from threads.domain.repository import PostRepository, CommentRepository
from typing import Literal, Optional, Union, NamedTuple
from dataclasses import dataclass

from django.db import transaction


class RepostResult(NamedTuple):
    repost: Union[DomainPost, DomainComment]
    original: Union[DomainPost, DomainComment]

@dataclass
class RepostTarget:
    target_type: Literal['post', 'comment']
    target_post_id: Optional[int] = None 
    target_comment_id: Optional[int] = None 

    def __post_init__(self):
        if self.target_type == "comment" and self.target_post_id is None:
            raise ValueError("轉發為留言時，必須指定 target_post_id")

class CreateRePost:
    def __init__(self, post_repository: Optional[PostRepository] = None, comment_repository: Optional[CommentRepository] = None):
        self.post_repository = post_repository
        self.comment_repository = comment_repository
    
    def _build_repost_entity(self, *, target_type, **kwargs) -> Union[DomainPost, DomainComment]:
        builders = {
            "post": self._build_post_repost,
            "comment": self._build_comment_repost
        }
        param_keys = {
            "post": {"author_id", "content", "repost_of", "repost_of_content_type"},
            "comment": {"author_id", "content", "repost_of", "repost_of_content_type","target"}
        }

        allowed_keys = param_keys[target_type]
        filter_kwargs = {key : value for key, value in kwargs.items() if key in allowed_keys} 

        return builders[target_type](**filter_kwargs)

    
    def _build_post_repost(self, author_id, content, repost_of, repost_of_content_type):
        return DomainPost(
                id=None,
                author_id=author_id,
                content=content,
                is_repost=True,
                repost_of=repost_of,
                repost_of_content_type=repost_of_content_type,
            )
    
    def _build_comment_repost(self, author_id, content, repost_of, repost_of_content_type, target: RepostTarget):
        return DomainComment(
                id=None,
                author_id=author_id,
                content=content,
                is_repost=True,
                repost_of=repost_of,
                repost_of_content_type=repost_of_content_type,
                parent_post_id=target.target_post_id,
                parent_comment_id=target.target_comment_id
            )

    def _get_original_content(self, repost_of_content_type, repost_of, author_id):
        fetchers = {
            "post":self.post_repository.get_post_by_id,
            "comment":self.comment_repository.get_comment_by_id
        }
        if repost_of_content_type not in fetchers:
            raise ValueError(f"Unsupported content_type: {repost_of_content_type}")
        
        fetcher = fetchers[repost_of_content_type]
        return fetcher(repost_of, author_id)


    def execute(self, author_id:int, content:str, repost_of:int, repost_of_content_type: Literal["post", "comment"],target: RepostTarget) -> RepostResult:
        repost_entity = self._build_repost_entity(
            target_type = target.target_type,
            author_id = author_id,
            content = content,
            repost_of = repost_of,
            repost_of_content_type = repost_of_content_type,
            target = target
        )

        with transaction.atomic():
            creator_map = {
                "post": self.post_repository.repost_post,
                "comment": self.comment_repository.repost_comment,
            }
            create_func = creator_map[target.target_type]
            created_repost = create_func(repost_entity)

            original = self._get_original_content(repost_of_content_type, repost_of, author_id)
        
        return RepostResult(repost=created_repost, original=original)
