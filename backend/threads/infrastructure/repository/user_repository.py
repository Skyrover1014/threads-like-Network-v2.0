from typing import Optional, List
from threads.domain.entities import User as DomainUser
from threads.domain.repository import UserRepository

from threads.models import User as DatabaseUser

from django.db import IntegrityError, DatabaseError
from threads.common.exceptions import EntityAlreadyExists, EntityOperationFailed, EntityDoesNotExist



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


    