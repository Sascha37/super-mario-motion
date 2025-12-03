import pytest
import numpy as np

from super_mario_motion.pose_features import _mid, _angle


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (0, 0, 0),
        (0, 1, 0.5),
        (1, 0, 0.5),
        (0, -1, -0.5),
        (-1, 1, 0),
        ],
    )
def test_mid(a, b, expected):
    assert _mid(a, b) == expected


@pytest.mark.parametrize(
    "a, b, c, expected",
    [
        (np.array([0, 0]), np.array([0, 0]), np.array([0, 0]), 0),
        (np.array([0, 0]), np.array([0, 1]), np.array([0, 0]), 0),
        ],
    )
def test_angle(a, b, c, expected):
    assert _angle(a, b, c) == pytest.approx(expected, abs=1e-3)
