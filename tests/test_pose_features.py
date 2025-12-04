import pytest
import numpy as np

from super_mario_motion.pose_features import _mid, _angle, extract_features

N_LM = 33


def make_empty_pose():
    return np.zeros((N_LM, 4), dtype=np.float32)


@pytest.mark.parametrize(
    "a, b, expected",
    [
        (0, 0, 0),
        (0, 1, 0.5),
        (1, 0, 0.5),
        (0, -1, -0.5),
        (-1, 1, 0)
        ]
    )
def test_mid(a, b, expected):
    assert _mid(a, b) == expected


@pytest.mark.parametrize(
    "a, b, c, expected",
    [
        (np.array([0, 0]), np.array([0, 0]), np.array([0, 0]), 0),
        (np.array([0, 0]), np.array([0, 1]), np.array([0, 0]), 0),
        (np.array([0, 0]), np.array([0, -1]), np.array([0, 0]), 0),
        (np.array([1, 1]), np.array([0, 0]), np.array([-1, -1]), 180),
        (np.array([0, 0]), np.array([0, 1]), np.array([1, 1]), 90),
        ]
    )
def test_angle(a, b, c, expected):
    assert _angle(a, b, c) == pytest.approx(expected, abs=1e-3)


def test_extract_features():
    lm = make_empty_pose()
    feats = extract_features(lm)

    assert feats.ndim == 1
    assert feats.dtype == np.float32
    assert len(feats) > 2*N_LM
