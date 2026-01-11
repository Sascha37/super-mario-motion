"""
Application entry point for Super Mario Motion.

Initializes StateManager, user data, game launcher, vision and ML modules,
input handling and the Tkinter GUI. The GUI is shown immediately with a
short "Please wait…" indicator while heavier subsystems (camera, ML) start
in a background thread. This avoids long blank periods and prevents the app
from appearing to crash while waiting for OS camera permissions.
"""

import os
import platform
import subprocess
import sys
import threading
import time
from pathlib import Path

import cv2 as cv

from super_mario_motion import (
    game_launcher, gamepad_visualizer, gui,
    user_data, vision
    )
from super_mario_motion.settings import Settings
from super_mario_motion.state import StateManager

gui_cams_available = []
cams_available = []


# --- macOS camera permission helper ---
def _ensure_macos_camera_permission() -> str:
    """Ensure camera permission on macOS.

    Returns one of: "authorized", "denied", "restricted", "not_determined", "unknown".
    """
    if platform.system() != "Darwin":
        return "unknown"

    try:
        # PyObjC AVFoundation
        from AVFoundation import AVCaptureDevice
        try:
            from AVFoundation import AVMediaTypeVideo  # type: ignore
            media_type = AVMediaTypeVideo
        except Exception:
            media_type = "video"

        status = AVCaptureDevice.authorizationStatusForMediaType_(media_type)
        # Apple's mapping: 0=notDetermined, 1=restricted, 2=denied, 3=authorized
        if status == 3:
            return "authorized"
        if status == 2:
            return "denied"
        if status == 1:
            return "restricted"

        # Not determined -> request access
        if status == 0:
            evt = threading.Event()
            result = {"granted": False}

            def _handler(granted):
                result["granted"] = bool(granted)
                evt.set()

            try:
                AVCaptureDevice.requestAccessForMediaType_completionHandler_(
                    media_type, _handler
                )
            except Exception:
                # If the request API is unavailable, fall back to "not_determined"
                return "not_determined"

            # Wait a bit for the user to respond
            evt.wait(30)

            # Re-check status (more reliable than handler)
            try:
                status2 = AVCaptureDevice.authorizationStatusForMediaType_(media_type)
                if status2 == 3:
                    return "authorized"
                if status2 == 2:
                    return "denied"
                if status2 == 1:
                    return "restricted"
                return "not_determined"
            except Exception:
                return "unknown"

        return "unknown"
    except Exception:
        return "unknown"


def webcam_is_available(x):
    """Best-effort check if a webcam is available on index x.

    Some webcams (and phone-continuity cameras) need a short warm-up or
    permission prompt on first access. We therefore retry a few times.

    Returns:
        bool: True if a frame can be captured from the webcam, otherwise False.
    """
    cam = None
    try:
        # Prefer AVFoundation backend on macOS when available
        if platform.system() == "Darwin" and hasattr(cv, "CAP_AVFOUNDATION"):
            cam = cv.VideoCapture(x, cv.CAP_AVFOUNDATION)
        else:
            cam = cv.VideoCapture(x)

        if cam is None:
            return False

        # Give the device a moment to initialize and allow permission prompts.
        for _ in range(8):  # ~1.6s total
            try:
                if cam.isOpened():
                    ret, _ = cam.read()
                    if ret:
                        return True
            except Exception:
                pass
            time.sleep(0.2)

        return False
    except Exception:
        return False
    finally:
        try:
            if cam is not None:
                cam.release()
        except Exception:
            pass


def find_cams():
    global cams_available, gui_cams_available
    gui_cams_available = []
    cams_available = []

    system = platform.system()

    if system == "Windows":
        from pygrabber.dshow_graph import FilterGraph
        try:
            names = FilterGraph().get_input_devices()
            cams_available = names
        except Exception:
            pass

    elif system == "Linux":
        try:
            out = subprocess.check_output(
                ["v4l2-ctl", "--list-devices"],
                text=True,
                errors="ignore"
                )

            current_name = None
            for line in out.splitlines():
                if line and not line.startswith("\t") and line.endswith(":"):
                    current_name = line[:-1]

                elif line.strip().startswith("/dev/video"):
                    line.strip()
                    cams_available.append(current_name)
        except Exception:
            pass

    elif system == "Darwin":
        from AVFoundation import AVCaptureDevice
        try:
            devices = AVCaptureDevice.devicesWithMediaType_("video")
            for device in devices:
                cams_available.append(device.localizedName())
        except Exception:
            pass

    for i, _cam in enumerate(cams_available):
        if not webcam_is_available(i):
            cams_available[i] = ""

    gui_cams_available = [x for x in cams_available if x]
    return cams_available





