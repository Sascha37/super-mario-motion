import threading
import time
from pathlib import Path
from collections import deque

import numpy as np
import cv2 as cv
import mediapipe as mp
from joblib import load

# Wir beziehen Frames aus vision.py
from . import vision


_current_pose = "standing"
_raw_frame = None
_skeleton_frame = None
_exit = False
_thread = None


mpPose = mp.solutions.pose
mpDrawing = mp.solutions.drawing_utils

# Landmarks
eye_left, eye_right = 2, 5
shoulder_left, shoulder_right = 11, 12
elbow_left, elbow_right = 13, 14
wrist_left, wrist_right = 15, 16
hip_left, hip_right = 23, 24
knee_left, knee_right = 25, 26
ankle_left, ankle_right = 27, 28


_smooth = deque(maxlen=7)

_model = None

def _mid(a,b): return (a+b)/2.0
def _angle(a,b,c):
    ba, bc = a-b, c-b
    denom = (np.linalg.norm(ba)*np.linalg.norm(bc))+1e-6
    cosang = np.dot(ba, bc)/denom
    return np.degrees(np.arccos(np.clip(cosang, -1.0, 1.0)))

def _extract_features(lm_arr: np.ndarray) -> np.ndarray:
    xy = lm_arr[:, :2].copy()
    mid_hip = _mid(xy[hip_left], xy[hip_right]); xy -= mid_hip
    mid_sh = _mid(xy[shoulder_left], xy[shoulder_right])
    torso = np.linalg.norm(mid_sh) + 1e-6; xy /= torso
    angs = np.array([
        _angle(xy[shoulder_left], xy[elbow_left], xy[wrist_left]),
        _angle(xy[shoulder_right], xy[elbow_right], xy[wrist_right]),
        _angle(xy[hip_left],      xy[knee_left],  xy[ankle_left]),
        _angle(xy[hip_right],     xy[knee_right], xy[ankle_right]),
    ], dtype=np.float32)
    def dist(i,j): return np.linalg.norm(xy[i]-xy[j])
    dists = np.array([
        dist(shoulder_left, shoulder_right),
        dist(hip_left, hip_right),
        dist(wrist_left, wrist_right),
        dist(ankle_left, ankle_right),
        dist(shoulder_left, hip_left),
        dist(shoulder_right, hip_right),
    ], dtype=np.float32)
    vis = lm_arr[:, 3].astype(np.float32)
    return np.concatenate([xy.flatten(), angs, dists, vis], axis=0)

def init():
    global _thread, _exit, _model
    _exit = False
    # Path
    model_path = Path(__file__).parent.parent.parent / "data" / "pose_model.joblib"
    # Modell laden
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
    with mpPose.Pose(static_image_mode=False, model_complexity=1,
                     enable_segmentation=False,
                     min_detection_confidence=0.5,
                     min_tracking_confidence=0.5) as pose:
        print(Path(__file__).name + " initialized (passive)")
        while not _exit:

            bgr = vision.rgb #latest raw frame from vision

            if bgr is None:
                time.sleep(0.01)
                continue

            _raw_frame = bgr
            rgb = cv.cvtColor(bgr, cv.COLOR_BGR2RGB)
            res = pose.process(rgb)

            if not res.pose_landmarks:
                time.sleep(0.005)
                continue

            # Skelett-Overlay
            skel = np.zeros_like(bgr)
            mpDrawing.draw_landmarks(skel, res.pose_landmarks, mpPose.POSE_CONNECTIONS)
            _skeleton_frame = skel

            lm = res.pose_landmarks.landmark
            lm_arr = np.array([[p.x, p.y, p.z, p.visibility] for p in lm], dtype=np.float32)
            feat = _extract_features(lm_arr)

            label = None
            if _model is not None:
                X = feat.reshape(1, -1)
                try:
                    label = _model.predict(X)[0]
                except Exception as e:
                    label = None

            if label is not None:
                _smooth.append(label)
                vals, counts = np.unique(list(_smooth), return_counts=True)
                _current_pose = vals[np.argmax(counts)]
                print(str(_current_pose))
            time.sleep(0.001)

def get_current_pose():
    return _current_pose

# TODO: For now I just commented it out, I dont know why this would be needed - Sascha

#def get_latest_raw_frame():
#    return vision.get_latest_raw_frame()

#def get_latest_skeleton():
#    return _skeleton_frame

def stop():
    global _exit, _thread
    _exit = True
    if _thread is not None:
        _thread.join(timeout=0.5)
        _thread = None
