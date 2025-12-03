import sys
import types
import pytest


@pytest.fixture(scope="session", autouse=True)
def mock_pyautogui():
    """
    In CI we mock pyautogui and mouseinfo completely,
    so importing super_mario_motion.input does not crash.
    """

    # fake pyautogui module
    fake = types.ModuleType("pyautogui")

    fake.keyDown = lambda *_: None
    fake.keyUp = lambda *_: None
    fake.press = lambda *_: None

    # register fake module BEFORE tests import code using pyautogui
    sys.modules["pyautogui"] = fake

    # mouseinfo is used internally by pyautogui → must also be faked
    sys.modules["mouseinfo"] = types.ModuleType("mouseinfo")
