import os

from PIL import Image

from super_mario_motion import path_helper as ph
from super_mario_motion.gamepad_visualizer import get_base_image, \
    pose_to_buttons


def images_equal(image1, image2):
    from PIL import ImageChops
    diff = ImageChops.difference(image1, image2)
    return not diff.getbbox()


def test_get_base_image():
    image = get_base_image()
    expected_image = Image.open(
        ph.resource_path(
            os.path.join(
                "images",
                'gamepad.png'
                )
            )
        )
    assert images_equal(image, expected_image)


def test_pose_to_buttons():
    assert pose_to_buttons("standing") == []
    _last_orientation = "right"
    assert pose_to_buttons("jumping") == ["A", "DPAD_RIGHT"]
    _last_orientation = "left"
    assert pose_to_buttons("jumping") == ["A", "DPAD_LEFT"]
    assert pose_to_buttons("throwing") == ["B"]
    assert pose_to_buttons("running_right") == ["DPAD_RIGHT", "B"]
    assert pose_to_buttons("crouching") == ["DPAD_DOWN"]
    assert pose_to_buttons("running_left") == ["DPAD_LEFT", "B"]
    assert pose_to_buttons("walking_left") == ["DPAD_LEFT"]
    assert pose_to_buttons("walking_right") == ["DPAD_RIGHT"]
    assert pose_to_buttons(_) == []


def test_draw_highlight_overlay():
    pass
