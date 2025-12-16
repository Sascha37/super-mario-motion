"""
Collects pose-sample data via MediaPipe Pose and writes feature rows to a
CSV file.
Provides a CLI for selecting label, duration, FPS, frame source (vision or
camera),
and output file. Used to record training data for pose-based models.
"""

import argparse
import csv
import time
from pathlib import Path

import cv2 as cv
import mediapipe as mp
import numpy as np

from super_mario_motion.pose_features import (elbow_left, elbow_right,
                                              extract_features, hip_left,
                                              hip_right, shoulder_left,
                                              shoulder_right, wrist_left,
                                              wrist_right)
from super_mario_motion.state import StateManager

# Init StateManager
state_manger = StateManager()

VISIBILITY_THRESH = 0.6  # can be tuned later
STABLE_N = 3  # how many consecutive similar frames are required
FEATURE_EPS = 0.2  # max allowed mean deviation per feature


def is_valid_lm_frame(lm_arr: np.ndarray) -> bool:
    """
    Check if a frame is good enough for training based on visibility.
    Only keep frames where all required joints are clearly visible.
    """
    required_indices = [
        shoulder_left, shoulder_right,
        elbow_left, elbow_right,
        wrist_left, wrist_right,
        hip_left, hip_right,
        ]
    vis = lm_arr[:, 3]
    return np.all(vis[required_indices] >= VISIBILITY_THRESH)


def features_similar(a: np.ndarray, b: np.ndarray, eps: float) -> bool:
    """
    Simple similarity check between two feature vectors.
    Uses mean absolute difference.
    """
    if a.shape != b.shape:
        return False
    return float(np.mean(np.abs(a - b))) < eps


def main():
    """Run pose sample collection as a CLI program.

    Command line arguments:
        --label (str, required):
            Class label for all collected samples
            (e.g., standing, walking_right, ...).
        --seconds (float, default=30):
            Duration of the recording in seconds.
        --csv (str, default="pose_samples.csv"):
            Name of the CSV file (stored under ./data/).
        --fps (float, default=20.0):
            Target sampling rate for saving feature rows.
        --source ({"auto", "vision", "camera"}, default="auto"):
            Source of frames:
              - "vision": use frames from StateManager / running app
              - "camera": read directly from an OpenCV camera
              - "auto": try vision first, fall back to camera.
        --camera-index (int, default=0):
            OpenCV camera index for camera / auto-fallback.

    The function captures frames, runs MediaPipe Pose, extracts features
    via `extract_features` and appends lines of the form:

        label, feat_0, feat_1, ..., feat_N

    to the configured CSV file.
    """
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--label", required=True,
        help="z.B. standing, walking_right, ..."
        )
    ap.add_argument(
        "--seconds", type=float, default=30,
        help="duration of recording"
        )
    ap.add_argument("--csv", default="pose_samples.csv")
    ap.add_argument(
        "--fps", type=float, default=20.0,
        help="goal-sampling rate"
        )

    ap.add_argument(
        "--source", choices=["auto", "vision", "camera"],
        default="auto",
        help="Frame-Source: 'auto' try vision first, else camera."
        )
    ap.add_argument(
        "--camera-index", type=int, default=0,
        help="OpenCV camera-index (for source=camera or "
             "auto-fallback)."
        )

    args = ap.parse_args()

    mp_pose = mp.solutions.pose
    out_path = Path(__file__).parent.parent.parent / "data" / args.csv
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(
        f"[collect] start recording: label={args.label}, {args.seconds}s, "
        f"source={args.source} → "
        f"{out_path}"
        )

    t_end = time.time() + args.seconds
    period = 1.0 / max(1e-3, args.fps)
    n_saved = 0

    cam = None
    if args.source == "camera":
        cam = cv.VideoCapture(args.camera_index)
        if not cam.isOpened():
            raise IOError(
                f"[collect] Could not open camera {args.camera_index}."
                )

    with mp_pose.Pose(
            min_detection_confidence=0.4, min_tracking_confidence=0.4
            ) as pose, open(out_path, "a", newline="") as f:

        writer = csv.writer(f)

        next_t = 0.0
        start_time = time.time()

        stable_buffer = []
        last_feat = None

        while time.time() < t_end:
            bgr = None

            if args.source in ("auto", "vision"):
                bgr = state_manger.get_opencv_image_webcam()

            if bgr is None and args.source in ("auto", "camera"):
                if cam is None:
                    cam = cv.VideoCapture(args.camera_index)
                    if not cam.isOpened():
                        print(
                            f"[collect] WARN: camera {args.camera_index} not "
                            f"available."
                            )
                        time.sleep(0.05)
                        continue
                ok, bgr = cam.read()
                if not ok:
                    time.sleep(0.01)
                    continue

            if bgr is None:
                time.sleep(0.01)
                continue

            rgb = cv.cvtColor(bgr, cv.COLOR_BGR2RGB)
            res = pose.process(rgb)
            if not res.pose_landmarks:
                time.sleep(0.002)
                continue

            lm = res.pose_landmarks.landmark
            lm_arr = np.array(
                [[p.x, p.y, p.z, p.visibility] for p in lm],
                dtype=np.float32
                )

            # filter frames based on landmark visibility
            if not is_valid_lm_frame(lm_arr):
                time.sleep(0.002)
                continue

            feat = extract_features(lm_arr)

            if last_feat is None:
                last_feat = feat
                stable_buffer = [feat]
            else:
                if features_similar(feat, last_feat, FEATURE_EPS):
                    stable_buffer.append(feat)
                    last_feat = feat
                else:
                    # pose changed, reset buffer
                    stable_buffer = [feat]
                    last_feat = feat

            # only write when pose is stable over STABLE_N frames
            if len(stable_buffer) >= STABLE_N:
                mean_feat = np.mean(stable_buffer, axis=0)
                writer.writerow(
                    [args.label] + [f"{x:.6f}" for x in mean_feat.tolist()]
                    )
                n_saved += 1
                stable_buffer = []  # reset buffer after saving one sample
                last_feat = None

            next_t += period
            sleep_for = next_t - (time.time() - start_time)
            if sleep_for > 0:
                time.sleep(sleep_for)

    if cam is not None:
        cam.release()

    print(f"[collect] Done. Saved: {n_saved} Samples.")


if __name__ == "__main__":
    main()
