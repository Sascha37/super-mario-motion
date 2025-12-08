"""
Webcam and MediaPipe-based pose detection and skeleton rendering.

Captures frames in a background thread, runs MediaPipe Pose, infers a
simple pose label from landmarks, renders webcam+skeleton frames, and
stores images, landmarks, pose, and debug strings in the shared
StateManager.
"""

import math
import threading
from pathlib import Path

import cv2 as cv
import mediapipe as mp
import numpy as np

from super_mario_motion.state import StateManager

# globals
lm_string = None
skeleton_only_frame = None
raw_frame = None
skel_frame = None
current_pose = "standing"

# runtime
cam = None
rgb = None
frame = None
_exit = False
thread = None

mpPose = mp.solutions.pose
mpDrawing = mp.solutions.drawing_utils

state_manager = StateManager()

# landmark indices
nose = 0
eye_left = 2
eye_right = 5
shoulder_left = 11
shoulder_right = 12
elbow_left = 13
elbow_right = 14
wrist_left = 15
wrist_right = 16
hip_left = 23
hip_right = 24
knee_left = 25
knee_right = 26
ankle_left = 27
ankle_right = 28


# enhance the image for better pose detection
def enhance_frame(rgb_frame: np.ndarray):
    """Enhance contrast for better pose detection."""
    ycrcb = cv.cvtColor(rgb_frame, cv.COLOR_RGB2YCrCb)
    y, cr, cb = cv.split(ycrcb)
    clahe = cv.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    y_eq = clahe.apply(y)
    ycrcb_eq = cv.merge((y_eq, cr, cb))
    return cv.cvtColor(ycrcb_eq, cv.COLOR_YCrCb2RGB)


def landmark_coords(image, lm):
    """Return pixel coordinates of a landmark in an image.

    Args:
        image: Numpy array (H, W, C) representing the current frame.
        lm: MediaPipe landmark object with normalized x/y in [0, 1].

    Returns:
        tuple[int, int]: (x, y) pixel coordinates of the landmark.
    """
    h = image.shape[0]
    w = image.shape[1]
    return int(w * lm.x), int(h * lm.y)


def init():
    """Initialize the webcam and start the camera processing thread.

    Opens the default camera (index 0) and starts `cam_loop` as a daemon
    thread. Raises an IOError if the camera cannot be opened.
    """
    global cam, rgb, frame, thread
    cam = cv.VideoCapture(0)
    if not cam.isOpened():
        raise IOError("Cannot open camera")

    # try to enforce a uniform resolution and FPS
    cam.set(cv.CAP_PROP_FRAME_WIDTH, 1280)
    cam.set(cv.CAP_PROP_FRAME_HEIGHT, 720)
    cam.set(cv.CAP_PROP_FPS, 30)

    print("cam opened")
    thread = threading.Thread(target=cam_loop, daemon=True)
    thread.start()


def stop_cam():
    global _exit, thread, cam
    _exit = True

    if thread is not None:
        thread.join(timeout=0.5)
        thread = None
    if cam is not None:
        cam.release()
        cam = None


