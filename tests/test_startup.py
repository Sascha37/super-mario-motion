"""
Test function for checking the availability of a webcam in the main module.

This function patches several modules and attributes to simulate their
behavior during testing.
It imports the according function from the corresponding module and
asserts that
the method is callable or has attributes.
More specifically, it uses monkeypatch to mock certain attributes
so that they can be called or accessed without raising an exception.
This is useful for testing modules that depend on external libraries or
resources.
"""

from super_mario_motion import collect, game_launcher, gamepad_visualizer, \
    gui, input as smm_input, main, vision, vision_ml


def test_main(monkeypatch):
    monkeypatch.setattr("cv2.VideoCapture", lambda *_: None)
    monkeypatch.setattr("tkinter.Tk", lambda *_: None)
    monkeypatch.setattr("pyautogui.keyDown", lambda *_: None)
    monkeypatch.setattr("pyautogui.keyUp", lambda *_: None)

    assert hasattr(main, "webcam_is_available")


def test_collect(monkeypatch):
    monkeypatch.setattr("cv2.VideoCapture", lambda *_: None)
    monkeypatch.setattr("time.sleep", lambda *_: None)

    assert hasattr(collect, "main")


def test_game_launcher(monkeypatch):
    monkeypatch.setattr("subprocess.Popen", lambda *_: None)
    monkeypatch.setattr("webbrowser.open", lambda *_: None)

    assert callable(game_launcher.launch_game)


def test_input(monkeypatch):
    class DummyThread:
        def __init__(self, *a, **k): pass

        def start(self): pass

    monkeypatch.setattr("threading.Thread", DummyThread)
    monkeypatch.setattr("pyautogui.keyDown", lambda *_: None)
    monkeypatch.setattr("pyautogui.keyUp", lambda *_: None)

    assert hasattr(smm_input, "init")


def test_gui(monkeypatch):
    monkeypatch.setattr("tkinter.Tk", lambda *_: None)

    assert hasattr(gui, "init")


def test_gamepad_visualizer(monkeypatch):
    monkeypatch.setattr("PIL.Image.open", lambda *_: None)

    assert hasattr(gamepad_visualizer, "get_base_image")
    assert hasattr(gamepad_visualizer, "pose_to_buttons")
    assert hasattr(gamepad_visualizer, "draw_highlight_overlay")
    assert hasattr(gamepad_visualizer, "create_gamepad_image")


def test_user_data(monkeypatch, tmp_path):
    monkeypatch.setattr("os.path.expanduser", lambda *_: str(tmp_path))
    monkeypatch.setattr("platform.system", lambda: "Linux")

    from super_mario_motion import user_data
    user_data.init()

    assert (tmp_path / "config" / "config.json").exists()


def test_vision(monkeypatch):
    monkeypatch.setattr("cv2.VideoCapture", lambda *_: None)

    assert hasattr(vision, "init")


def test_vision_ml(monkeypatch):
    monkeypatch.setattr("mediapipe.solutions.pose.Pose", lambda *_: None)
    monkeypatch.setattr("time.sleep", lambda *_: None)

    assert hasattr(vision_ml, "init")
