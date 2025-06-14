from threads.domain.entities import Post as DomainPost
from threads.domain.repository import PostRepository

class CreatePost:
    def __init__(self, post_repository: PostRepository):
        self.post_repository = post_repository
    
    def execute(self, author_id:int, content:str ) -> DomainPost:
        try:
            new_post = DomainPost(id=None, author_id=author_id, content=content)
        except ValueError as e:
            raise
        return self.post_repository.create_post(new_post)