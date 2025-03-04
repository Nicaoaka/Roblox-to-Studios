import pprint
import winsound
import threading
import text_parser
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789.-, '
# alphanumeric with , .-



# Load cache
# Set to prevent duplicates: contains hashes of previously loaded/queued parts
import time
print("Loading indexed_parts.csv Cache")
start_time = time.time()
indexed_parts: set[str] = set()
with open("indexed_parts.csv", "r") as f:
    for line in f:
        indexed_parts.add(line)
print(f"Loaded {len(indexed_parts)} parts in {'{:.6f}'.format(time.time() - start_time)} seconds!")
del start_time



import pyautogui
# while True:
#     print(pyautogui.position())
#     time.sleep(1)
# (top_left x, top_left y, width, height)
FULL_SCREEN = (1744, 392, 1930-1744, 837-392)
WINDOWED = (1750, 391, 1940-1750, 825-391)
REGION = FULL_SCREEN



def add_new_part():
    # get image of pre-defined region
    im = pyautogui.screenshot(region=REGION) # TODO
    print()

    # convert to text
    start_time = time.time()
    text_data: str = pytesseract.image_to_string(im, config=custom_config)
    if not text_data:
        winsound.PlaySound("SystemHand", winsound.SND_ALIAS | winsound.SND_ASYNC)
        im.show()
        print(text_data)
        return True
    print(f"OCR         {time.time() - start_time} seconds.")

    # parse data
    text_data += "\n" # if text_data doesn't end with a \n, there will be catastrophic backtracking (idk how to fix)
    try:
        new_part_csv: str = text_parser.parse_oc_image_text(text_data, for_csv=True)
    except Exception as e:
        winsound.PlaySound("SystemHand", winsound.SND_ALIAS | winsound.SND_ASYNC)
        im.show()
        print(text_data)
        print(f"ERROR: {e}")
        return True


    # check that it is actually new
    if new_part_csv in indexed_parts:
        winsound.PlaySound("SystemExclamation", winsound.SND_ALIAS | winsound.SND_ASYNC)
        print("That part was already added")
        pprint.pprint(text_parser.parse_oc_image_text(text_data, for_csv=False), indent=4)
        return True # return False would end the hotkey listener
    
    threading.Thread(target=winsound.Beep, args=(400, 500)).start()
    indexed_parts.add(new_part_csv)
    print(f"ADDED: PART #{len(indexed_parts)}")

    # store to files for future runs
    with open("queued_parts.csv", 'a') as f:
        f.write(new_part_csv)
    with open("indexed_parts.csv", 'a') as f:
        f.write(new_part_csv)


from pynput import keyboard

# add hotkeys
with keyboard.GlobalHotKeys({
        '<ctrl>+c': False,      # end program
        '<ctrl>+f': add_new_part,
    }) as h:
    h.join()










    # # Use Snip-It (Put in add_new_part())
    # image_dib = ImageGrab.grabclipboard()
    # im = convertImageFormat(image_dib, 'PNG')

# ONLY necessary for manual snip-it / clipboard image conversion (MOVE TO TOP)
# from PIL import ImageGrab, Image
# import io
# def convertImageFormat(imgObj, outputFormat="PNG"):
#     # function by ScottC - https://stackoverflow.com/a/74541605
#     newImgObj = imgObj
#     if outputFormat and (imgObj.format != outputFormat):
#         imageBytesIO = io.BytesIO()
#         imgObj.save(imageBytesIO, outputFormat)
#         newImgObj = Image.open(imageBytesIO)
#     return newImgObj
