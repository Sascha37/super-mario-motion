"""
Application entry point for Super Mario Motion.

Initializes StateManager, user data, game launcher, vision and ML modules,
input handling and the Tkinter GUI. The GUI is shown immediately with a
short "Please wait…" indicator while heavier subsystems (camera, ML) start
in a background thread. This avoids long blank periods and prevents the app
from appearing to crash while waiting for OS camera permissions.
"""

import sys
import threading
import os

import cv2 as cv

from super_mario_motion import game_launcher, gamepad_visualizer, gui, input, \
    user_data, vision, vision_ml
from super_mario_motion.state import StateManager


def webcam_is_available():
    """Best-effort check if a webcam is available on index 0.

    Returns:
        bool: True if a frame can be captured from the webcam, otherwise False.
    """
    try:
        cam = cv.VideoCapture(0)
        if cam is None:
            return False
        is_opened = False
        try:
            is_opened = cam.isOpened()
        except Exception:
            is_opened = False
        if not is_opened:
            try:
                cam.release()
            except Exception:
                pass
            return False

        try:
            ret, _ = cam.read()
        except Exception:
            ret = False
        try:
            cam.release()
        except Exception:
            pass
        return bool(ret)
    except Exception:
        return False


def _start_heavy_init_async(on_ready):
    """Start camera/ML/input modules in a background thread.

    Calls `on_ready()` on the Tk thread when initialization has finished
    (successfully or with handled errors).
    """
    def _worker():
        # Initialize heavy modules in the background to keep UI responsive
        errors = []
        try:
            vision.init()
        except Exception as e:
            errors.append(f"Camera init failed: {e}")

        try:
            vision_ml.init()
        except Exception as e:
            errors.append(f"ML init failed: {e}")

        try:
            input.init()
        except Exception as e:
            errors.append(f"Input init failed: {e}")

        # Notify UI thread
        try:
            gui.window.after(0, lambda: on_ready(errors))
        except Exception:
            # If GUI is already closed, ignore
            pass

    threading.Thread(target=_worker, daemon=True).start()


# Function gets called every millisecond after the mainloop of the tkinter ui
def update():
    """Main update loop that synchronizes state, vision and GUI.

    This function:
      * Writes GUI settings (mode, send inputs) into the StateManager.
      * Retrieves current pose predictions.
      * Updates camera images via `vision` and displays them in the GUI.
      * Updates pose preview image/text/debug information.
      * Updates the virtual gamepad visualizer.
      * Reschedules itself with `gui.window.after(1, update)`.
    """

    # Write GUI information into state
    state_manager.set_current_mode(gui.selected_mode.get())
    state_manager.set_control_scheme(gui.selected_control_scheme.get())
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
    gamepad_img = gamepad_visualizer.create_gamepad_image(
        pose_for_gamepad, send_active=send_active
        )
    gui.set_gamepad_image(gamepad_img)

    gui.window.after(20, update)


if __name__ == "__main__":
    print("Super Mario Motion starting…")

    state_manager = StateManager()

    if hasattr(sys, "_MEIPASS"):
        print("[SMM] Opened in standalone executable mode")
        state_manager.set_standalone(True)

    # Lightweight inits first
    user_data.init()
    game_launcher.init()

    # Show GUI immediately with a startup overlay
    gui.init()
    try:
        gui.show_startup_overlay("Please wait… Initializing camera and model…")
    except Exception:
        pass

    def _on_ready(errors: list[str]):
        # Update overlay with errors if any; otherwise hide it
        if errors:
            msg = "\n".join(errors)
            try:
                gui.show_startup_overlay(f"Some components failed to start:\n{msg}")
            except Exception:
                pass
        else:
            try:
                gui.hide_startup_overlay()
            except Exception:
                pass

        # Start periodic updates once heavy init finished (even with errors)
        gui.window.after(0, update)

    # Start heavy subsystems in background
    _start_heavy_init_async(_on_ready)

    # Enter GUI loop
    gui.window.mainloop()
