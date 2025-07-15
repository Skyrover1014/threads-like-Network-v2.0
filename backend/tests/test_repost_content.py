
from unittest.mock import Mock
from threads.use_cases.commands.repost_content import CreateRePost, RepostTarget, RepostResult
from threads.domain.entities import Post as DomainPost


# Create your tests here.
def test_execute_successful_post_repost():
    post_repo = Mock()
    comment_repo = Mock()
    use_case = CreateRePost(post_repository=post_repo, comment_repository=comment_repo)

    mock_original_post = DomainPost(
        id=1,
        author_id=10,
        # author_name="test_user",
        content="This is a mock post",
        likes_count=0,
        comments_count=0,
        reposts_count=0,
        is_repost=False,
        repost_of=None,
        repost_of_content_type=None
    )
    post_repo.get_post_by_id.return_value = mock_original_post

    mock_repost = DomainPost(
        id=2,
        author_id=10,
        # author_name="test_user",
        content="Reposting this!",
        likes_count=0,
        comments_count=0,
        reposts_count=0,
        is_repost=True,
        repost_of=1,
        repost_of_content_type="post"
    )
    post_repo.repost_post.return_value = mock_repost

    result = use_case.execute(
        author_id=10,
        content="Reposting this!",
        repost_of=1,
        repost_of_content_type="post",
        target=RepostTarget(target_type="post")
    )

    assert isinstance(result, RepostResult)
    assert result.repost.id == 2
    assert result.repost.is_repost is True
    assert result.repost.repost_of == 1
    assert result.original == mock_original_post