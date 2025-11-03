import sys
import tkinter as tk
from tkinter import ttk
from pathlib import Path

from PIL import ImageTk, Image

pose = ""

# Width and Height
window_width = 650
window_height = 700

option_menu_width = 17

webcam_image_width = 612
webcam_image_height = 408

gamepad_image_width = 200
gamepad_image_height = 100

# Colors
color_background = '#202326'
color_foreground = '#141618'
color_white = '#FFFFFF'

# Filepaths for images that are being used on init
path_data_folder = Path(__file__).parent / "data"
path_image_webcam_sample = path_data_folder / 'webcam_sample.jpg'
path_image_pose_default = path_data_folder / 'standing.png'
path_image_gamepad = path_data_folder / 'gamepad.png'

# Paddings
label_webcam_top_padding = 20
edge_padding_default = 20


# Function gets called once in main.py once the program starts
def init():
    global window
    window = tk.Tk()

    window.title('Super Mario Motion')
    window.minsize(window_width, window_height)
    window.maxsize(window_width, window_height)

    window.configure(background=color_background)

    # Loading default images
    try:
        image_webcam_sample = ImageTk.PhotoImage(
            Image.open(path_image_webcam_sample).resize((webcam_image_width, webcam_image_height), Image.LANCZOS))
        image_pose = ImageTk.PhotoImage(Image.open(path_image_pose_default).resize((100, 100), Image.LANCZOS))
        image_gamepad = ImageTk.PhotoImage(Image.open(path_image_gamepad).resize((gamepad_image_width, gamepad_image_height), Image.LANCZOS))
    except FileNotFoundError:
        print("Error: File not found")
        sys.exit(1)

    # Label displaying Webcam Preview
    global label_webcam
    label_webcam = tk.Label(
        window,
        image=image_webcam_sample,
        bd=0)
    label_webcam.image = image_webcam_sample
    label_webcam.grid(
        row=0,
        column=0,
        columnspan=2,
        pady=(label_webcam_top_padding,0),
        padx=(edge_padding_default,0))

    # Frame containing UI Elements located on the bottom left
    frame_bottom_left = tk.Frame(
        window,
        bg=color_foreground)

    frame_bottom_left.grid(
        row=1,
        column=0,
        padx=edge_padding_default,
        pady=(5,0)
    )

    # Text Label "Preview:"
    label_preview = tk.Label(
        frame_bottom_left,
        bg=color_foreground,
        fg=color_white,
        text = "Preview:")
    label_preview.grid(
        row=0,
        column=0)

    # Preview Option Menu
    global selected_preview
    selected_preview = tk.StringVar()

    option_menu_preview = ttk.Combobox(
        frame_bottom_left,
        textvariable=selected_preview
    )

    option_menu_preview['values'] = ["Webcam", "Webcam + Skeleton", "Skeleton Only"]
    option_menu_preview.current(0)

    option_menu_preview.grid(
        row=0,
        column=1
        )

    # Text Label "Mode:"
    label_mode = tk.Label(
        frame_bottom_left,
        bg=color_foreground,
        fg=color_white,
        text = "Mode:")

    label_mode.grid(
        row=1,
        column=0,
        )

    # Mode Option Menu
    global selected_mode
    selected_mode = tk.StringVar()
    option_menu_mode = ttk.Combobox(
        frame_bottom_left,
        textvariable=selected_mode,
        )
    option_menu_mode['values'] = ["Simple", "Full-body"]
    option_menu_mode.current(0)

    option_menu_mode.grid(
        row=1,
        column=1,
        )

    # Debug Checkbox
    global allow_debug_info
    allow_debug_info = tk.IntVar()

    checkbox_debug_info = tk.Checkbutton(
        frame_bottom_left,
        text='Debug Info',
        bg=color_foreground,
        fg=color_white,
        selectcolor=color_background,
        highlightthickness=0,
        bd=0,
        variable=allow_debug_info,
        onvalue=1,
        offvalue=0,
        width=20,
        height=2)

    checkbox_debug_info.grid(
        row=2,
        column=0,
        columnspan=2
        )

    # Send Inputs Checkbox
    global send_keystrokes
    send_keystrokes = tk.IntVar()

    checkbox_toggle_inputs = tk.Checkbutton(
        frame_bottom_left,
        text='Send Inputs',
        bg=color_foreground,
        fg=color_white,
        selectcolor=color_background,
        highlightthickness=0,
        bd=0,
        variable=send_keystrokes,
        onvalue=1,
        offvalue=0,
        width=20,
        height=2)

    checkbox_toggle_inputs.grid(
        row=3,
        column=0,
        columnspan=2
        )


    # Frame containing UI Elements located on the bottom right

    frame_bottom_right = tk.Frame(
        window,
        bg=color_foreground)

    frame_bottom_right.grid(
        row=1,
        column=1,
        padx=edge_padding_default,
        pady=(20,0)
    )
    # Image Label Virtual Gamepad Visualizer
    global label_virtual_gamepad_visualizer
    label_virtual_gamepad_visualizer = tk.Label(
        frame_bottom_right,
        image=image_gamepad,
        bd=0)
    label_virtual_gamepad_visualizer.image = image_gamepad
    label_virtual_gamepad_visualizer.grid(
        row=0,
        column=0)

    # Image Label designated for displaying the current pose
    global label_pose_visualizer
    label_pose_visualizer = tk.Label(
        frame_bottom_right,
        image=image_pose,
        bd=0)
    label_pose_visualizer.image = image_pose
    label_pose_visualizer.grid(
        row=0,
        column=1)

    # Text Label "Current pose:"
    global label_current_pose
    label_current_pose = tk.Label(
        frame_bottom_right,
        bg=color_foreground,
        fg=color_white,
        text = "Current pose:" + pose)

    label_current_pose.grid(
        row=1,
        column=0,
        columnspan=2)

    # Debug Text Label Displaying Landmark Coordinates
    global label_debug_landmarks
    label_debug_landmarks = tk.Label(
        frame_bottom_right,
        bg=color_foreground,
        fg=color_white,
        width=60,
        height=10,
        text = "",
        font=("Consolas", 6))

    label_debug_landmarks.grid(
        row=2,
        column=0,
        columnspan=2)
    # Init completed
    print(Path(__file__).name + " initialized")


