import threading
from pathlib import Path

import cv2 as cv
import mediapipe as mp
import numpy as np

# globals
raw_frame = None
skel_frame = None
exitApp = False
current_pose = "standing"

# runtime
cam = None
rgb = None
frame = None

mpPose = mp.solutions.pose
mpDrawing = mp.solutions.drawing_utils

# landmark indices
left_shoulder = 11
right_shoulder = 12
left_elbow = 13
right_elbow = 14
left_wrist = 15
right_wrist = 16
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


def angle(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    cos = (np.dot(a - b, c - b)) / (np.linalg.norm(a - b) * np.linalg.norm(c - b))
    return np.degrees(np.arccos(cos))


def init():
    global cam, rgb, frame
    cam = cv.VideoCapture(0)
    if not cam.isOpened():
        raise IOError("Cannot open camera")
    print("cam opened")
    thread = threading.Thread(target=cam_loop)
    thread.start()


def cam_loop():
    global frame, rgb, cam, current_pose
    with mpPose.Pose(
            static_image_mode=False,  # uses live video, not single pictures
            model_complexity=1,  # uses mid-precision and mid-speed
            enable_segmentation=False,  # ignores the background
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
    ) as pose:
        print(Path(__file__).name + " initialized")
        while cam.isOpened():
            ret, image = cam.read()
            if not ret:
                break

            rgb = cv.cvtColor(image, cv.COLOR_BGR2RGB)
            results = pose.process(rgb)
            frame = cv.cvtColor(image, cv.COLOR_RGB2BGR)

            if results.pose_landmarks:
                mpDrawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mpPose.POSE_CONNECTIONS
                )
                # TODO: implement posture estimations

                lm = results.pose_landmarks.landmark

                # get joint coordinates
                left_shoulder_x, left_shoulder_y = landmark_coords(frame, lm[left_shoulder])
                right_shoulder_x, right_shoulder_y = landmark_coords(frame, lm[right_shoulder])
                left_elbow_x, left_elbow_y = landmark_coords(frame, lm[left_elbow])
                right_elbow_x, right_elbow_y = landmark_coords(frame, lm[right_elbow])
                left_wrist_x, left_wrist_y = landmark_coords(frame, lm[left_wrist])
                right_wrist_x, right_wrist_y = landmark_coords(frame, lm[right_wrist])
                hip_left_x, hip_left_y = landmark_coords(frame, lm[hip_left])
                hip_right_x, hip_right_y = landmark_coords(frame, lm[hip_right])
                knee_left_x, knee_left_y = landmark_coords(frame, lm[knee_left])
                knee_right_x, knee_right_y = landmark_coords(frame, lm[knee_right])
                ankle_left_x, ankle_left_y = landmark_coords(frame, lm[ankle_left])
                ankle_right_x, ankle_right_y = landmark_coords(frame, lm[ankle_right])

                right_hand_up = right_wrist_y < right_shoulder_y  # check if right wrist is above right shoulder
                left_hand_up = left_wrist_y < left_shoulder_y     # check if left wrist is above left shoulder
                both_hands_up = right_hand_up and left_hand_up
                hands_below_knees = right_wrist_y < knee_right_y and left_wrist_y < knee_left_y


                if both_hands_up:
                    print("Both hands up!")
                    current_pose = "jumping"
                elif right_hand_up:
                    print("Right hand up!")  # debug message
                    current_pose = "walking_right"
                elif left_hand_up:
                    print("Left hand up!")
                    current_pose = "walking_left"
                elif hands_below_knees:
                    print("Both hands below knees!")
                    current_pose = "crouching"
                else:
                    current_pose = "standing"
            if exitApp:
                break

    cam.release()


def get_latest_raw_frame():
    return rgb


def get_latest_skeleton():
    return frame

def get_current_pose():
    return current_pose
