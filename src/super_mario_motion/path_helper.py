import os
import sys


# When its running as a single file executable it points to the _MEIPASS
# folder
def resource_path(rel_path):
    if hasattr(sys, '_MEIPASS'):
        # noinspection PyProtectedMember
        return os.path.join(sys._MEIPASS, rel_path)
    return os.path.join(os.path.dirname(__file__), rel_path)
