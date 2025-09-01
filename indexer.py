import pprint
import winsound     # play simple audio
import threading    # mainly for audio
import time
import traceback    # better error printing

import pyautogui    # Screenshots
import pytesseract  # OCR (image -> text)
from pynput import mouse, keyboard  # Hotkeys & input control

# Input controllers (used for auto-delete & auto-select)
keyboard_controller = keyboard.Controller()
mouse_controller = mouse.Controller()

from config import * # Constants
import text_parser  # Regex (Noisy text -> data)

# Tesseract OCR setup
pytesseract.pytesseract.tesseract_cmd = TESSERACT_LOCATION
custom_config = (
    r'--oem 3 --psm 6 '
    r'-c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,.-' # regex equiv: [\w,.-]
)



# --- ANSI Colors ---
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"

INDEX_MENU = f"""
{GREEN}========================================{RESET}

        {BOLD}-- Configurations --{RESET}

Screenshot Region: {YELLOW}{__region_var_name}{RESET}

{CYAN}HOTKEYS{RESET}
Add part:   {HK_ADD_PART}
Pause:      {HK_PAUSE}
Resume:     {HK_RESUME}
Exit:       {HK_EXIT}

Downward red axis rotation towards front
is +Positive: {YELLOW}{FLIP_AXIS}{RESET}
is -Negative: {YELLOW}{not FLIP_AXIS}{RESET}

Auto Delete Mode: {YELLOW}{AUTO_DELETE}{RESET}
Auto Select Mode: {YELLOW}{AUTO_RESELECT}{RESET}

Play Audio: {PLAY_SOUNDS}

{GREEN}========================================{RESET}
"""


def win_beep(frequency: int, duration_ms: int) -> None:
    """Play a simple beep sound in a background thread."""
    if not PLAY_SOUNDS:
        return
    threading.Thread(
        target=winsound.Beep,
        args=(frequency, duration_ms),
        daemon=False,
    ).start()


def notify_success(message: str, img=None) -> None:
    """Success feedback: high-pitched beep + console print."""
    print(f'{GREEN}{message}{RESET}')
    win_beep(700, 450)
    if img:
        img.show()


def notify_duplicate(message: str, img=None) -> None:
    """Duplicate feedback: Windows exclamation sound + console print."""
    print(f'{YELLOW}{message}{RESET}')
    if not PLAY_SOUNDS:
        return
    winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS | winsound.SND_ASYNC)
    if img:
        img.show()


def notify_error(message: str, img=None) -> None:
    """Error feedback: Windows error sound + console print."""
    print(f'{RED}{message}{RESET}')
    if not PLAY_SOUNDS:
        return
    winsound.PlaySound("SystemHand", winsound.SND_ALIAS | winsound.SND_ASYNC)
    if img:
        img.show()



class PartIndexer:

    def __init__(self) -> None:
        self.indexed_parts: set[str] = set()
        self.starting_part_count: int = 0
        self._paused: bool = False
        self.last_part_added = 0
    

    def add_new_part(self):
        """
        Capture the screen region, OCR → structured part data,
        and save it to file if new.

        Returns:
            True (to keep hotkey listener alive).
        """
        if self._paused:
            print(f'Paused: Press {HK_RESUME} to resume.')
            return
        
        if self.last_part_added + ADD_PART_MIN_TIME > time.time():
            print(f'Can add next part in {round(self.last_part_added + ADD_PART_MIN_TIME - time.time(),3)} seconds')
            return
        start_time = time.time()
        self.last_part_added = start_time
        win_beep(500, 300)
        
        # Screenshot pre-defined region
        img = pyautogui.screenshot(region=REGION_TO_SCREENSHOT)

        # Use an OCR (Optical Character Recognition)
        text_data: str = pytesseract.image_to_string(img, config=custom_config)
        if not text_data:
            notify_error("No text found", img)
            return

        try:
            json_data = text_parser.parse_image_text(text_data)
        except ValueError as e:
            notify_error(f"{text_data}\nREGEX ERROR: {e}", img)
            with REGEX_ERR_FILE.open('a') as f:
                f.write(f"{repr(text_data)}\n")
            return
        # any unhandled error during parsing
        except Exception as e:
            notify_error(f"{text_data}\nPARSER ERROR: {e}\n{traceback.format_exception(e)}", img)
            with PARSER_ERR_PATH.open('a') as f:
                f.write(f"{repr(text_data)}\n")
            return

        # Obby Creator fixes
        json_data["Position"][0] *= -1 # type: ignore - Position data will be int|float
        if FLIP_AXIS:
            def rotate_180(n):
                return n - 180 if n > 0 else n + 180
            json_data["Orientation"][1] = rotate_180(json_data["Orientation"][1]) # type: ignore - Orientation data will be int|float
        
        new_part_delimited: str = text_parser.to_delimeted(json_data, DELIMITER)

        # duplicate check
        if new_part_delimited in self.indexed_parts:
            message = "\n--  -  -- --- ----- --- --  -  --\n" +\
                pprint.pformat(json_data, indent=4) +\
                "\n-- That part was already added --\n"
            notify_duplicate(message)
            return
        
        # save and update cache
        self.indexed_parts.add(new_part_delimited)
        for file in [INDEXED_PARTS_PATH, NEW_PARTS_PATH]:
            with file.open('a') as f:
                f.write(new_part_delimited)

        # What to do after saving a part
        if AUTO_DELETE:
            keyboard_controller.tap(keyboard.Key.delete)
        if AUTO_RESELECT:
            time.sleep(0.3)
            mouse_controller.click(mouse.Button.left)
            
        notify_success(f"-- ADDED: PART #{len(self.indexed_parts)} in {time.time() - start_time:.3f} seconds --")


    def pause(self):
        if not self._paused:
            print(f"-- Indexing Paused -- Press {HK_RESUME} to resume")
            self._paused = True

    def resume(self):
        if self._paused:
            print(f"-- Indexing Resumed -- Press {HK_PAUSE} to pause")
            self._paused = False


    def join_hotkeys(self):

        def exit_program():
            hotkeys.stop()
            win_beep(500, 750)
            print("-- Exitted program --")
            print(f"Added {len(self.indexed_parts) - self.starting_part_count} parts this session.")

        hotkeys = keyboard.GlobalHotKeys({
            HK_ADD_PART: lambda: threading.Thread(target=self.add_new_part, daemon=True).start(),
            HK_PAUSE: self.pause,
            HK_RESUME: self.resume,
            HK_HELP: lambda: print(INDEX_MENU),
            HK_EXIT: exit_program,
        })
        hotkeys.start()
        hotkeys.join()


    def real_init(self, is_new_session: bool = True):

        # Load cache
        # Set to prevent duplicates: contains hashes of previously loaded/queued parts
        print("Loading indexed_parts.txt Cache . . .")
        start_time = time.time()

        if INDEXED_PARTS_PATH.exists():
            self.indexed_parts = {line for line in INDEXED_PARTS_PATH.read_text().splitlines()}
        
        if is_new_session:
            self.starting_part_count = len(self.indexed_parts)
            with NEW_PARTS_PATH.open('w'):
                ...
        print(f"Loaded {len(self.indexed_parts)} parts in {'{:.6f}'.format(time.time() - start_time)} seconds!")

    def start_session(self, is_new_session: bool = True):
        self.real_init(is_new_session)
        notify_success("-- SETUP READY --")
        print(INDEX_MENU)
        try:
            self.join_hotkeys()
        except KeyboardInterrupt:
            ...
        self._paused = False


def main():
    pi = PartIndexer()
    pi.start_session()

if __name__ == "__main__":
    main()
