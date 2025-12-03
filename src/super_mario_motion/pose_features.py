import numpy as np

"""
Compute normalized pose features from MediaPipe landmark arrays.

Provides angle, distance, and normalized coordinate features centered at
the mid-hip, scaled by torso length, and augmented with joint angles and
pairwise distances plus visibility values.
"""

# Landmarks
eye_left, eye_right = 2, 5
shoulder_left, shoulder_right = 11, 12
elbow_left, elbow_right = 13, 14
wrist_left, wrist_right = 15, 16
hip_left, hip_right = 23, 24
knee_left, knee_right = 25, 26
ankle_left, ankle_right = 27, 28


def _mid(a, b):
    return (a + b) / 2.0


def _angle(a, b, c):
    """Compute the angle (in degrees) at point b given three points a, b, c.

    Args:
        a, b, c: NumPy arrays representing 2D or 3D points.

    Returns:
        float: Angle at point b in degrees.
    """
    ba, bc = a - b, c - b
    length_product = (np.linalg.norm(ba) * np.linalg.norm(bc)) + 1e-6
    angle_cosine = np.dot(ba, bc) / length_product
    return np.degrees(np.arccos(np.clip(angle_cosine, -1.0, 1.0)))


def extract_features(lm_arr: np.ndarray) -> np.ndarray:
    """Extract a feature vector from full pose landmark data.

    Processing steps:
      * Use only x,y coordinates and center them at the mid-hip.
      * Normalize by torso length (distance from mid-hip to mid-shoulder).
      * Compute joint angles for elbows and knees.
      * Compute selected pairwise distances (shoulders, hips, wrists, ankles,
        shoulders, hips).
      * Append landmark visibility values.

    Args:
        lm_arr: Array of shape (N, 4) with [x, y, z, visibility] for each
            landmark (MediaPipe pose format).

    Returns:
        np.ndarray: 1D feature vector concatenating:
            [xy_flattened, angles, distances, visibility].
    """
    xy = lm_arr[:, :2].copy()
    mid_hip = _mid(xy[hip_left], xy[hip_right])
    xy -= mid_hip
    mid_sh = _mid(xy[shoulder_left], xy[shoulder_right])
    torso = np.linalg.norm(mid_sh) + 1e-6
    xy /= torso
    angles = np.array(
        [
            _angle(xy[shoulder_left], xy[elbow_left], xy[wrist_left]),
            _angle(xy[shoulder_right], xy[elbow_right], xy[wrist_right]),
            _angle(xy[hip_left], xy[knee_left], xy[ankle_left]),
            _angle(xy[hip_right], xy[knee_right], xy[ankle_right]),
            ], dtype=np.float32
        )

    def dist(i, j): return np.linalg.norm(xy[i] - xy[j])

    dists = np.array(
        [
            dist(shoulder_left, shoulder_right),
            dist(hip_left, hip_right),
            dist(wrist_left, wrist_right),
            dist(ankle_left, ankle_right),
            dist(shoulder_left, hip_left),
            dist(shoulder_right, hip_right),
            ], dtype=np.float32
        )
    vis = lm_arr[:, 3].astype(np.float32)
    return np.concatenate([xy.flatten(), angles, dists, vis], axis=0)
