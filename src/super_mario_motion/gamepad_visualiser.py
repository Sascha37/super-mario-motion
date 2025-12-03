import os
from typing import Iterable, List

from PIL import Image, ImageDraw

from super_mario_motion import path_helper as ph

"""
Utilities for mapping pose labels to virtual gamepad inputs and rendering
a gamepad image with highlighted buttons. Provides functions to load the
base controller image, translate poses into button presses, and draw
visual overlays indicating active inputs.
"""

GAMEPAD_PATH = ph.resource_path(os.path.join("images", "gamepad.png"))

BUTTON_POSITIONS = {
    "DPAD_UP": (0.22, 0.28, 0.06),
    "DPAD_DOWN": (0.22, 0.73, 0.06),
    "DPAD_LEFT": (0.11, 0.5, 0.06),
    "DPAD_RIGHT": (0.33, 0.5, 0.06),

    "SELECT": (0.49, 0.76, 0.06),
    "START": (0.63, 0.76, 0.06),

    "A": (0.78, 0.55, 0.06),
    "B": (0.87, 0.38, 0.06),
    }

base_image: Image.Image | None = None
last_orientation: str = "right"


def get_base_image() -> Image.Image:
    """Load and cache the base gamepad image.

    Returns:
        Image.Image: The base RGBA gamepad image.
    """
    global base_image
    if base_image is None:
        base_image = Image.open(GAMEPAD_PATH).convert("RGBA")
    return base_image


def pose_to_buttons(pose: str) -> List[str]:
    """Map a pose label to a list of virtual gamepad buttons.

    The function keeps track of the last left/right orientation to decide
    in which direction to jump.

    Args:
        pose: Pose label (e.g. 'standing', 'running_right', 'jumping').

    Returns:
        list[str]: List of button names that should be considered pressed.
    """
    global last_orientation
    match pose:
        case "standing":
            return []
        case "walking_right":
            last_orientation = "right"
            return ["DPAD_RIGHT"]
        case "walking_left":
            last_orientation = "left"
            return ["DPAD_LEFT"]
        case "running_right":
            last_orientation = "right"
            return ["DPAD_RIGHT", "B"]
        case "running_left":
            last_orientation = "left"
            return ["DPAD_LEFT", "B"]
        case "crouching":
            return ["DPAD_DOWN"]
        case "throwing":
            return ["B"]
        case "jumping":
            return ["A",
                    "DPAD_RIGHT" if last_orientation == "right" else
                    "DPAD_LEFT"]
        case _:
            return []


def draw_highlight_overlay(
        base_size: tuple[int, int],
        pressed: Iterable[str]
        ) -> Image.Image:
    """Create an RGBA overlay that highlights pressed buttons.

    Args:
        base_size: (width, height) of the target gamepad image.
        pressed: Iterable of button names to highlight.

    Returns:
        Image.Image: Transparent overlay image with colored highlights.
    """
    w, h = base_size
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    for btn in pressed:
        if btn not in BUTTON_POSITIONS:
            continue
        x_r, y_r, r_r = BUTTON_POSITIONS[btn]
        cx, cy = int(w * x_r), int(h * y_r)
        r = int(min(w, h) * r_r)

        if btn.startswith("DPAD"):
            color = (66, 135, 245, 180)
        elif btn in ("A", "B"):
            color = (235, 64, 52, 200)
        else:
            color = (255, 215, 0, 180)

        bbox = (cx - r, cy - r, cx + r, cy + r)
        draw.rectangle(bbox, fill=color, outline=(0, 0, 0, 220), width=2)

    return overlay


def create_gamepad_image(
        pose: str, send_active: bool = True,
        base_image_: Image.Image | None = None
        ) -> Image.Image:
    """Create a gamepad image with highlighted buttons for a given pose.

    Args:
        pose: Pose label that will be mapped to button presses.
        send_active: If False, no buttons are highlighted even if the pose
            would trigger them.
        base_image_: Optional base image to draw on. If None, the default
            gamepad image from disk is used.

    Returns:
        Image.Image: Final RGB image of the gamepad with highlights.
    """
    base = (base_image_.convert(
        "RGBA"
        ) if base_image_ is not None else get_base_image())
    img = base.copy()

    if send_active:
        pressed = pose_to_buttons(pose)
        if pressed:
            overlay = draw_highlight_overlay(img.size, pressed)
            img = Image.alpha_composite(img, overlay)

    return img.convert("RGB")
