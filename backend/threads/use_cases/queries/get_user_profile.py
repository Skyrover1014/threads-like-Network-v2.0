from threads.domain.repository import UserRepository
from threads.domain.entities import User as DomainUser
from typing import Optional

class GetUserProfile:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        
    def execute(self, user_id: int) -> Optional[DomainUser]:
        return self.user_repository.get_user_by_id(user_id)