import threading
import time
from collections import deque
from pathlib import Path

import numpy as np
from joblib import load
from sklearn.exceptions import NotFittedError

from .pose_features import extract_features
# we get frames from vision.py
from .state import StateManager

state_manager = StateManager()

_current_pose = "standing"
_exit = False
_thread = None
_model = None


def init():
    global _thread, _exit, _model
    _exit = False
    # Path
    model_path = Path(
        __file__
        ).parent.parent.parent / "data" / "pose_model.joblib"
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
    global _current_pose, _exit

    print(Path(__file__).name + " initialized (passive)")

    smooth = deque(maxlen=7)

    while not _exit:
        lm_arr = state_manager.get_pose_landmarks()

        if lm_arr is None:
            time.sleep(0.01)
            continue

        try:
            feat = extract_features(lm_arr)
        except (ValueError, TypeError):
            time.sleep(0.01)
            continue

        if feat is None:
            time.sleep(0.01)
            continue

        try:
            x = feat.reshape(1, -1)
        except ValueError:
            time.sleep(0.01)
            continue

        label = None
        if _model is not None:
            try:
                label = _model.predict(x)[0]
            except (ValueError, TypeError, NotFittedError):
                label = None

        if label is not None:
            smooth.append(label)
            vals, counts = np.unique(list(smooth), return_counts=True)
            _current_pose = vals[np.argmax(counts)]

            state_manager.set_pose_full_body(_current_pose)

        time.sleep(0.001)


def stop():
    global _exit, _thread
    _exit = True
    if _thread is not None:
        _thread.join(timeout=0.5)
        _thread = None
