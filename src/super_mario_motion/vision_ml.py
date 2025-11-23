import threading
import time
from pathlib import Path

import cv2 as cv
import mediapipe as mp
import numpy as np
from joblib import load

# we get frames from vision.py
from . import vision
from .pose_features import extract_features
from .state import StateManager

state_manager = StateManager()

_current_pose = "standing"
_raw_frame = None
_skeleton_frame = None
_exit = False
_thread = None
_model = None

mpPose = mp.solutions.pose
mpDrawing = mp.solutions.drawing_utils


def init():
    global _thread, _exit, _model
    _exit = False
    # Path
    model_path = (
            Path(__file__).parent.parent.parent / "data" / "pose_model.joblib")
    # load model
    try:
        _model = load(model_path)
        print(f"vision_ml: model loaded ({Path(model_path).name})")
    except Exception as e:
        _model = None
        print("vision_ml: could not load model:", e)

    _thread = threading.Thread(target=_worker, daemon=True)
    _thread.start()


def _worker():
    global _current_pose, _raw_frame, _skeleton_frame
    with mpPose.Pose() as pose:
        print(Path(__file__).name + " initialized (passive)")
        while not _exit:

            bgr = vision.rgb  # latest raw frame from vision

            if bgr is None:
                time.sleep(0.01)
                continue

            _raw_frame = bgr
            rgb = cv.cvtColor(bgr, cv.COLOR_BGR2RGB)
            res = pose.process(rgb)

            if not res.pose_landmarks:
                time.sleep(0.005)
                continue

            # Skeleton-Overlay
            skel = np.zeros_like(bgr)
            mpDrawing.draw_landmarks(skel, res.pose_landmarks,
                                     mpPose.POSE_CONNECTIONS)
            _skeleton_frame = skel

            lm = res.pose_landmarks.landmark
            lm_arr = np.array([[p.x, p.y, p.z, p.visibility] for p in lm],
                              dtype=np.float32)
            feat = extract_features(lm_arr)

            label = None
            if _model is not None:
                x = feat.reshape(1, -1)
                try:
                    label = _model.predict(x)[0]
                except (ValueError, TypeError, NotFittedError):
                    label = None

            if label is not None:
                _smooth.append(label)
                vals, counts = np.unique(list(_smooth), return_counts=True)
                _current_pose = vals[np.argmax(counts)]

                state_manager.set_pose_full_body(_current_pose)
            time.sleep(0.001)


def stop():
    global _exit, _thread
    _exit = True
    if _thread is not None:
        _thread.join(timeout=0.5)
        _thread = None
