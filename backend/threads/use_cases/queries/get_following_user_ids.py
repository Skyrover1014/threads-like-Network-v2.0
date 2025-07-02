from threads.domain.repository import UserRepository
from typing import List


class GetFollowingUserIds:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def execute(self,auth_user_id:int) -> List[int]: 
        return self.user_repository.get_following_user_ids(auth_user_id)