"""
Full-body pose classification from MediaPipe landmarks using a trained ML
model.

Loads an SVM-based pose classifier (external or bundled), runs a passive
background worker that reads pose landmarks from StateManager, extracts
features, predicts poses with smoothing, and writes the smoothed full-body
pose labels back to shared state.
"""

import os
import threading
import time
from collections import deque
from pathlib import Path
from pickle import UnpicklingError

import numpy as np
from joblib import load
from sklearn.exceptions import NotFittedError

from super_mario_motion import path_helper as ph
from super_mario_motion.pose_features import extract_features
# get frames from vision.py
from super_mario_motion.state import StateManager
from super_mario_motion.settings import Settings

state_manager = StateManager()

_current_pose = "standing"
_exit = False
_thread = None
_model = None
model_path = None

P_THRESH = Settings.p_thresh  # threshold for model confidence
VOTE_RATIO = Settings.vote_ratio    # ratio for the majority vote


def init():
    """Load the ML model and start the passive worker thread."""
    global _thread, _exit, _model, model_path
    _exit = False

    # Try to load the external model
    try:
        model_path = Path(
            state_manager.get_data_folder_path()
            ) / "pose_model.joblib"
        _model = load(model_path)
        print(f"[vision_ml] external model loaded ({model_path})")
    except (FileNotFoundError, OSError, EOFError, UnpicklingError):
        print(f"[vision_ml] could not load external model at: {model_path}")
        # Try to load the internal fallback model
        try:
            model_path = ph.resource_path(
                os.path.join("data", "pose_model.joblib")
                )
            _model = load(model_path)
            print(f"[vision_ml] fallback model loaded ({model_path})")
        except Exception as e:
            _model = None
            print("[vision_ml] could not load fallback model:", e)

    _thread = threading.Thread(target=_worker, daemon=True)
    _thread.start()


def _worker():
    """Continuously classify full-body poses from landmark data.

    Steps:
      * Read the latest landmarks from StateManager.
      * Extract PCA-scaled feature vector.
      * Predict pose with the loaded SVM model.
      * Apply the majority vote smoothing over recent predictions.
      * Store smoothed pose in StateManager.

    Runs until `_exit` is set to True.
    """
    global _current_pose, _exit

    print(Path(__file__).name + " initialized (passive)")

    smooth = deque(maxlen=Settings.ml_majority_vote)

    while not _exit:
        lm_arr = state_manager.get_pose_landmarks()

        if lm_arr is None:
            time.sleep(0.01)
            continue

        # skip frames with low landmark visibility
        vis = lm_arr[:, 3]
        if np.mean(vis) < Settings.frame_quality:  # can be tuned later
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
                proba = _model.predict_proba(x)[0]
                pmax = float(np.max(proba))
                if pmax >= P_THRESH:
                    label = _model.classes_[int(np.argmax(proba))]
                else:
                    label = None
            except (ValueError, TypeError, NotFittedError):
                label = None

        if label is not None:
            smooth.append(label)
            vals, counts = np.unique(list(smooth), return_counts=True)
            best_i = int(np.argmax(counts))
            best_label = vals[best_i]
            best_ratio = counts[best_i] / len(smooth)

            if best_ratio >= VOTE_RATIO:
                _current_pose = best_label
                state_manager.set_pose_full_body(_current_pose)

        time.sleep(0.001)


def stop():
    """Stop the classifier worker thread."""
    global _exit, _thread
    _exit = True
    if _thread is not None:
        _thread.join(timeout=0.5)
        _thread = None
