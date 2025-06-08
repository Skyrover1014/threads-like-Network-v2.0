import hashlib
from threads.domain.entities import User as DomainUser
from threads.domain.repository import UserRepository

class RegisterUser:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        
    def execute(self, username: str, email: str, password: str) -> DomainUser:

        if password is None or len(password) < 3:
            raise ValueError("密碼必須至少8個字元")
        hashed_password = hashlib.sha256(password.encode()).hexdigest()

        try:
            new_user = DomainUser(id=None, username=username, email=email, hashed_password=hashed_password)
        except ValueError as e:
            raise
        return self.user_repository.create_user(new_user)
