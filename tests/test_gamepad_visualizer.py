import os

from PIL import Image

import super_mario_motion.gamepad_visualizer as gv
from super_mario_motion import path_helper as ph
from super_mario_motion.gamepad_visualizer import get_base_image, \
    pose_to_buttons

last_orientation: str = "right"


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
    gv.last_orientation = "right"
    assert pose_to_buttons("jumping") == ["A", "DPAD_RIGHT"]
    gv.last_orientation = "left"
    assert pose_to_buttons("jumping") == ["A", "DPAD_LEFT"]
    assert pose_to_buttons("throwing") == ["B"]
    assert pose_to_buttons("running_right") == ["DPAD_RIGHT", "B"]
    assert pose_to_buttons("crouching") == ["DPAD_DOWN"]
    assert pose_to_buttons("running_left") == ["DPAD_LEFT", "B"]
    assert pose_to_buttons("walking_left") == ["DPAD_LEFT"]
    assert pose_to_buttons("walking_right") == ["DPAD_RIGHT"]
    # TODO: add test for swimming
    assert pose_to_buttons("not_defined") == []


def test_draw_highlight_overlay():
    image = Image.new('RGBA', (200, 100))

    res_image1 = gv.create_gamepad_image(
        pose="walking_right",
        send_active=False,
        base_image_=image
        )

    res_image2 = gv.create_gamepad_image(
        pose="walking_right", base_image_=image
        )

    assert image.mode == 'RGBA'
    assert res_image1.size == image.size

    expected = image.convert("RGB")

    # the image should remain the same because no inputs are sent
    assert images_equal(res_image1, expected)
    # the image should be different because an input is being sent and
    # highlighted
    assert not images_equal(res_image2, expected)
