# domain/repository.py
from abc import ABC, abstractmethod
from typing import Optional, List, Literal
from .entities import User as DomainUser
from .entities import Follow as DomainFollow
from .entities import Post as DomainPost
from .entities import Comment as DomainComment
from .entities import Like as DomainLike



class UserRepository(ABC):
    @abstractmethod
    def create_user(self, user: DomainUser) -> DomainUser:
        pass
    
    @abstractmethod
    def get_user_by_id(self, user_id: int) -> Optional[DomainUser]:
        pass
    
    @abstractmethod
    def update_user(self, user: DomainUser) -> DomainUser:
        pass
    
    @abstractmethod
    def delete_user(self, user_id: int) -> None:
        pass

    @abstractmethod
    def get_followers_count_by_user_id(self, user_id:int) -> int:
        pass
    
    @abstractmethod
    def get_followings_count_by_user_id(self, user_id:int) -> int:
        pass
    
    @abstractmethod
    def get_posts_count_by_user_id(self, user_id:int) -> int:
        pass

    @abstractmethod
    def get_following_user_ids(self, user_id:int) -> List[int]:
        pass
    

class FollowRepository(ABC):
    @abstractmethod
    def create_follow(self, follower_id:int, following_id:int) -> DomainFollow:
        pass
    
    @abstractmethod
    def delete_follow(self, follower_id:int, following_id:int) -> None:
        pass
    
    @abstractmethod
    def get_followers_by_user_id(self, user_id:int, offset:int, limit:int) -> List[DomainUser]:
        pass
    
    @abstractmethod
    def get_followings_by_user_id(self, user_id:int, offset:int, limit:int) -> List[DomainUser]:
        pass
    
    @abstractmethod
    def is_following(self, follower_id:int, following_id:int) -> bool:
        pass

class PostRepository(ABC):
    @abstractmethod
    def create_post(self, post: DomainPost) -> DomainPost:
        pass

    @abstractmethod
    def get_post_by_id(self, post_id:int, auth_user_id: int) -> Optional[DomainPost]:
        pass

    @abstractmethod
    def update_post(self, post: DomainPost) -> DomainPost:
        pass

    @abstractmethod
    def delete_post(self, user_id:int ,post_id:int) -> None:
        pass

    @abstractmethod
    def get_all_posts(self,auth_user_id:int, offset:int,limit:int) -> List[DomainPost]:
        pass
    
    @abstractmethod #取得作者的所有貼文 -> 支援profile頁面貼文
    def get_posts_by_author_id(self,auth_user_id:int, author_id:int, offset:int, limit:int) -> List[DomainPost]:
        pass
    
    @abstractmethod #取得所有followings的貼文 -> 支援following頁面貼文
    def get_posts_by_following_ids(self,auth_user_id:int, following_ids:List[int], offset:int, limit:int) -> List[DomainPost]:
        pass
    
    @abstractmethod
    def repost_post(self, post:DomainPost) -> DomainPost:
        pass

class CommentRepository(ABC):
    @abstractmethod
    def get_comment_by_id(self, comment_id:int) -> Optional[DomainUser]:
        pass
    
    @abstractmethod
    def create_comment(self, comment:DomainComment) -> DomainComment:
        pass
    
    @abstractmethod
    def update_comment(self, user_id:int, comment:DomainComment) -> DomainComment:
        pass
    @abstractmethod
    def delete_comment(self, user_id:int, comment_id:int) -> None:
        pass

    @abstractmethod
    def get_comments_by_post_id(self,auth_user_id:int, post_id:int, offset:int, limit:int) -> List[DomainComment]:
        pass
    
    @abstractmethod
    def get_all_child_comments_by_comment_id(self,auth_user_id:int, comment_id:int, offset:int, limit:int) -> List[DomainComment]:
        pass
    @abstractmethod
    def repost_comment(self, comment:DomainComment)-> DomainComment:
        pass



class LikeRepository(ABC):
    @abstractmethod
    def create_like(self, like:DomainLike) -> DomainLike:
        pass
    
    @abstractmethod
    def delete_like(self, like:DomainLike) -> None:
        pass

    @abstractmethod
    def get_like_by_id(self, user_id:int, content_id:int,  content_type: Literal['post','comment'] ) -> Optional[DomainLike]:
        pass