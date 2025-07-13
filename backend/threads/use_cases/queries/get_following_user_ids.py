from threads.domain.repository import UserRepository
from typing import List

from threads.common.exceptions.repository_exceptions import EntityOperationFailed
from threads.common.exceptions.use_case_exceptions import ServiceUnavailable

class GetFollowingUserIds:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
    
    def execute(self,auth_user_id:int) -> List[int]:
        try:
            return self.user_repository.get_following_user_ids(auth_user_id)
        # except EntityDoesNotExist as e:
        #     raise NotFound(message=e.message)
        except EntityOperationFailed as e:
            raise ServiceUnavailable