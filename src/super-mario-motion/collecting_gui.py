import sys
import tkinter as tk
import threading
import collect
from tkinter import ttk
from pathlib import Path

from PIL import ImageTk, Image

COLLECTION_STEPS = [
    ("standing", 10),
    ("walking_left", 10),
    ("walking_right", 10),
    ("jumping", 10),
]
CSV_PATH = "pose_samples.csv"
FPS = 30

pose = ""

# Width and Height
window_width = 650
window_height = 700

option_menu_width = 17

webcam_image_width = 612
webcam_image_height = 408

# Colors
color_background = '#202326'
color_foreground = '#141618'
color_white = '#FFFFFF'

# Filepaths for images that are being used on init
path_data_folder = Path(__file__).parent / "images"
path_image_webcam_sample = path_data_folder / 'webcam_sample.jpg'

# Paddings
label_webcam_top_padding = 20
edge_padding_default = 20
horizontal_padding = (window_width - webcam_image_width) // 2


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
    except FileNotFoundError as e:
        print(f"Error: File not found: {e}")
        print("Exiting...")
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
        padx=(horizontal_padding, horizontal_padding))

    # Frame containing UI Elements located on the bottom left
    frame_bottom_left = tk.Frame(
        window,
        bg=color_foreground)

    frame_bottom_left.grid(
        row=1,
        column=0,
        padx=horizontal_padding,
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

    # Custom ttk Style for Combobox
    style = ttk.Style()
    style.theme_use('default')
    style.configure("Custom.TCombobox",
                    fieldbackground=color_foreground,
                    background = color_foreground,
                    foreground ="white"
        )
    style.map("Custom.TCombobox",
            fieldbackground=[("readonly",color_foreground)],
            foreground=[("readonly","white")],
            background=[("readonly",color_foreground)])
    # What to do when ComboboxSelected

    def clear_combobox_selection(event):
        event.widget.selection_clear()

    # Preview Option Menu
    global selected_preview
    selected_preview = tk.StringVar()

    option_menu_preview = ttk.Combobox(
        frame_bottom_left,
        textvariable=selected_preview,
        state="readonly",
        style="Custom.TCombobox"
    )
    option_menu_preview.bind("<<ComboboxSelected>>", clear_combobox_selection)
    option_menu_preview['values'] = ["Webcam", "Webcam + Skeleton", "Skeleton Only"]
    option_menu_preview.current(0)

    option_menu_preview.grid(
        row=0,
        column=1
        )

    # Debug Checkbox
    global allow_debug_info
    allow_debug_info = tk.IntVar(value=1)

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

    # Frame containing UI Elements located on the bottom right

    frame_bottom_right = tk.Frame(
        window,
        bg=color_foreground)

    frame_bottom_right.grid(
        row=1,
        column=1,
        padx=horizontal_padding,
        pady=(20,0)
    )

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

    global label_status
    label_status = tk.Label(
        window,
        bg=color_background,
        fg=color_white,
        text="",
        font=("Consolas", 30)
    )
    label_status.grid(row=2, column=0, columnspan=2, pady=(60,0))

    window.after(500, start_sequence)


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

    # calculate the source and destination image ratios
    img = Image.fromarray(array)
    src_w, src_h = img.size
    dst_w, dst_h = webcam_image_width, webcam_image_height
    src_ratio = src_w / src_h
    dst_ratio = dst_w / dst_h

    # keep the aspect ratio and resize the image
    if src_ratio > dst_ratio:
        new_w = dst_w
        new_h = int(dst_w / src_ratio)
    else:
        new_h = dst_h
        new_w = int(dst_h * src_ratio)

    # add black bars to the resized image to maintain webcam preview size
    img = img.resize((new_w, new_h), Image.LANCZOS)
    canvas = Image.new('RGB', (dst_w, dst_h), (0, 0, 0))
    canvas.paste(img, ((dst_w - new_w) // 2, (dst_h - new_h) // 2))
    image = ImageTk.PhotoImage(canvas)

    label_webcam.config(image=image)
    label_webcam.image = image

def update_pose(new_pose):
    global pose
    pose = new_pose


def update_debug_landmarks(landmarks):
    label_debug_landmarks.config(
        text = landmarks if allow_debug_info.get() else "")

def start_sequence():
    run_step(0)

def run_step(index):
    if index >= len(COLLECTION_STEPS):
        label_status.config(text="Fertig. Fenster schließt nach 5 Sekunden.")
        window.after(5000, window.destroy)
        return

    pose_name, seconds = COLLECTION_STEPS[index]
    show_countdown(5, pose_name, seconds, index)

def show_countdown(n, pose_name, seconds, index):
    if n == 0:
        label_status.config(text=f"Aufnahme: {pose_name}")
        threading.Thread(
            target=record_pose,
            args=(pose_name, seconds, index),
            daemon=True
        ).start()
        return

    label_status.config(text=f"{pose_name} in {n} …")
    window.after(1000, show_countdown, n - 1, pose_name, seconds, index)

def record_pose(pose_name, seconds, index):
    sys.argv = [
        "collect.py",
        "--label", pose_name,
        "--seconds", str(seconds),
        "--csv", CSV_PATH,
        "--fps", str(FPS),
        "--source", "auto",
    ]
    collect.main()

    window.after(500, lambda: run_step(index + 1))