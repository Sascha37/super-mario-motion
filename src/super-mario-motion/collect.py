# collect.py
import argparse, time, csv
from pathlib import Path
import numpy as np
import cv2 as cv
import mediapipe as mp

# TODO: Remove import vision  # nutzt die Kamera aus laufenden Programm
from state import StateManager

# Init StateManager
state_manger = StateManager()

# Landmarks
eye_left, eye_right = 2, 5
shoulder_left, shoulder_right = 11, 12
elbow_left, elbow_right = 13, 14
wrist_left, wrist_right = 15, 16
hip_left, hip_right = 23, 24
knee_left, knee_right = 25, 26
ankle_left, ankle_right = 27, 28

def _mid(a,b): return (a+b)/2.0
def _angle(a,b,c):
    ba, bc = a-b, c-b
    denom = (np.linalg.norm(ba)*np.linalg.norm(bc))+1e-6
    cosang = np.dot(ba, bc)/denom
    return np.degrees(np.arccos(np.clip(cosang, -1.0, 1.0)))

def extract_features(lm_arr: np.ndarray) -> np.ndarray:
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

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--label", required=True, help="z.B. standing, walking_right, ...")
    ap.add_argument("--seconds", type=float, default=30, help="Dauer der Aufnahme")
    ap.add_argument("--csv", default="pose_samples.csv")
    ap.add_argument("--fps", type=float, default=20.0, help="Ziel-Samplingrate")

    ap.add_argument("--source", choices=["auto", "vision", "camera"], default="auto",
                    help="Frame-Quelle: 'auto' versucht zuerst vision, sonst Kamera.")
    ap.add_argument("--camera-index", type=int, default=0,
                    help="OpenCV Kamera-Index (für source=camera bzw. auto-Fallback).")

    args = ap.parse_args()

    mpPose = mp.solutions.pose
    out_path = Path(__file__).parent.parent.parent / "data" / args.csv
    out_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"[collect] Starte Aufnahme: label={args.label}, {args.seconds}s, source={args.source} → {out_path}")

    t_end = time.time() + args.seconds
    period = 1.0 / max(1e-3, args.fps)
    n_saved = 0

    cam = None
    if args.source == "camera":
        cam = cv.VideoCapture(args.camera_index)
        if not cam.isOpened():
            raise IOError(f"[collect] Could not open camera {args.camera_index}.")

    with mpPose.Pose(static_image_mode=False, model_complexity=1,
                     enable_segmentation=False,
                     min_detection_confidence=0.5,
                     min_tracking_confidence=0.5) as pose, \
         open(out_path, "a", newline="") as f:
        writer = csv.writer(f)

        next_t = 0.0
        start_time = time.time()
        while time.time() < t_end:
            bgr = None

            if args.source in ("auto", "vision"):
                bgr = state_manger.get_opencv_image_webcam()

            if bgr is None and args.source in ("auto", "camera"):
                if cam is None:
                    cam = cv.VideoCapture(args.camera_index)
                    if not cam.isOpened():
                        print(f"[collect] WARN: Kamera {args.camera_index} nicht verfügbar.")
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
            lm_arr = np.array([[p.x, p.y, p.z, p.visibility] for p in lm], dtype=np.float32)
            feat = extract_features(lm_arr)

            writer.writerow([args.label] + [f"{x:.6f}" for x in feat.tolist()])
            n_saved += 1

            next_t += period
            sleep_for = next_t - (time.time() - start_time)
            if sleep_for > 0:
                time.sleep(sleep_for)

    if cam is not None:
        cam.release()

    print(f"[collect] Fertig. Gespeichert: {n_saved} Samples.")

if __name__ == "__main__":
    main()