# set_webcam_image and set_pose_image are supposed to be called in the update-loop in main.py
def set_webcam_image(webcam,webcam_skeleton,only_sekeleton):
    match selected_preview.get():
        case "Webcam": array = webcam
        case "Webcam + Skeleton": array = webcam_skeleton
        case "Skeleton Only": array = only_sekeleton
        case _: array = webcam

    if array is None:
        return

    array = array[:, ::-1, :]   # flip the camera horizontally only for the user
    image = ImageTk.PhotoImage(Image.fromarray(array).resize((webcam_image_width, webcam_image_height), Image.LANCZOS))
    label_webcam.config(image=image)
    label_webcam.image = image

def set_gamepad_image(updated_gamepad_image):
    if gamepad_image is None:
        return
    image = ImageTk.PhotoImage(updated_gamepad_image.resize((gamepad_image_width, gamepad_image_height), Image.LANCZOS))
    label_virtual_gamepad_visualizer.config(image=image)
    label_virtual_gamepad_visualizer.image = image

def update_pose(new_pose):
    global pose
    pose = new_pose

def update_pose_image():
    valid_poses = ["standing", "jumping", "crouching", "throwing", "walking_right", "walking_left", "running_right",
                   "running_left"]
    if pose in valid_poses:
        try:
            window.image_pose = ImageTk.PhotoImage(
                Image.open(path_data_folder / (pose + '.png')).resize((100, 100), Image.LANCZOS))
        except FileNotFoundError:
            print("Error: File not found")
            sys.exit(1)

        label_pose_visualizer.config(image=window.image_pose)
        label_pose_visualizer.image = window.image_pose
    else:
        print("Invalid pose")

def update_pose_text():
    label_current_pose.config(
        text = "Current pose:" + pose)

def update_debug_landmarks(landmarks):
    label_debug_landmarks.config(
        text = landmarks if allow_debug_info.get() else "")

def get_boolean_send_keystrokes():
    return send_keystrokes.get()


def get_active_mode():
    return selected_mode.get()
