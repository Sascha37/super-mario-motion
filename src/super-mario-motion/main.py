import cv2 as cv
import gui
import vision
import vision_ml
import input
import argparse
import collect
import sys
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

    # Retrieve Checkbox Info from gui.py
    state_manager.set_send_permission(gui.send_keystrokes.get())

    # Retrieve predicted pose from vision.py
    current_pose = state_manager.get_pose()

    # Update Images to display in gui.py
    vision.update_images()
    gui.set_webcam_image(*state_manager.get_all_opencv_images())

    # Update Pose Preview Indicator in gui.py
    gui.update_pose(current_pose)
    gui.update_pose_image()
    gui.update_pose_text()
    gui.update_debug_landmarks(state_manager.get_landmark_string())

    gui.window.after(1, update)

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--collect', action='store_true', help='Starte den Datensammler')
    parser.add_argument('--label', type=str, help='Label für Datensammlung')
    parser.add_argument('--seconds', type=float, help='Dauer der Aufnahme')
    parser.add_argument('--csv', type=str, help='Pfad zur CSV-Datei')
    parser.add_argument('--fps', type=float, help='Samplingrate')
    parser.add_argument('--source', type=str, choices=['auto', 'vision', 'camera'], help='Frame-Quelle')
    parser.add_argument('--camera-index', type=int, help='Kameraindex')
    args = parser.parse_args()

    if args.collect:
        new_argv = ['collect.py']
        if args.label is not None:
            new_argv += ['--label', args.label]
        if args.seconds is not None:
            new_argv += ['--seconds', str(args.seconds)]
        if args.csv is not None:
            new_argv += ['--csv', args.csv]
        if args.fps is not None:
            new_argv += ['--fps', str(args.fps)]
        if args.source is not None:
            new_argv += ['--source', args.source]
        if args.camera_index is not None:
            new_argv += ['--camera-index', str(args.camera_index)]

        sys.argv = new_argv
        collect.main()
    else:
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