import os

import super_mario_motion.path_helper as ph
from super_mario_motion.path_helper import resource_path


def test_resource_path_normal_environment():
    expected_dir = os.path.dirname(ph.__file__)

    result = resource_path("file.txt")
    expected = os.path.join(expected_dir, "file.txt")

    assert result == expected
