import sys
import types

# fake pyautogui for testing purposes, to avoid conflicts with actual
# pyautogui module in the ci
fake_pyautogui = types.ModuleType("pyautogui")
fake_pyautogui.keyDown = lambda *_: None
fake_pyautogui.keyUp = lambda *_: None
fake_pyautogui.press = lambda *_: None
fake_pyautogui.FAILSAFE = False

sys.modules["pyautogui"] = fake_pyautogui

# mouseinfo also required
fake_mouseinfo = types.ModuleType("mouseinfo")
sys.modules["mouseinfo"] = fake_mouseinfo
