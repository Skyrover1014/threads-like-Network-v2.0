# domain/repository.py
from abc import ABC, abstractmethod
from typing import Optional, List
from .entities import User as DomainUser
from .entities import Follow as DomainFollow
from .entities import ContentItem as DomainContentItem
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

class ContentItemRepository(ABC):
    @abstractmethod
    def create_content_item(self, content_item: DomainContentItem) -> DomainContentItem:
        pass

    @abstractmethod
    def get_content_item_by_id(self, content_item_id:int) -> Optional[DomainContentItem]:
        pass

    @abstractmethod
    def update_content_item(self, content_item: DomainContentItem) -> DomainContentItem:
        pass

    @abstractmethod
    def delete_content_item(self, content_item_id:int) -> None:
        pass

    @abstractmethod
    def get_likes_by_content_item_id(self, content_item_id:int, offset:int, limit:int) -> List[DomainLike]:
        pass

    @abstractmethod
    def get_comments_by_content_item_id(self, content_item_id:int, offset:int, limit:int) -> List[DomainComment]:
        pass
    
    @abstractmethod #取得作者的所有貼文 -> 支援profile頁面貼文和following頁面貼文
    def get_content_items_by_author_id(self, author_id:int, offset:int, limit:int) -> List[DomainContentItem]:
        pass

    @abstractmethod
    def get_comments_count_by_content_item_id(self, content_item_id:int) -> int:
        pass
    
    @abstractmethod
    def get_likes_count_by_content_item_id(self, content_item_id:int) -> int:
        pass
    
    @abstractmethod
    def get_reposts_count_by_content_item_id(self, content_item_id:int) -> int:
        pass

    
class LikeRepository(ABC):
    @abstractmethod
    def create_like(self, user_id:int, content_item_id:int) -> DomainLike:
        pass
    
    @abstractmethod
    def delete_like(self, user_id:int, content_item_id:int) -> None:
        pass