import math
import threading
from pathlib import Path

import cv2 as cv
import mediapipe as mp
import numpy as np

from .state import StateManager

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


def landmark_coords(image, lm):
    h = image.shape[0]
    w = image.shape[1]
    return int(w * lm.x), int(h * lm.y)


def init():
    global cam, rgb, frame
    cam = cv.VideoCapture(0)
    if not cam.isOpened():
        raise IOError("Cannot open camera")
    print("cam opened")
    thread = threading.Thread(target=cam_loop, daemon=True)
    thread.start()


def detect_pose_simple(frame_, lm):
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
    global frame, rgb, cam, current_pose, skeleton_only_frame, lm_string
    with mpPose.Pose() as pose:
        print(Path(__file__).name + " initialized")
        while cam.isOpened():
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

                # get current pose via helper method
                current_pose = detect_pose_simple(frame, lm)

                state_manager.set_pose(current_pose)

                # Saves all Landmark cords into a string
                lm_string = ""
                for x in range(33):
                    lm_string += str(x) + str(
                        landmark_coords(frame, lm[x])) + " "
                    if (x + 1) % 4 == 0:
                        lm_string += "\n"
                state_manager.set_landmark_string(lm_string)

    cam.release()


def update_images():
    state_manager.set_all_opencv_images(rgb, frame, skeleton_only_frame)
