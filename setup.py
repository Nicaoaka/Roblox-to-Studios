import pprint       # debug
import winsound     # built-in windows sounds
import threading    # async sounds

import text_parser  # Regex (Noisy text -> data)
import pytesseract  # OCR (image -> Noisy text)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-, '
# pytesseract accepted chars: alphanumeric with , .-



# BEFORE USING THIS TOOL:
# Fix bool cast make it input().lower() == "true"
RED_DOWN_TOWARDS_POSITIVE: bool = input("DOWNward RED axis rotation towards FRONT of obby +POSITIVE: ").lower() == "true"
print("Set to:", RED_DOWN_TOWARDS_POSITIVE)

AUTO_DELETE = input("Use AutoDelete: ").lower() == "true"
print("Set to:", AUTO_DELETE)

# Hotkeys
ADD_PART = 'f'
SAVE_TO_SEPARATE_FILE = '<ctrl>+v'
END_PROGRAM = '<ctrl>+c'

DELIMITER: str = ";"
if all([c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.- ,[](){}" for c in DELIMITER]):
    raise ValueError("Invalid Delimiter")

print(
f"""
Hotkeys:
add part:       {ADD_PART}
save to file:   {SAVE_TO_SEPARATE_FILE}
END:            {END_PROGRAM}
"""
)

confirm = ""
while confirm != "confirm":
    confirm = input("Type 'confirm' to confirm: ")



# Load cache
# Set to prevent duplicates: contains hashes of previously loaded/queued parts
import time # timing cause curious
print("Loading indexed_parts.txt Cache")
start_time = time.time()
indexed_parts: set[str] = set()
with open("current/indexed_parts.txt", "r") as f:
    for line in f:
        print(repr(line))
        indexed_parts.add(line)
print(f"Loaded {len(indexed_parts)} parts in {'{:.6f}'.format(time.time() - start_time)} seconds!")
del start_time



import pyautogui # region screenshot
# while True:
#     print(pyautogui.position())
#     time.sleep(1)
# (top_left x, top_left y, width, height)
FULL_SCREEN = (1744, 361, 1930-1744, 878-361)
WINDOWED = (1750, 361, 1940-1750, 856-361)
REGION = FULL_SCREEN

def good_result(to_print, im=None):
    print(to_print)
    threading.Thread(target=winsound.Beep, args=(400, 500)).start()
    if im: im.show()

def soft_error(to_print, im=None):
    print(to_print)
    winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS | winsound.SND_ASYNC)
    if im: im.show()

def critical_error(to_print, im=None):
    print(to_print)
    winsound.PlaySound("SystemHand", winsound.SND_ALIAS | winsound.SND_ASYNC)
    if im: im.show()



def add_new_part():
    start_time = time.time()



    # get image of pre-defined region
    im = pyautogui.screenshot(region=REGION)



    # convert to text
    text_data: str = pytesseract.image_to_string(im, config=custom_config)
    if not text_data:
        critical_error("No text found", im)
        return True



    # parse data
    json, uncertainties = None, None
    try:
        json, uncertainties = text_parser.parse_image_text(text_data)
    # non match
    except ValueError as e:
        critical_error(f"{text_data}\nERROR: {e}", im)
        with open("testing_stuff/errors.txt", 'a') as f:
            f.write("START"+text_data+"END\n\n")
        return True
    # unexpected
    except Exception as e:
        critical_error(f"{text_data}\nERROR: {e}", im)
        with open("testing_stuff/errors.txt", 'a') as f:
            f.write("START"+text_data+"END\n\n")
        raise e



    # Obby Creator fixes
    json["Position"][0] *= -1
    if RED_DOWN_TOWARDS_POSITIVE:
        def rotate_180(n):
            return n - 180 if n > 0 else n + 180
        json["Orientation"][1] = rotate_180(json["Orientation"][1])
    new_part_delimited: str = text_parser.to_delimeted(json, uncertainties, DELIMITER)



    # check that it is actually new
    if new_part_delimited in indexed_parts:
        message = "\n-- That part was already added --\n" +\
            pprint.pformat(json, indent=4) + "\n" +\
            pprint.pformat(uncertainties, indent=4)
        soft_error(message)
        return True # return False would end the hotkey listener
    


    # store / add to cache
    indexed_parts.add(new_part_delimited)
    with open("current/queued_parts.txt", 'a') as f:
        f.write(new_part_delimited)
    with open("current/indexed_parts.txt", 'a') as f:
        f.write(new_part_delimited)

    if AUTO_DELETE:
        pyautogui.press('delete')
        
    good_result(f"-- ADDED: PART #{len(indexed_parts)} in {time.time() - start_time} seconds --")



def save_to_file():
    
    confirm = ""
    while confirm != "confirm":
        filename = input("Enter Filename (optionally include filetype): ")
        print(f"Will be named:\n{filename}")
        confirm = input("Type 'confirm': ")

    save = ""
    with open("current/indexed_parts.txt", 'r') as f:
        save = f.read()

    with open("saved_data/"+filename, 'w') as f:
        f.write(save)



from pynput import keyboard

# add hotkeys
def run():
    with keyboard.GlobalHotKeys({
            ADD_PART: add_new_part,
            SAVE_TO_SEPARATE_FILE: save_to_file,
            END_PROGRAM: False,      # EXIT / end program
        }) as h:
        good_result("-- SETUP READY --")
        h.join()

def main():
    run()

if __name__ == "__main__":
    main()
