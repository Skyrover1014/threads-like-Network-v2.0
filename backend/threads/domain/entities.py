# domain/entity/user.py
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Literal
from abc import ABC, abstractmethod
import re
from threads.common.base_exception import DomainValidationError


@dataclass
class User:
    id: int   
    username: str
    email: str
    hashed_password: str = field(repr=False)

    followers_count: int = 0
    followings_count: int = 0
    posts_count: int = 0

    def __post_init__(self):
        self.validate_username()
        self.validate_email()
        self.validate_counters()

    def validate_email(self):
        email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(email_pattern, self.email):
            raise DomainValidationError(message="無效的電子郵件地址")
        
    def validate_username(self):
        if len(self.username) < 5:
            raise DomainValidationError(message="使用者名稱必須至少5個字元")
        if len(self.username) > 15:
            raise DomainValidationError(message="使用者名稱不能超過15個字元")
        if not self.username.isalnum():
            raise DomainValidationError(message="使用者名稱只能包含英文字母和數字")
    def validate_counters(self):
        if self.followers_count < 0 or self.followings_count < 0 or self.posts_count < 0:
            raise DomainValidationError(message="快取欄位不能為負數")


@dataclass
class Follow:
    id:int
    follower_id:int
    following_id:int
    # created_at:datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        self.validate_follow()

    def validate_follow(self):
        if self.following_id == self.follower_id:
            raise DomainValidationError("不能關注自己")

@dataclass
class Like:
    id:int
    user_id:int
    content_item_id:int
    content_type:Literal['post', 'comment']

    def verify_deletable_by(self, deleter):
        if self.user_id != deleter:
           raise DomainValidationError(message="無權限刪除按讚紀錄")
        

    def __post_init__(self):
        self.validate_content_type()

    def validate_content_type(self):
        if self.content_type not in ['post', 'comment']:
            raise DomainValidationError(message="無效的 content_type，必須是 'post' 或 'comment'")


@dataclass
class ContentItem(ABC):
    id:int
    author_id:int
    content:str
    # author_name:str
    author_name:Optional[str] = None
    created_at:Optional[datetime] = None
    updated_at:Optional[datetime] = None

    #快取欄位非核心欄位，不會影響資料庫，真正資料來自Like等表
    likes_count:int = field(default=0)
    comments_count:int = field(default=0)
    reposts_count:int = field(default=0)

    is_liked:bool = field(default=False)

    #具備轉發貼文的性質
    is_repost:bool = field(default=False) #ContentItem是否為轉發
    repost_of:Optional[int] = field(default=None) #ContentItem轉發的原始ContentItemID
    repost_of_content_type:Optional[Literal['post','comment']] = None

    def __post_init__(self):
        self.validate_content()
        self.validate_likes_count()
        self.validate_comments_count()
        self.validate_reposts_count()
        now = datetime.now()
        if self.created_at is None:
            self.created_at = now
        if self.updated_at is None:
            self.updated_at = self.created_at

    def validate_content(self):
        if len(self.content) < 1:
            raise DomainValidationError(message="內容不能為空")
        if len(self.content) > 255:
            raise DomainValidationError(message="內容不能超過255個字元")
    def validate_likes_count(self):
        if self.likes_count < 0:
            raise DomainValidationError(message="喜歡數不能為負數")
    def validate_comments_count(self):
        if self.comments_count < 0:
            raise DomainValidationError(message="評論數不能為負數")
    def validate_reposts_count(self):   
        if self.reposts_count < 0:
            raise DomainValidationError(message="轉發數不能為負數")

    def update_content(self, new_content, editor_id):
        if self.author_id != editor_id:
            raise DomainValidationError(message="無權限修改貼文")
        self.content = new_content
        self.updated_at = datetime.now()
    
    def verify_deletable_by(self, deleter):
        if self.author_id != deleter:
           raise DomainValidationError(message="無權限刪除貼文")
         
@dataclass
class Post(ContentItem):
    pass

@dataclass (kw_only=True)
class Comment(ContentItem):
    parent_post_id:int
    parent_comment_id:Optional[int] = field(default=None) 

