import getpass
import os
import platform
import random
import sys
import threading
import tkinter as tk
import webbrowser
from datetime import datetime
from pathlib import Path
from tkinter import ttk

import cv2
from PIL import Image, ImageTk

from super_mario_motion import collect, game_launcher, path_helper as ph, \
    vision, vision_ml
from super_mario_motion.state import StateManager

pose = ""

array = None
window = None
frame_bottom_left, frame_bottom_right = None, None
label_webcam = None
selected_preview, selected_mode = None, None
allow_debug_info, send_keystrokes, checkbox_toggle_inputs = None, None, None
(label_virtual_gamepad_visualizer, label_pose_visualizer, label_current_pose,
 label_debug_landmarks) = None, None, None, None
button_collect_start, label_collect_status = None, None

# Webcam preview
webcam_image_width = 612
webcam_image_height = 408

# Gamepad
gamepad_image_width = 200
gamepad_image_height = 100

# Colors
color_background = '#202326'
color_dark_widget = '#141618'
color_white = '#FFFFFF'
color_disabled_background = '#444444'
color_disabled_text = '#888888'
# Filepaths for images that are being used on init
path_image_webcam_sample = ph.resource_path(
    os.path.join("images", "webcam_sample.jpg")
    )
path_image_pose_default = ph.resource_path(
    os.path.join("images", "unknown.png")
    )
path_image_gamepad = ph.resource_path(os.path.join("images", "gamepad.png"))

# Paddings
label_webcam_top_padding = 20
edge_padding_default = 20
horizontal_padding = (650 - webcam_image_width) // 2
frame_padding_y = (20, 0)

# Window size
window_width = webcam_image_width + 2 * edge_padding_default
window_height = 750

# Collecting
COLLECTION_STEPS = [
    ("standing", 10),
    ("walking_left", 10),
    ("running_left", 10),
    ("walking_right", 10),
    ("running_right", 10),
    ("jumping", 10),
    ("crouching", 10),
    ("throwing", 10),
    ("swimming", 10),
    ]
CSV_PATH = "pose_samples.csv"
FPS = 30
current_run_csv = CSV_PATH

# Will hold the randomized order for a single collection run
collection_order = None

collecting = False
collect_stop = False
after_handles = []

# StateManager
state_manager = StateManager()


