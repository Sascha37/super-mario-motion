"""
Unit tests for rule-based pose detection.

Constructs synthetic landmark configurations to verify that
`detect_pose_simple` returns the correct pose labels for standing,
walking, running, jumping, crouching, throwing, and swimming cases.
"""

import numpy as np

from super_mario_motion.vision import (
    detect_pose_simple, eye_left,
    eye_right, shoulder_left, shoulder_right, wrist_left, wrist_right
    )


class DummyLm:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.z = 0.0
        self.visibility = 1.0


def make_landmarks():
    # create 33 neutral landmarks
    lm = [DummyLm(0.5, 0.5) for _ in range(33)]
    return lm


def make_frame():
    # create a blank frame (height=480, width=640)
    return np.zeros((480, 640, 3), dtype=np.uint8)


def test_standing_default():
    lm = make_landmarks()
    frame = make_frame()

    label = detect_pose_simple(frame, lm)

    assert label == "standing"


def test_jumping():
    lm = make_landmarks()
    frame = make_frame()

    # jumping: both arms above shoulders
    lm[shoulder_left].y = 0.6
    lm[shoulder_right].y = 0.6
    lm[wrist_left].y = 0.5
    lm[wrist_right].y = 0.5
    lm[eye_left].y = lm[eye_right].y = 0.4

    label = detect_pose_simple(frame, lm)
    assert label == "jumping"


def test_walking_left():
    lm = make_landmarks()
    frame = make_frame()

    # walking left: left_shoulder_y > left_wrist_y > left_eye_y
    lm[shoulder_left].y = 0.6
    lm[wrist_left].y = 0.5
    lm[eye_left].y = 0.4
    lm[wrist_right].y = 0.7

    label = detect_pose_simple(frame, lm)
    assert label == "walking_left"


def test_walking_right():
    lm = make_landmarks()
    frame = make_frame()

    # walking right: right_shoulder_y > right_wrist_y > right_eye_y
    lm[shoulder_right].y = 0.6
    lm[wrist_right].y = 0.5
    lm[eye_right].y = 0.4
    lm[wrist_left].y = 0.7

    label = detect_pose_simple(frame, lm)
    assert label == "walking_right"


def test_running_left():
    lm = make_landmarks()
    frame = make_frame()

    lm[eye_left].y = 0.5  # eye at mid
    lm[wrist_left].y = 0.3  # hand above eye

    label = detect_pose_simple(frame, lm)
    assert label == "running_left"


def test_running_right():
    lm = make_landmarks()
    frame = make_frame()

    lm[eye_right].y = 0.5  # eye at mid
    lm[wrist_right].y = 0.3  # hand above eye

    label = detect_pose_simple(frame, lm)
    assert label == "running_right"


def test_throwing():
    lm = make_landmarks()
    frame = make_frame()

    # throwing: wrists close, above shoulders
    lm[wrist_left].x = 0.52
    lm[wrist_right].x = 0.48
    lm[shoulder_left].y = 0.6
    lm[wrist_left].y = 0.4  # above shoulder
    lm[wrist_right].y = 0.4

    label = detect_pose_simple(frame, lm)
    assert label == "throwing"


def test_crouching():
    lm = make_landmarks()
    frame = make_frame()

    # crouching: wrists close and below shoulders
    lm[shoulder_left].y = 0.4
    lm[wrist_left].y = 0.7
    lm[wrist_right].y = 0.7

    lm[wrist_left].x = 0.52
    lm[wrist_right].x = 0.48

    label = detect_pose_simple(frame, lm)
    assert label == "crouching"


def test_swimming():
    lm = make_landmarks()
    frame = make_frame()

    # swimming: left wrist right of right wrist
    lm[wrist_left].x = 0.5
    lm[wrist_right].x = 0.6

    label = detect_pose_simple(frame, lm)
    assert label == "swimming"
