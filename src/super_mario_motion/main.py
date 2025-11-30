import sys

import cv2 as cv

from super_mario_motion import gamepad_visualiser, gui, input, user_data, \
    vision, vision_ml
from super_mario_motion.state import StateManager


def webcam_is_available():
    """Check if a webcam is available on index 0.

    Returns:
        bool: True if a frame can be captured from the webcam, otherwise False.
    """
    cam = cv.VideoCapture(0)
    if not cam.isOpened():
        return False
    tmp, _ = cam.read()
    cam.release()
    return tmp


# Function gets called every millisecond after the mainloop of the tkinter ui
def update():
    """Main update loop that synchronizes state, vision and GUI.

    This function:
      * Writes GUI settings (mode, send inputs) into the StateManager.
      * Retrieves current pose predictions.
      * Updates camera images via `vision` and displays them in the GUI.
      * Updates pose preview image/text/debug info.
      * Updates the virtual gamepad visualizer.
      * Reschedules itself with `gui.window.after(1, update)`.
    """

    # Write GUI info into state
    state_manager.set_current_mode(gui.selected_mode.get())
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

    # Update virtual gamepad visualizer
    pose_for_gamepad = (
        current_pose_full_body
        if state_manager.get_current_mode() == "Full-body"
        else current_pose
        )
    send_active = state_manager.get_send_permission()
    gamepad_img = gamepad_visualiser.create_gamepad_image(
        pose_for_gamepad, send_active=send_active
        )
    gui.set_gamepad_image(gamepad_img)

    # print(f"simple: {current_pose}, full-body: {current_pose_full_body}")

    gui.window.after(1, update)


if __name__ == "__main__":
    if not webcam_is_available():
        print("No Webcam found.")
    else:
        print("Webcam found")
        print("Super Mario Motion started")

        state_manager = StateManager()

        if hasattr(sys, "_MEIPASS"):
            print("[SMM] Opened in standalone executable mode")
            state_manager.set_standalone(True)

        user_data.init()

        vision.init()
        vision_ml.init()
        input.init()
        gui.init()

        gui.window.after(0, update)
        gui.window.mainloop()