# Function gets called once in main.py once the program starts
def init():
    """Initialize the main GUI window and all static widgets.

    This sets up layout, styles, default images, and registers callbacks
    for mode selection, buttons, and window close events.
    """
    global window
    global frame_bottom_left, frame_bottom_right
    global label_webcam
    global selected_preview, selected_mode
    global allow_debug_info, send_keystrokes, checkbox_toggle_inputs
    global label_virtual_gamepad_visualizer, label_pose_visualizer, \
        label_current_pose, \
        label_debug_landmarks
    global button_collect_start, label_collect_status

    window = tk.Tk()
    window.title('Super Mario Motion')
    window.minsize(window_width, window_height)
    #  window.maxsize(window_width, window_height)
    window.configure(background=color_background)

    window.protocol("WM_DELETE_WINDOW", close)

    # always open the gui in the center of the screen
    system = platform.system()

    if system in ("Windows", "Darwin"):  # calculation for Windows and macOS
        window.withdraw()
        window.update_idletasks()

        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        window.geometry(f"{window_width}x{window_height}+{x}+{y}")
        window.deiconify()

    if system == "Darwin":
        # always open the gui on top of all other windows for macOS
        window.lift()
        window.attributes('-topmost', True)
        window.after(100, lambda: window.attributes('-topmost', False))

    # Loading default images
    try:
        image_webcam_sample = ImageTk.PhotoImage(
            Image.open(path_image_webcam_sample).resize(
                (webcam_image_width, webcam_image_height),
                Image.LANCZOS
                )
            )
        image_pose = ImageTk.PhotoImage(
            Image.open(path_image_pose_default).resize(
                (100, 100),
                Image.LANCZOS
                )
            )
        image_gamepad = ImageTk.PhotoImage(
            Image.open(path_image_gamepad).resize(
                (gamepad_image_width, gamepad_image_height),
                Image.LANCZOS
                )
            )
    except FileNotFoundError as e:
        print(f"Error: File not found: {e}")
        sys.exit(1)

    # Image Label for the preview of the webcam
    label_webcam = tk.Label(window, image=image_webcam_sample, bd=0)
    label_webcam.image = image_webcam_sample
    label_webcam.grid(
        row=0,
        column=0,
        columnspan=2,
        pady=(label_webcam_top_padding, 0),
        padx=(horizontal_padding, horizontal_padding)
        )

    # Frame Bottom Left
    frame_bottom_left = tk.Frame(window, bg=color_dark_widget)
    # Widgets on these rows expand evenly
    frame_bottom_left.columnconfigure(0, weight=1)
    frame_bottom_left.columnconfigure(1, weight=1)
    frame_bottom_left.grid(
        row=1,
        column=0,
        padx=(horizontal_padding, 0),
        pady=frame_padding_y,
        sticky="nw"
        )

    # Button "Launch Game"
    button_launch_game = ttk.Button(
        frame_bottom_left,
        text="Launch Game",
        command=start_game_button_action,
        style="Custom.TButton"
        )

    button_launch_game.grid(
        row=0,
        column=0,
        sticky="nsew"
        )

    # This button will be disabled if the paths
    # defined in game_launcher are invalid
    if not game_launcher.all_paths_valid:
        button_launch_game.state(["disabled"])

    # Button "Help"
    button_help = ttk.Button(
        frame_bottom_left,
        text="Help",
        command=open_help_menu,
        style="Custom.TButton"
        )

    button_help.grid(
        row=0,
        column=1,
        sticky="nsew"
        )

    # Separator
    separator = ttk.Separator(
        frame_bottom_left,
        orient=tk.HORIZONTAL,
        style="Custom.TSeparator"
        )
    separator.grid(
        row=1,
        column=0,
        columnspan=2,
        stick="ew",
        pady=30
        )

    # Text Label "Preview:"
    label_preview = tk.Label(
        frame_bottom_left,
        bg=color_dark_widget,
        fg=color_white,
        text="Preview:"
        )
    label_preview.grid(
        row=2,
        column=0
        )

    # Custom ttk Style for Combobox
    style = ttk.Style()
    style.theme_use('alt')
    style.configure(
        "Custom.TCombobox",
        fieldbackground=color_dark_widget,
        background=color_dark_widget,
        foreground="white"
        )
    style.map(
        "Custom.TCombobox",
        fieldbackground=[("readonly", color_dark_widget)],
        foreground=[("readonly", "white")],
        background=[("readonly", color_dark_widget)]
        )

    # Custom ttk Style for Buttons
    style.configure(
        "Custom.TButton",
        fieldbackground=color_dark_widget,
        background=color_dark_widget,
        foreground="white"
        )
    style.map(
        "Custom.TButton",
        background=[
            ("active", "white"),
            ("pressed", "white"),
            ("disabled", color_disabled_background),
            ],
        foreground=[
            ("active", "black"),
            ("pressed", "black"),
            ("disabled", color_disabled_text)
            ],
        embossed=[
            ("disabled", 0)
            ]
        )

    # Custom ttk Style for Separator
    style.configure(
        "Custom.TSeparator",
        background="black"
        )

    # This is needed to deselect the text inside of a ttk Combobox
    def clear_combobox_selection(event):
        event.widget.selection_clear()

    # Preview Combobox
    global selected_preview
    selected_preview = tk.StringVar()
    option_menu_preview = ttk.Combobox(
        frame_bottom_left,
        textvariable=selected_preview,
        state="readonly",
        style="Custom.TCombobox"
        )
    option_menu_preview.bind("<<ComboboxSelected>>", clear_combobox_selection)
    option_menu_preview['values'] = ["Webcam", "Webcam + Skeleton",
                                     "Skeleton Only"]
    option_menu_preview.current(0)
    option_menu_preview.grid(row=2, column=1)

    # "Mode:" Text Label
    label_mode = tk.Label(
        frame_bottom_left, bg=color_dark_widget,
        fg=color_white, text="Mode:"
        )
    label_mode.grid(row=3, column=0)

    # Mode Combobox
    global selected_mode
    selected_mode = tk.StringVar()

    # Gets called when the Mode Combobox is selected
    def on_mode_change(event):
        event.widget.selection_clear()
        apply_mode(selected_mode.get())

    option_menu_mode = ttk.Combobox(
        frame_bottom_left,
        textvariable=selected_mode,
        state="readonly",
        style="Custom.TCombobox"
        )
    option_menu_mode.bind("<<ComboboxSelected>>", on_mode_change)
    option_menu_mode['values'] = ["Simple", "Full-body", "Collect"]
    option_menu_mode.current(0)
    option_menu_mode.grid(row=3, column=1)

    # Debug Info Checkbox
    global allow_debug_info
    allow_debug_info = tk.IntVar(value=0)
    checkbox_debug_info = tk.Checkbutton(
        frame_bottom_left, text='Debug Info',
        bg=color_dark_widget, fg=color_white,
        selectcolor=color_background,
        highlightthickness=0, bd=0,
        variable=allow_debug_info, width=20,
        height=2
        )
    checkbox_debug_info.grid(
        row=4,
        column=0,
        columnspan=2,
        sticky="ew"
        )

    # Send Inputs Checkbox
    global send_keystrokes, checkbox_toggle_inputs
    send_keystrokes = tk.IntVar()
    checkbox_toggle_inputs = tk.Checkbutton(
        frame_bottom_left,
        text='Send Inputs',
        bg=color_dark_widget,
        fg=color_white,
        selectcolor=color_background,
        highlightthickness=0,
        bd=0, variable=send_keystrokes,
        width=20, height=2
        )
    checkbox_toggle_inputs.grid(
        row=5,
        column=0,
        columnspan=2,
        sticky="ew"
        )

    # Frame bottom right
    frame_bottom_right = tk.Frame(window, bg=color_dark_widget)
    frame_bottom_right.grid(
        row=1,
        column=1,
        padx=(0, horizontal_padding),
        pady=frame_padding_y,
        sticky="ne"
        )

    # gamepad
    global label_virtual_gamepad_visualizer
    label_virtual_gamepad_visualizer = tk.Label(
        frame_bottom_right,
        image=image_gamepad, bd=0
        )
    label_virtual_gamepad_visualizer.image = image_gamepad
    label_virtual_gamepad_visualizer.grid(row=0, column=0)

    # pose image
    global label_pose_visualizer
    label_pose_visualizer = tk.Label(
        frame_bottom_right, image=image_pose,
        bd=0
        )
    label_pose_visualizer.image = image_pose
    label_pose_visualizer.grid(row=0, column=1)

    # pose text
    global label_current_pose
    label_current_pose = tk.Label(
        frame_bottom_right,
        bg=color_dark_widget,
        fg=color_white,
        text="Current pose:" + pose
        )
    label_current_pose.grid(row=1, column=0, columnspan=2)

    # debug text
    global label_debug_landmarks
    label_debug_landmarks = tk.Label(
        frame_bottom_right, bg=color_dark_widget,
        fg=color_white,
        width=60, height=10, font=("Consolas", 6)
        )
    label_debug_landmarks.grid(row=2, column=0, columnspan=2)

    # Text Label for the collection status, visible during collect mode
    global label_collect_status, button_collect_start
    label_collect_status = tk.Label(
        window, bg=color_background,
        fg=color_white,
        font=("Consolas", 25)
        )
    label_collect_status.grid(row=2, column=0, columnspan=2, pady=(20, 0))
    label_collect_status.grid_remove()

    # Start Collecting ttk Button
    button_collect_start = ttk.Button(
        window,
        text="Start collecting",
        command=start_collect_sequence,
        style="Custom.TButton"
        )
    button_collect_start.grid(row=3, column=0, columnspan=2, pady=(10, 0))
    button_collect_start.grid_remove()

    print(Path(__file__).name + " initialized")


