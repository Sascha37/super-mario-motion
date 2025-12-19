"""Central shared state container for the application.

StateManager stores pose predictions, mode settings, image frames, landmark
strings and send-permission flags as class-level attributes. GUI, vision,
vision_ML and input modules all read/write to this manager, providing a simple
synchronized state interface without requiring instance passing.
"""


class StateManager:
    # Init default values
    pose = "default"
    pose_full_body = "default"

    landmark_string = "default"

    opencv_image_webcam = None
    opencv_image_webcam_skeleton = None
    opencv_image_skeleton_only = None

    gui_checkbox_send_permission = False

    gui_current_mode = "Simple"
    gui_control_scheme = "Original (RetroArch)"
    custom_key_mapping = {}

    pose_landmarks = None

    standalone = False

    data_folder_path = None

    config_path = None

    invalid_config = False

    # Getter
    @classmethod
    def get_pose(cls):
        return cls.pose

    @classmethod
    def get_pose_full_body(cls):
        return cls.pose_full_body

    @classmethod
    def get_landmark_string(cls):
        return cls.landmark_string

    @classmethod
    def get_all_opencv_images(cls):
        return (
            cls.opencv_image_webcam,
            cls.opencv_image_webcam_skeleton,
            cls.opencv_image_skeleton_only,
            )

    @classmethod
    def get_opencv_image_webcam(cls):
        return cls.opencv_image_webcam

    @classmethod
    def get_send_permission(cls):
        return cls.gui_checkbox_send_permission

    @classmethod
    def get_current_mode(cls):
        return cls.gui_current_mode

    @classmethod
    def get_pose_landmarks(cls):
        return cls.pose_landmarks

    @classmethod
    def get_control_scheme(cls):
        return cls.gui_control_scheme

    @classmethod
    def get_standalone(cls):
        return cls.standalone

    @classmethod
    def get_data_folder_path(cls):
        return cls.data_folder_path

    @classmethod
    def get_custom_key_mapping(cls):
        return cls.custom_key_mapping

    @classmethod
    def get_config_path(cls):
        return cls.config_path

    @classmethod
    def get_invalid_config(cls):
        return cls.invalid_config

    # Setter
    @classmethod
    def set_pose(cls, new_pose):
        cls.pose = new_pose

    @classmethod
    def set_pose_full_body(cls, new_pose):
        cls.pose_full_body = new_pose

    @classmethod
    def set_landmark_string(cls, new_landmark_string):
        cls.landmark_string = new_landmark_string

    @classmethod
    def set_all_opencv_images(
        cls, new_webcam, new_webcam_skeleton,
        new_skeleton_only
            ):
        cls.opencv_image_webcam = new_webcam
        cls.opencv_image_webcam_skeleton = new_webcam_skeleton
        cls.opencv_image_skeleton_only = new_skeleton_only

    @classmethod
    def set_send_permission(cls, new_send_permission):
        cls.gui_checkbox_send_permission = new_send_permission

    @classmethod
    def set_current_mode(cls, new_mode):
        cls.gui_current_mode = new_mode

    @classmethod
    def set_pose_landmarks(cls, new_landmarks):
        cls.pose_landmarks = new_landmarks

    @classmethod
    def set_standalone(cls, new_standalone):
        cls.standalone = new_standalone

    @classmethod
    def set_control_scheme(cls, new_scheme):
        cls.gui_control_scheme = new_scheme

    @classmethod
    def set_data_folder_path(cls, new_data_folder_path):
        cls.data_folder_path = new_data_folder_path

    @classmethod
    def set_custom_key_mapping(cls, new_mapping):
        cls.custom_key_mapping = new_mapping

    @classmethod
    def set_config_path(cls, new_config_path):
        cls.config_path = new_config_path

    @classmethod
    def set_invalid_config(cls, new_invalid_config):
        cls.invalid_config = new_invalid_config
