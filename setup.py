
import pprint       # print json / debug
import winsound     # built-in windows sounds
import threading    # async sounds

import pyautogui # region screenshot (GET image)
import pytesseract  # OCR (image -> Noisy text)
import text_parser  # Regex (Noisy text -> data)

from pynput import mouse, keyboard
keyboard_controller = keyboard.Controller()
mouse_controller = mouse.Controller()

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789,.-'
# pytesseract accepted chars: [\w,.-]


from config import * # Constants



print(
f"""{"\n" * 4}
-- Configuration --

Downward red axis rotation towards front
is +Positive: {RED_DOWN_TOWARDS_POSITIVE}
is -Negative: {not RED_DOWN_TOWARDS_POSITIVE}

Auto Delete Mode: {AUTO_DELETE}
Auto Select Mode: {AUTO_SELECT}

HOTKEYS:
Add part:   {ADD_PART}
EXIT:       {EXIT}
{"\n" * 4}""")
input("Press enter to continue")



# Load cache
# Set to prevent duplicates: contains hashes of previously loaded/queued parts
import time # timing cause curious
print("Loading indexed_parts.txt Cache")
start_time = time.time()
indexed_parts: set[str] = set()
with open("current/indexed_parts.txt", "r") as f:
    for line in f:
        indexed_parts.add(line)
starting_part_count = len(indexed_parts)
print(f"Loaded {starting_part_count} parts in {'{:.6f}'.format(time.time() - start_time)} seconds!")
del start_time

# clear previous session's temporary 'new' data
with open("current/new.txt", 'w') as f:
    f.write("")



def winBeep(frequency: int, duration: int):
    threading.Thread(target=winsound.Beep, args=(frequency, duration), daemon=False).start()

def good_notif(to_print, im=None):
    print(to_print)
    winBeep(700,450)
    if im: im.show()

def ok_notif(to_print, im=None):
    print(to_print)
    winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS | winsound.SND_ASYNC)
    if im: im.show()

def error_notif(to_print, im=None):
    print(to_print)
    winsound.PlaySound("SystemHand", winsound.SND_ALIAS | winsound.SND_ASYNC)
    if im: im.show()



def add_new_part():
    start_time = time.time()
    winBeep(500, 300)
    


    # get image of pre-defined region
    im = pyautogui.screenshot(region=REGION)



    # convert to text
    text_data: str = pytesseract.image_to_string(im, config=custom_config)
    if not text_data:
        error_notif("No text found", im)
        return True



    # parse data
    json_data = None
    try:
        json_data = text_parser.parse_image_text(text_data)
    # non match
    except ValueError as e:
        error_notif(f"{text_data}\nERROR: {e}", im)
        with open("testing_stuff/non_match.txt", 'a') as f:
            f.write(f"{repr(text_data)}\n")
        return True
    # unexpected
    except Exception as e:
        error_notif(f"{text_data}\nERROR: {e}", im)
        with open("testing_stuff/text_parser_errors.txt", 'a') as f:
            f.write(f"{repr(text_data)}\n")
        raise e



    # Obby Creator fixes
    json_data["Position"][0] *= -1
    if RED_DOWN_TOWARDS_POSITIVE:
        def rotate_180(n):
            return n - 180 if n > 0 else n + 180
        json_data["Orientation"][1] = rotate_180(json_data["Orientation"][1])
    new_part_delimited: str = text_parser.to_delimeted(json_data, DELIMITER)



    # check that it is actually new
    if new_part_delimited in indexed_parts:
        message = "\n-- That part was already added --\n" +\
            pprint.pformat(json_data, indent=4)
        ok_notif(message)
        return True # return False would end the hotkey listener
    


    # store / add to cache
    indexed_parts.add(new_part_delimited)
    with open("current/queued_parts.txt", 'a') as f:
        f.write(new_part_delimited)
    with open("current/indexed_parts.txt", 'a') as f:
        f.write(new_part_delimited)
    with open("current/new.txt", 'a') as f:
        f.write(new_part_delimited)



    # On-completion
    if AUTO_DELETE:
        keyboard_controller.tap(keyboard.Key.delete)
    if AUTO_SELECT:
        time.sleep(0.3)
        mouse_controller.click(mouse.Button.left)
        
    print(f"-- ADDED: PART #{len(indexed_parts)} in {time.time() - start_time} seconds --")



def exit_program():
    import sys
    winBeep(500,750)
    print("-- Exitted program --")
    print(f"Added {len(indexed_parts) - starting_part_count} parts this session.")
    sys.exit()



# add hotkeys
def run():
    with keyboard.GlobalHotKeys({
            ADD_PART: lambda: threading.Thread(target=add_new_part, daemon=True).start(),
            EXIT: exit_program,      # EXIT / end program
    }) as h:
        good_notif("-- SETUP READY --")
        h.join()

def main():
    run()

if __name__ == "__main__":
    main()
