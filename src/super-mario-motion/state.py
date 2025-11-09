class StateManager:
    # Init defualt values
    pose = "default"

    landmark_string = "default"

    opencv_image_webcam = None
    opencv_image_webcam_skeleton = None
    opencv_image_skeleton_only = None

    gui_checkbox_send_permission = False

    # Getter
    @classmethod
    def get_pose(cls):
        return cls.pose

    @classmethod
    def get_landmark_string(cls):
        return cls.landmark_string

    @classmethod
    def get_all_opencv_images(cls):
        return (cls.opencv_image_webcam,
                cls.opencv_image_webcam_skeleton,
                cls.opencv_image_skeleton_only)

    @classmethod
    def get_send_permission(cls):
        return cls.gui_checkbox_send_permission

    # Setter
    @classmethod
    def set_pose(cls, new_pose):
        cls.pose = new_pose

    @classmethod
    def set_landmark_string(cls, new_landmark_string):
        cls.landmark_string = new_landmark_string

    @classmethod
    def set_all_opencv_images(cls, new_webcam, new_webcam_skeleton, new_skeleton_only):
        cls.opencv_image_webcam = new_webcam
        cls.opencv_image_webcam_skeleton = new_webcam_skeleton
        cls.opencv_image_skeleton_only = new_skeleton_only

    @classmethod
    def set_send_permission(cls, new_send_permission):
        cls.gui_checkbox_send_permission = new_send_permission
