class StateManager:
    # Init defualt values
    pose = "default"
    landmark_string = "default"

    opencv_image_webcam = None
    opencv_image_webcam_skeleton = None
    opencv_image_skeleton_only = None

    # Getter
    def get_pose(self):
        return StateManager.pose

    def get_landmark_string(self):
        return StateManager.landmark_string

    def get_all_opencv_images(self):
        return (StateManager.opencv_image_webcam,
                StateManager.opencv_image_webcam_skeleton,
                StateManager.opencv_image_skeleton_only)

    # Setter
    def set_pose(self, new_pose):
        StateManager.pose = new_pose

    def set_landmark_string(self, new_landmark_string):
        StateManager.landmark_string = new_landmark_string

    def set_all_opencv_images(self, new_webcam, new_webcam_skeleton, new_skeleton_only):
        StateManager.opencv_image_webcam = new_webcam
        StateManager.opencv_image_webcam_skeleton = new_webcam_skeleton
        StateManager.opencv_image_skeleton_only = new_skeleton_only

