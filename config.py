from collections import namedtuple

# --- Screen Regions ---
ScreenRegion = namedtuple("ScreenRegion", ["x", "y", "width", "height"])
FULL_SCREEN = ScreenRegion(1744, 361, 1930 - 1744, 878 - 361)
WINDOWED = ScreenRegion(1750, 361, 1940 - 1750, 856 - 361)





# --- Selection (FULL_SCREEN or WINDOWED) ---
REGION = FULL_SCREEN

# --- Hotkeys (Direct Variables) ---
ADD_PART = '<ctrl>+f'
EXIT = '<ctrl>+x'

# --- Axis Configuration ---
# \/ DOWNward RED rotation axis towards FRONT of obby is +POSITIVE
RED_DOWN_TOWARDS_POSITIVE = True

# --- Auto behaviors ---
AUTO_DELETE = True
AUTO_SELECT = AUTO_DELETE and True





# --- Delimiter ---
# Change DELIMITER in Roblox Studio as well !!!
# Must have *at least one* character that isn't in invalid chars
DELIMITER = ";"
INVALID_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-,[](){}"
if all(c in INVALID_CHARS for c in DELIMITER):
    raise ValueError(f"Invalid Delimiter: {DELIMITER}")

# --- Helper Function (Commented) ---
# def get_mouse_pos():
#     import pyautogui
#     import time
#     while True:
#         print(pyautogui.position())
#         time.sleep(1)