# set_webcam_image and set_pose_image are supposed to be called in the
# update-loop in main.py
def set_webcam_image(webcam, webcam_skeleton, only_skeleton):
    """Update the webcam preview image according to the selected preview mode.

    The input images are numpy arrays; this function mirrors the image for the
    user, letterboxes it to the fixed preview size, and updates the label.
    """
    global array
    match selected_preview.get():
        case "Webcam":
            array = webcam
        case "Webcam + Skeleton":
            array = webcam_skeleton
        case "Skeleton Only":
            array = only_skeleton
        case _:
            array = webcam

    if array is None:
        return

    array = array[:, ::-1, :]  # flip the camera horizontally only for the user
    # image = ImageTk.PhotoImage(Image.fromarray(array).resize((
    # webcam_image_width, webcam_image_height), Image.LANCZOS))

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


def set_gamepad_image(updated_gamepad_image):
    """Update the virtual gamepad preview image using the logic of
    gamepad_visualizer.py."""
    if updated_gamepad_image is None:
        return
    image = ImageTk.PhotoImage(
        updated_gamepad_image.resize(
            (gamepad_image_width, gamepad_image_height), Image.LANCZOS
            )
        )
    label_virtual_gamepad_visualizer.config(image=image)
    label_virtual_gamepad_visualizer.image = image


