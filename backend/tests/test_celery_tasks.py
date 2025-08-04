import pytest
from threads.tasks import add  

def test_add_task_sync():
    result = add.delay(2, 3)
    assert result.get(timeout=10) == 5

# def test_another_task_behavior():
#     # 這裡再測你其他 task 的輸入／輸出
#     # e.g. from threads.tasks import multiply
#     # result = multiply.delay(4, 6)
#     # assert result.get(timeout=5) == 24
#     pass