def _start_heavy_init_async(on_ready):
    """Start camera/ML/input modules in a background thread.

    Calls `on_ready()` on the Tk thread when initialization has finished
    (successfully or with handled errors).
    """

    def _worker():
        # Initialize heavy modules in the background to keep the UI responsive
        errors = []
        # Ensure Matplotlib (used by MediaPipe drawing_utils) has a writable
        # config dir to avoid long first-run cache creation delays.
        try:
            mpl_dir_ = Path.home() / ".super_mario_motion_mpl"
            mpl_dir_.mkdir(parents=True, exist_ok=True)
            os.environ.setdefault("MPLCONFIGDIR", str(mpl_dir_))
        except Exception:
            pass

        # Detect available cameras after GUI is shown.
        # On macOS we first ensure camera permission is granted; otherwise
        # enumerating/validating cameras will look like "no camera found".
        try:
            if platform.system() == "Darwin":
                try:
                    gui.window.after(
                        0, lambda: gui.show_startup_overlay(
                            "Camera access required…\nPlease allow camera access when prompted."
                        )
                    )
                except Exception:
                    pass

                perm = _ensure_macos_camera_permission()

                if perm != "authorized":
                    # Provide actionable message and skip scanning for now.
                    msg = (
                        "Camera access not granted.\n"
                        "Enable it in System Settings → Privacy & Security → Camera,\n"
                        "then restart the app."
                    )
                    try:
                        gui.window.after(0, lambda: gui.show_startup_overlay(msg))
                    except Exception:
                        pass

                    # Inform GUI combobox with a clearer placeholder.
                    try:
                        gui.window.after(0, lambda: gui.set_available_cams([], [], status_text="(camera access required)"))
                    except Exception:
                        pass
                else:
                    try:
                        gui.window.after(
                            0, lambda: gui.show_startup_overlay(
                                "Loading cameras…"
                            )
                        )
                    except Exception:
                        pass

                    cams = find_cams()
                    globals()["cams_available"] = cams
                    globals()["gui_cams_available"] = [c for c in cams if c]

                    # Push list into GUI (combobox) on Tk thread
                    try:
                        gui.window.after(
                            0,
                            lambda: gui.set_available_cams(gui_cams_available, cams_available)
                        )
                    except Exception:
                        pass
            else:
                # Non-macOS: just scan.
                try:
                    gui.window.after(
                        0, lambda: gui.show_startup_overlay(
                            "Loading cameras…"
                        )
                    )
                except Exception:
                    pass

                cams = find_cams()
                globals()["cams_available"] = cams
                globals()["gui_cams_available"] = [c for c in cams if c]

                try:
                    gui.window.after(
                        0,
                        lambda: gui.set_available_cams(gui_cams_available, cams_available)
                    )
                except Exception:
                    pass
        except Exception as e:
            errors.append(f"Camera detection failed: {e}")

        # Lazy-import heavy modules here to avoid blocking GUI import time.
        try:
            import importlib
            vision_ = importlib.import_module("super_mario_motion.vision")
            # expose to this module's globals so `update()` can use it
            globals()["vision"] = vision_
        except Exception as e:
            vision_ = None
            errors.append(f"Camera module import failed: {e}")

        try:
            try:
                gui.window.after(
                    0, lambda: gui.show_startup_overlay(
                        "Starting camera…"
                        )
                    )
            except Exception:
                pass
            if vision_ is not None:
                vision_.init()
        except Exception as e:
            errors.append(f"Camera init failed: {e}")

        try:
            import importlib
            vision_ml = importlib.import_module("super_mario_motion.vision_ml")
            # optional exposure for other modules
            globals()["vision_ml"] = vision_ml
            try:
                gui.window.after(
                    0, lambda: gui.show_startup_overlay(
                        "Loading pose model…"
                        )
                    )
            except Exception:
                pass
            vision_ml.init()
        except Exception as e:
            errors.append(f"ML init failed: {e}")

        try:
            import importlib
            input_mod = importlib.import_module("super_mario_motion.input")
            # optional exposure for completeness
            globals()["input"] = input_mod
            try:
                gui.window.after(
                    0, lambda: gui.show_startup_overlay(
                        "Starting input module…"
                        )
                    )
            except Exception:
                pass
            input_mod.init()
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
    try:
        if "vision" in globals():
            vision.update_images()
    except Exception:
        pass
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

    gui.window.after(Settings.gui_update_ms, update)


if __name__ == "__main__":
    print("Super Mario Motion starting…")

    state_manager = StateManager()

    if hasattr(sys, "_MEIPASS"):
        print("[SMM] Opened in standalone executable mode")
        state_manager.set_standalone(True)

    # Configure Matplotlib cache directory early (used by mediapipe's
    # drawing_utils) to avoid long font-cache build times on the first run.
    try:
        mpl_dir = Path.home() / ".super_mario_motion_mpl"
        mpl_dir.mkdir(parents=True, exist_ok=True)
        os.environ.setdefault("MPLCONFIGDIR", str(mpl_dir))
    except Exception:
        pass

    # Lightweight inits first
    user_data.init()
    game_launcher.init()

    # Show GUI immediately with a startup overlay
    gui.init()
    try:
        gui.show_startup_overlay("Please wait… Initializing camera and model…")
        try:
            gui.window.update_idletasks()
        except Exception:
            pass
    except Exception:
        pass


    def _on_ready(errors: list[str]):
        # Update overlay with errors if any; otherwise hide it
        if errors:
            msg = "\n".join(errors)
            try:
                gui.show_startup_overlay(
                    f"Some components failed to start:\n{msg}"
                    )
            except Exception:
                pass
        else:
            try:
                gui.hide_startup_overlay()
            except Exception:
                pass

        # Start periodic updates once heavy init finished (even with errors)
        gui.window.after(0, update)


    # Start heavy subsystems in the background
    _start_heavy_init_async(_on_ready)

    # Enter GUI loop
    gui.window.mainloop()
