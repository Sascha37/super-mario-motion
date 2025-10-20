import threading
from pathlib import Path

import cv2 as cv
import mediapipe as mp
import numpy as np

# globals
raw_frame = None
skel_frame = None
exitApp = False

# runtime
cam = None
rgb = None
frame = None

mpPose = mp.solutions.pose
mpDrawing = mp.solutions.drawing_utils


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
    global frame, rgb, cam
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

            image = cv.flip(image, 1)  # flips the camera horizontally
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

                # landmark indices
                right_wrist = 16
                right_shoulder = 12

                # get right wrist and right shoulder coordinates
                rw_x, rw_y = landmark_coords(frame, lm[right_wrist])
                rs_x, rs_y = landmark_coords(frame, lm[right_shoulder])

                right_hand_up = rw_y < rs_y  # check if right wrist is above right shoulder

                if right_hand_up:
                    print("Right hand up!")  # debug message
            if exitApp:
                break

    cam.release()


def get_latest_raw_frame():
    return rgb


def get_latest_skeleton():
    return frame
