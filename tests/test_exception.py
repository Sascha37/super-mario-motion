import pytest
from super_mario_motion import main


def test_exception():
    try:
        main
    except Exception as e:
        pytest.fail(e)
