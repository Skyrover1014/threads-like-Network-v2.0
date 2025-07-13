from typing import Optional, List
from threads.domain.entities import User as DomainUser
from threads.domain.repository import UserRepository

from threads.models import User as DatabaseUser

from django.db import IntegrityError, DatabaseError
# from threads.common.base_exception import EntityAlreadyExists, EntityOperationFailed, EntityDoesNotExist, DomainValidationError

from threads.common.base_exception import DomainValidationError
from threads.common.exceptions.repository_exceptions import EntityAlreadyExists, EntityDoesNotExist, EntityOperationFailed, InvalidEntityInput

class UserRepositoryImpl(UserRepository):
    def create_user(self, user: DomainUser) -> DomainUser:
        try:
            db_user = DatabaseUser.objects.create(
                username=user.username,
                email=user.email,
                hashed_password=user.hashed_password
            )
        
        except IntegrityError as e:
            err_msg = str(e)
            if "username" in err_msg:
                raise EntityAlreadyExists(message="使用者名稱已存在")
            elif "email" in err_msg:
                raise EntityAlreadyExists(message="電子郵件已存在")
       
        except DatabaseError as e:
            raise EntityOperationFailed(message="資料庫操作失敗")
        try:
            return self._decode_orm_user(db_user)
        except InvalidEntityInput as e:
            raise
    
    def get_user_by_id(self, user_id: int) -> Optional[DomainUser]:
        try:
            db_user = DatabaseUser.objects.get(id=user_id)
        except DatabaseUser.DoesNotExist:
            raise EntityDoesNotExist(message="使用者不存在")
        except DatabaseError as e :
            raise EntityOperationFailed(message="資料庫操作失敗")
        try:
            return self._decode_orm_user(db_user)
        except InvalidEntityInput as e:
            raise
        
    # def update_user(self, user: DomainUser) -> DomainUser:
        
    #     try:
    #         db_user = DatabaseUser.objects.get(id=user.id)
    #     except DatabaseUser.DoesNotExist:
    #         raise EntityDoesNotExist(message="使用者不存在",source="[Database_User]")
    #     except DatabaseError :
    #         raise EntityOperationFailed(message="資料庫操作失敗", source="[Database_User]") 
               
    #     db_user.username = user.username
    #     db_user.email = user.email
    #     db_user.hashed_password = user.hashed_password

    #     try:
    #         db_user.save()
    #     except IntegrityError as e:
    #         err_msg = str(e)
    #         if "username" in err_msg:
    #             raise EntityAlreadyExists(message="使用者名稱已存在", source="[Database_User]")
    #         elif "email" in err_msg:
    #             raise EntityAlreadyExists(message="電子郵件已存在",source="[Database_User]")
        
    #     except DatabaseError :
    #         raise EntityOperationFailed(message="資料庫操作失敗", source="[Database_User]") 
        
    #     return self._decode_orm_user(db_user)
        
    # def delete_user(self, user_id: int) -> None:
    #     try:
    #         db_user = DatabaseUser.objects.get(id=user_id)
    #     except DatabaseUser.DoesNotExist:   
    #         raise EntityDoesNotExist(message="使用者不存在",source="[Database_User]")
    #     except DatabaseError :
    #         raise EntityOperationFailed(message="資料庫操作失敗", source="[Database_User]") 
        
    #     try:    
    #         db_user.delete()
    #     except DatabaseError :
    #         raise EntityOperationFailed(message="資料庫操作失敗", source="[Database_User]") 
        
    # def get_followers_count_by_user_id(self, user_id:int) -> int:
    #     try:
    #         return DatabaseUser.objects.get(id=user_id).followers_count
    #     except DatabaseUser.DoesNotExist:
    #         raise EntityDoesNotExist(message="使用者不存在",source="[Database_User]")
    #     except DatabaseError :
    #         raise EntityOperationFailed(message="資料庫操作失敗", source="[Database_User]") 
        
    # def get_followings_count_by_user_id(self, user_id:int) -> int:
    #     try:
    #         return DatabaseUser.objects.get(id=user_id).followings_count
    #     except DatabaseUser.DoesNotExist:
    #         raise EntityDoesNotExist(message="使用者不存在",source="[Database_User]")
    #     except DatabaseError :
    #         raise EntityOperationFailed(message="資料庫操作失敗", source="[Database_User]") 
    
    # def get_posts_count_by_user_id(self, user_id:int) -> int:
    #     try:
    #         return DatabaseUser.objects.get(id=user_id).posts_count
    #     except DatabaseUser.DoesNotExist:
    #         raise EntityDoesNotExist(message="使用者不存在",source="[Database_User]")
    #     except DatabaseError :
    #         raise EntityOperationFailed(message="資料庫操作失敗", source="[Database_User]") 

    def get_following_user_ids(self, user_id: int) -> List[int]:
        try:
            db_user = DatabaseUser.objects.get(id=user_id)
        except DatabaseUser.DoesNotExist:
            raise EntityDoesNotExist(message="使用者不存在")
        except DatabaseError :
            raise EntityOperationFailed(message="資料庫操作失敗") 
        
        followings = db_user.followings.all()
        following_ids = followings.values_list("following_id", flat=True)
        return list(following_ids)


    def _decode_orm_user(self, db_user: DatabaseUser) -> DomainUser:
        try:
            return DomainUser(
                id=db_user.id,
                username=db_user.username,
                email=db_user.email,
                hashed_password=db_user.hashed_password,
                followers_count=db_user.followers_count,
                followings_count=db_user.followings_count,
                posts_count=db_user.posts_count
            )
        except DomainValidationError as e:
            raise InvalidEntityInput (message="資料轉換為 Entity 時失敗")


    