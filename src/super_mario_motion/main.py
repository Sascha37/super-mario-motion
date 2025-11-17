import cv2 as cv

import gui
import input
import vision
import vision_ml
from state import StateManager


# Checks if a webcam is available
def webcam_is_available():
    cam = cv.VideoCapture(0)
    if not cam.isOpened():
        return False
    tmp, _ = cam.read()
    cam.release()
    return tmp


# Function gets called every millisecond after the mainloop of the tkinter ui
def update():

    # Write GUI info into state
    state_manager.set_current_mode(gui.get_active_mode())
    state_manager.set_send_permission(gui.send_keystrokes.get())

    # Retrieve predicted poses
    current_pose = state_manager.get_pose()
    current_pose_full_body = state_manager.get_pose_full_body()

    # Update Images to display in gui.py
    vision.update_images()
    gui.set_webcam_image(*state_manager.get_all_opencv_images())

    # Update Pose Preview Indicator in gui.py
    gui.update_pose(
        current_pose_full_body
        if state_manager.get_current_mode() == "Full-body"
        else current_pose
        )
    gui.update_pose_image()
    gui.update_pose_text()
    gui.update_debug_landmarks(state_manager.get_landmark_string())

    print(f"simple: {current_pose}, full-body: {current_pose_full_body}")

    gui.window.after(1, update)


if __name__ == "__main__":
    if not webcam_is_available():
        print("No Webcam found.")
    else:
        print("Webcam found")
        print("Super Mario Motion started")

        state_manager = StateManager()

        vision.init()
        vision_ml.init()
        input.init()
        gui.init()

        gui.window.after(0, update)
        gui.window.mainloop()