def update_pose(new_pose):
    global pose
    pose = new_pose


def update_pose_image():
    """Update the pose image icon based on the current pose name."""
    valid_poses = [
        "standing", "jumping", "crouching", "throwing",
        "walking_right", "walking_left", "running_right", "running_left",
        "swimming"
        ]
    if pose in valid_poses:
        try:
            window.image_pose = ImageTk.PhotoImage(
                Image.open(
                    ph.resource_path(os.path.join("images", pose + ".png"))
                    ).resize(
                    (100, 100), Image.LANCZOS
                    )
                )
        except FileNotFoundError:
            print("Error: File not found")
            sys.exit(1)
    else:
        # Display question mark symbol if unknown pose is performed
        window.image_pose = ImageTk.PhotoImage(
            Image.open(path_image_pose_default).resize(
                (100, 100),
                Image.LANCZOS
                )
            )

    label_pose_visualizer.config(image=window.image_pose)
    label_pose_visualizer.image = window.image_pose


def update_pose_text():
    label_current_pose.config(text="Current pose:" + pose)


def update_debug_landmarks(landmarks):
    label_debug_landmarks.config(
        text=landmarks if allow_debug_info.get() else ""
        )


def apply_mode(mode: str):
    """Switch the UI between play modes and collect mode.

    Args:
        mode: One of "Simple", "Full-body", "Collect".
    """
    global label_collect_status, button_collect_start
    global label_virtual_gamepad_visualizer, label_pose_visualizer, \
        label_current_pose
    global checkbox_toggle_inputs, allow_debug_info, send_keystrokes

    if mode == "Collect":
        allow_debug_info.set(1)
        send_keystrokes.set(0)

        # Hide widgets that are not relevant
        checkbox_toggle_inputs.grid_remove()
        label_virtual_gamepad_visualizer.grid_remove()
        label_pose_visualizer.grid_remove()
        label_current_pose.grid_remove()

        # Display collect mode specific widgets
        label_collect_status.grid()
        button_collect_start.grid()
        _set_collect_button(starting=False)

    else:
        checkbox_toggle_inputs.grid()

        # Display play mode specific widgets
        label_virtual_gamepad_visualizer.grid()
        label_pose_visualizer.grid()
        label_current_pose.grid()

        # Hide collect mode specific widgets
        label_collect_status.grid_remove()
        _set_collect_button(starting=False)
        button_collect_start.grid_remove()


def _set_collect_button(starting: bool):
    """Configure the collect button text and callback based on state.

    Args:
        starting: If True, button becomes a “Stop collecting” button.
    """
    if starting:
        button_collect_start.config(
            text="Stop collecting",
            command=stop_collect_sequence
            )
    else:
        button_collect_start.config(
            text="Start collecting",
            command=start_collect_sequence
            )


# Collecting mode-specific functions:
def _schedule_after(ms, func, *args):
    aid = window.after(ms, func, *args)
    after_handles.append(aid)
    return aid


def _cancel_scheduled():
    while after_handles:
        aid = after_handles.pop()
        try:
            window.after_cancel(aid)
        except tk.TclError:
            pass