def detect_pose_simple(frame_, lm):
    """Determine a simple pose label from landmark positions.

    Heuristic rules based on relative positions of eyes, shoulders and
    wrists define these poses:

    * standing
    * walking_left / walking_right
    * running_left / running_right
    * jumping
    * crouching
    * throwing
    * swimming

    Args:
        frame_: Current image frame (for coordinate scaling).
        lm: Sequence of MediaPipe pose landmarks.

    Returns:
        str: Detected pose label.
    """

    # helper functions for coordinates and distance
    def coordinates(index):
        return landmark_coords(frame_, lm[index])

    def distance(x, y):
        return math.hypot(y[0] - x[0], y[1] - x[1])

    # get relevant landmark coordinates
    eye_left_xy = coordinates(eye_left)
    eye_right_xy = coordinates(eye_right)
    shoulder_left_xy = coordinates(shoulder_left)
    shoulder_right_xy = coordinates(shoulder_right)
    wrist_left_xy = coordinates(wrist_left)
    wrist_right_xy = coordinates(wrist_right)

    # define common coordinates
    shoulder_width = distance(shoulder_left_xy, shoulder_right_xy)
    shoulder_left_y, shoulder_right_y = (shoulder_left_xy[1],
                                         shoulder_right_xy[1])
    eye_left_y, eye_right_y = eye_left_xy[1], eye_right_xy[1]
    wrist_left_x, wrist_left_y = wrist_left_xy
    wrist_right_x, wrist_right_y = wrist_right_xy
    wrist_dist = distance(wrist_left_xy, wrist_right_xy)
    hands_below_shoulders = (
            wrist_left_y > shoulder_left_y
            and wrist_right_y > shoulder_right_y)

    # throwing: hands near each other
    throwing = wrist_dist < shoulder_width * 0.75 and not hands_below_shoulders

    # walking: hand between shoulder and eyes
    walking_left = shoulder_left_y > wrist_left_y > eye_left_y
    walking_right = shoulder_right_y > wrist_right_y > eye_right_y

    # running: hand above eyes
    running_left = wrist_left_y < eye_left_y
    running_right = wrist_right_y < eye_right_y

    # jumping: both arms above shoulders
    jumping = (running_right or walking_right) and (
            running_left or walking_left)

    # crouching: hands near each other and below shoulders
    crouching = wrist_dist < shoulder_width * 0.75 and hands_below_shoulders

    swimming = wrist_left_x < wrist_right_x

    # setting priorities (higher = higher priority)
    if swimming:
        return "swimming"

    if throwing:
        return "throwing"

    if jumping:
        return "jumping"

    if running_right:
        return "running_right"
    if running_left:
        return "running_left"

    if walking_right:
        return "walking_right"
    if walking_left:
        return "walking_left"

    if crouching:
        return "crouching"

    return "standing"


def cam_loop():
    """Camera processing loop that runs in a background thread.

    This loop:
      * Grabs frames from the webcam.
      * Runs MediaPipe Pose on each frame.
      * Draws skeleton overlays for full and skeleton-only frames.
      * Extracts pose landmarks as a NumPy array.
      * Detects the current simple pose via `detect_pose_simple`.
      * Updates the StateManager with landmarks, pose and debug strings.

    Loop exits when `_exit` is set to True or the camera is closed.
    """
    global frame, rgb, cam, current_pose, skeleton_only_frame, lm_string
    with mpPose.Pose(
            static_image_mode=False,
            model_complexity=1,
            smooth_landmarks=True,
            enable_segmentation=False,
            min_detection_confidence=0.3,   # more robust
            min_tracking_confidence=0.3,    # more robust
            ) as pose:

        print(Path(__file__).name + " initialized")
        while not _exit and cam.isOpened():
            ret, image = cam.read()
            if not ret:
                break

            rgb = cv.cvtColor(image, cv.COLOR_BGR2RGB)
            results = pose.process(rgb)
            frame = cv.cvtColor(image, cv.COLOR_RGB2BGR)

            if results.pose_landmarks:
                # Draw webcam footage and skeleton
                mpDrawing.draw_landmarks(
                    frame, results.pose_landmarks, mpPose.POSE_CONNECTIONS
                    )

                # Draw an image of only the skeleton
                skeleton_only_frame = np.zeros_like(frame)
                mpDrawing.draw_landmarks(
                    skeleton_only_frame, results.pose_landmarks,
                    mpPose.POSE_CONNECTIONS
                    )

                # Simple pose detection
                lm = results.pose_landmarks.landmark

                # save landmarks to state
                lm_arr = np.array(
                    [[p.x, p.y, p.z, p.visibility] for p in lm],
                    dtype=np.float32
                    )
                state_manager.set_pose_landmarks(lm_arr)

                # get current pose via helper method
                current_pose = detect_pose_simple(frame, lm)

                state_manager.set_pose(current_pose)

                # Saves all Landmark cords into a string
                lm_string = ""
                for x in range(33):
                    lm_string += str(x) + str(
                        landmark_coords(frame, lm[x])
                        ) + " "
                    if (x + 1) % 4 == 0:
                        lm_string += "\n"
                state_manager.set_landmark_string(lm_string)

    cam.release()


def update_images():
    state_manager.set_all_opencv_images(rgb, frame, skeleton_only_frame)
