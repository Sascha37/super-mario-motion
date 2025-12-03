"""
Resolve resource file paths for both normal execution and PyInstaller builds.
Returns absolute paths that work whether files live next to the script or in
the temporary _MEIPASS directory of a packaged executable.
"""

import os
import sys


def resource_path(rel_path):
    if hasattr(sys, '_MEIPASS'):
        # noinspection PyProtectedMember
        return os.path.join(sys._MEIPASS, rel_path)
    return os.path.join(os.path.dirname(__file__), rel_path)