def start_collect_sequence():
    """Start a full pose collection run with randomized pose order."""
    global collecting, collect_stop, current_run_csv, collection_order
    if collecting:
        return
    collect_stop = False
    collecting = True
    _cancel_scheduled()
    # Randomize the order of collection steps for this run
    collection_order = random.sample(COLLECTION_STEPS, len(COLLECTION_STEPS))

    runs_dir = Path(state_manager.get_data_folder_path())

    user = getpass.getuser()
    current_run_csv = str(
        runs_dir / f"pose_samples_{user}_"
                   f"{datetime.now().strftime('%d.%m.%Y_%H.%M')}.csv"
        )
    label_collect_status.config(text="Starting Sequence…")
    _set_collect_button(starting=True)
    run_collect_step(0)


def stop_collect_sequence():
    global collecting, collect_stop
    collect_stop = True
    collecting = False
    _cancel_scheduled()
    label_collect_status.config(text="Stopped.")
    _set_collect_button(starting=False)


def run_collect_step(index: int):
    """Run a single step of the collection sequence.

    Advances through COLLECTION_STEPS (or the randomized order) and
    triggers countdown and recording for each pose.
    """
    global collecting, collect_stop, collection_order
    if collect_stop:
        _set_collect_button(starting=False)
        return

    steps = collection_order if collection_order else COLLECTION_STEPS

    if index >= len(steps):
        _cancel_scheduled()
        label_collect_status.config(text="Finished.")
        collecting = False
        collect_stop = False
        collection_order = None
        _set_collect_button(starting=False)
        return

    pose_name, seconds = steps[index]
    show_collect_countdown(3, pose_name, seconds, index)


def show_collect_countdown(n: int, pose_name: str, seconds: float, index: int):
    """Show a countdown before recording a specific pose.

    When countdown reaches zero, starts recording for the given pose.
    """
    if collect_stop:
        return
    if n == 0:
        label_collect_status.config(
            text=f"Recording: {pose_name} ({int(seconds)}s)"
            )
        if not collect_stop:
            threading.Thread(
                target=record_collect_pose,
                args=(pose_name, seconds, index),
                daemon=True
                ).start()
            show_recording_countdown(int(seconds), pose_name, index)
        return

    label_collect_status.config(text=f"{pose_name} in {n} …")
    _schedule_after(
        1000, show_collect_countdown, n - 1, pose_name, seconds,
        index
        )


def show_recording_countdown(remaining: int, pose_name: str, index: int):
    if collect_stop:
        return
    if remaining <= 0:
        return
    label_collect_status.config(text=f"Recording: {pose_name} ({remaining}s)")
    _schedule_after(
        1000, show_recording_countdown, remaining - 1, pose_name,
        index
        )


def record_collect_pose(pose_name: str, seconds: float, index: int):
    """Record pose samples for the given duration and schedule next step.

    This function runs in a worker thread and calls collect.main()
    with appropriate CLI arguments.
    """
    if collect_stop:
        return
    global current_run_csv
    sys.argv = [
        "collect.py",
        "--label", pose_name,
        "--seconds", str(seconds),
        "--csv", current_run_csv,
        "--fps", str(FPS),
        "--source", "auto",
        ]
    collect.main()
    if not collect_stop:
        _schedule_after(500, lambda: run_collect_step(index + 1))


# Takes in a Path and opens this path as a file in the default browser
def open_browser(path):
    webbrowser.open_new_tab(path.as_uri())


# gets called by the "Help"-Button, calls open_browser in a separate thread,
# so that the main thread does not have to wait for the browser to start up
# (~5 seconds)
def open_help_menu():
    if state_manager.get_standalone:
        help_path = os.path.join("help", "help_page.pdf")
    else:
        help_path = os.path.join("..", "..", "docs", "help", "help_page.pdf")

    help_file_path = Path(
        ph.resource_path(
            help_path
            )
        )
    threading.Thread(
        target=open_browser, args=(help_file_path,),
        daemon=True
        ).start()


# os.path.join("images","webcam_sample.jpg")
# gets called by the "Start Game"-Button
def start_game_button_action():
    threading.Thread(target=game_launcher.launch_game, daemon=True).start()


def close():
    try:
        vision_ml.stop()
    except (RuntimeError, AttributeError, cv2.error) as e:
        print("ML shutdown warning:", e)

    try:
        vision.stop_cam()
    except (RuntimeError, AttributeError, cv2.error) as e:
        print("Camera shutdown warning:", e)

    window.destroy()
