import cv2
import cv2 as cv
import numpy as np
import mediapipe as mp
from pathlib import Path

mpPose = mp.solutions.pose
mpDrawing = mp.solutions.drawing_utils

def init():
    cam = cv.VideoCapture(0)
    if not cam.isOpened():
        raise IOError("Cannot open camera")

    with mpPose.Pose(
        static_image_mode = False,        #uses live video, not single pictures
        model_complexity = 1,             #uses mid-precision and mid-speed
        enable_segmentation = False,      #ignores the background
        min_detection_confidence = 0.5,
        min_tracking_confidence = 0.5
    ) as pose:
        print(Path(__file__).name + " initialized")
        while cam.isOpened():
            ret, image = cam.read()
            if not ret:
                break

            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            results = pose.process(rgb)

            frame = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            if results.pose_landmarks:
                mpDrawing.draw_landmarks(
                    frame,
                    results.pose_landmarks,
                    mpPose.POSE_CONNECTIONS
                )

        cam.release()
