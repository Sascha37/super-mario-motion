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
                eye_left_x, eye_left_y = landmark_coords(frame, lm[eye_left])
                eye_right_x, eye_right_y = landmark_coords(frame, lm[eye_right])
                shoulder_left_x, shoulder_left_y = landmark_coords(frame, lm[shoulder_left])
                shoulder_right_x, shoulder_right_y = landmark_coords(frame, lm[shoulder_right])
                elbow_left_x, elbow_left_y = landmark_coords(frame, lm[elbow_left])
                elbow_right_x, elbow_right_y = landmark_coords(frame, lm[elbow_right])
                wrist_left_x, wrist_left_y = landmark_coords(frame, lm[wrist_left])
                wrist_right_x, wrist_right_y = landmark_coords(frame, lm[wrist_right])
                hip_left_x, hip_left_y = landmark_coords(frame, lm[hip_left])
                hip_right_x, hip_right_y = landmark_coords(frame, lm[hip_right])
                knee_left_x, knee_left_y = landmark_coords(frame, lm[knee_left])
                knee_right_x, knee_right_y = landmark_coords(frame, lm[knee_right])
                ankle_left_x, ankle_left_y = landmark_coords(frame, lm[ankle_left])
                ankle_right_x, ankle_right_y = landmark_coords(frame, lm[ankle_right])

                walking_left = shoulder_left_y < wrist_left_y < eye_left_y
                walking_right = shoulder_right_y < wrist_right_y < eye_right_y
                running_left = wrist_left_y > eye_left_y  # check if left wrist is above left shoulder
                running_right = wrist_right_y > eye_right_y  # check if right wrist is above right shoulder
                jumping = running_right and running_left
                crouching = wrist_right_y < knee_right_y and wrist_left_y < knee_left_y
                swimming_left = wrist_left_x < shoulder_right_x and wrist_right_x < shoulder_right_x
                swimming_right = wrist_left_x > shoulder_left_x and wrist_right_x > shoulder_left_x



                if jumping:
                    print("Jumping!")
                    current_pose = "jumping"
                elif walking_right:
                    print("Walking right")
                    current_pose = "walking_right"
                elif walking_left:
                    print("Walking reft!")
                    current_pose = "walking_left"
                elif running_right:
                    print("Running right")  # debug message
                    current_pose = "running_right"
                elif running_left:
                    print("Running left!")
                    current_pose = "running_left"
                elif crouching:
                    print("Both hands below knees!")
                    current_pose = "crouching"
                elif swimming_left:
                    print("Swimming left")
                    current_pose = "swimming_left"
                elif swimming_right:
                    print("Swimming right")
                    current_pose = "swimming_right"
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
