"""
Configuration for OC to Studios

Adjust these settings to match your monitor, hotkeys, and Studio setup.
"""
from collections import namedtuple
from pathlib import Path

# --- Utilities ---
ScreenRegion = namedtuple('ScreenRegion', ['x', 'y', 'width', 'height'])
def get_region(top_left: tuple[int, int], bottom_right: tuple[int, int]) -> ScreenRegion:
    return ScreenRegion(top_left[0], top_left[1], bottom_right[0] - top_left[0], bottom_right[1] - top_left[1])

def print_mouse_position(interval: float = 1.0) -> None:
    """
    Continuously prints the mouse position every `interval` seconds.
    Useful for calibrating screen regions.
    """
    import pyautogui
    import time

    print('Press Ctrl+C to stop.')
    try:
        while True:
            print(pyautogui.position())
            time.sleep(interval)
    except KeyboardInterrupt:
        print('Stopped mouse position logging.')


# --- Tesseract.exe Location --- 
TESSERACT_LOCATION = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


# --- Main Commands ---
COMMAND_ALIASES = {
    'index': ['1', 'i'],

    'save_idx': ['2', 's', 'si'],
    'save_queue': ['sq',],

    'queue_idx': ['3', 'q', 'qi'],
    'queue_saved': ['qs',],
    'queue_append_idx': ['qai',],
    'queue_append_saved': ['qas',],

    'transfer': ['4', 't'],

    'delete_idx': ['5', 'd', 'di'],
    'delete_new': ['dn',],
    'delete_queue': ['dq',],

    'help': ['h', 'help'],
    'clear': ['cl', 'clear'],
    'quit': ['q!'],
}



# --- Screenshot Regions ---
# These likely have to be updated per monitor.
# This is my setup, but you can add or just have one.
IN_FULL_SCREEN = get_region(
    top_left=     (1744, 361),
    bottom_right= (1905, 878))
IN_WINDOWED = get_region(
    top_left=     (1750, 361),
    bottom_right= (1905, 856))
REGION_TO_SCREENSHOT = IN_FULL_SCREEN
# use print_mouse_position(interval=1), then run this file to get mouse positions
# see what should be within those regions in Setup/


# --- Axis Configuration ---
# Set to True if global rotation of a part downward towards the front using the red axis
# causes a positive angle change.
# This can be fixed in studios, but it is best to get it correct.
FLIP_AXIS = True


# --- Auto Behaviors in Index Mode ---
# These only activate if a part is successfully saved.
#    (do not activate on duplicate or error)
AUTO_DELETE = False     # Press delete after saving a part
AUTO_RESELECT = False   # Press left click after saving a part
ADD_PART_MIN_TIME = 0.9 # Don't let another part be added until this many seconds have passed
    # useful to stay at fixed intervals


# --- Play Sounds in Index Mode ---
PLAY_SOUNDS = True


# --- Hotkeys (pynput) ---
HK_ADD_PART = 'f'
HK_PAUSE = 'c'
HK_RESUME = '<ctrl>+e' # use an uncommon combo/key
HK_HELP = 'h'
HK_EXIT = '<ctrl>+c'   # only hotkey that will exit index session
    # (ctrl+c is not picked up unless that is the selected hotkey)




# =========================
#     Advanced settings
# =========================

# --- Delimiter ---
#   - Change DELIMITER in Roblox Studio as well!
#   - Must include at least one character not in INVALID_CHARS.
DELIMITER = ';'
INVALID_CHARS = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-,[](){}'
if all(c in INVALID_CHARS for c in DELIMITER):
    raise ValueError(f'Invalid Delimiter: {DELIMITER}')

# --- File System ---
ACTIVE_DIR = Path('Active')
NEW_PARTS_PATH = ACTIVE_DIR / 'new.txt'
INDEXED_PARTS_PATH = ACTIVE_DIR / 'indexed.txt'
QUEUED_PATH = ACTIVE_DIR / 'queued.txt'

SAVES_DIR = Path('Saves')

DEBUG_DIR = Path('_debug')
REGEX_ERR_FILE = DEBUG_DIR / 'regex_no_match.txt'
PARSER_ERR_PATH = DEBUG_DIR / 'parser_raised_exception.txt'







# Do not change these.
__region_var_name = [name for name, v in locals().items() if v == REGION_TO_SCREENSHOT and name != 'REGION'][0]
__all__ = [
    'TESSERACT_LOCATION',

    'COMMAND_ALIASES',

    'REGION_TO_SCREENSHOT',
    'FLIP_AXIS',
    'AUTO_DELETE', 'AUTO_RESELECT', 'ADD_PART_MIN_TIME',
    'PLAY_SOUNDS',
    'HK_ADD_PART', 'HK_PAUSE', 'HK_RESUME', 'HK_HELP', 'HK_EXIT',
    
    'DELIMITER',

    'ACTIVE_DIR', 'NEW_PARTS_PATH', 'INDEXED_PARTS_PATH', 'QUEUED_PATH',
    'SAVES_DIR',
    'DEBUG_DIR', 'REGEX_ERR_FILE', 'PARSER_ERR_PATH',
    
    '__region_var_name',
]
