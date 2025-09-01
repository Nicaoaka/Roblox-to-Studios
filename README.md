# Roblox-to-Studios

Console-based tool for scraping Roblox Obby Creator part properties via screenshot+OCR to transfer obbies to Roblox Studios.

Built on Python 3.13.1 in Windows.

With this tool you can transfer parts at around 1 part per second. This isn't amazing, but it is way easier and faster than manually putting in part data. This program is made for transferring obbies made of basic parts shapes (Block, Ball, Cylinder, ...) with complex or varied positions, orientations, colors, etc that would be tedious to repeatedly copy and paste manually into Roblox Studios.

## Installation

### In Terminal
```bash
git clone https://github.com/Nicaoaka/Roblox-to-Studios.git
cd Roblox-to-Studios
pip install -r requirements.txt
```
Pytesseract is a wrapper of Google's Tesseract OCR. Go to [Tesseract Installation Page](https://tesseract-ocr.github.io/tessdoc/Installation.html) and download the latest one for your platform. Locate where the executable (.exe) file was downloaded to and set `TESSERACT_LOCATION` to the path in `config.py`.

### Config Setup
Run Obby Creator to see where the properties menu shows up and what appears within it.

In `config.py`, define the screenshot region with the __top-left__ and __bottom-right__ mouse positions of the 'Properties' panel. You can use `print_mouse_position()` to continuously print the mouse position in the terminal at a chosen interval.

<img src="Setup/annotated_whole.PNG" alt="Properties showing Top Left and Bottom Right points" height="400"/>

The Screenshotted region should look like this:

<img src="Setup/region_to_screenshot.PNG" alt="Expected Screenshot Region" height="275"/>


## Usage

### Set FLIP_AXIS

After loading an obby in Obby Creator, open `config.py` and set `FLIP_AXIS = True` if rotating downward on the red axis (toward the front) results in a positive angle change. Otherwise set it to `False`.

### Running the Program
Run `main.py` in terminal or through any code runner. Most interaction will occur through terminal/console.
```bash
python main.py
```

### Enter Commands

The main flow is `1`, `2`, `3`, `4`, `5`, and `q!`.

    [I]ndex -> [S]ave -> [Q]ueue -> [T]ransfer -> [D]elete -> Quit!

### Default Command Aliases
```
Index Mode                      [1/i]

Save Indexed                    [2/s/si]
Save Queue                      [sq]

Queue Indexed                   [3/q/qi]
Queue a Save file               [qs]
Queue Append Indexed            [qai]
Queue Append a Save file        [qas]

Transfer Mode                   [4/t]

Delete Indexed                  [5/d/di]
Delete New                      [dn]
Delete Queue                    [dq]

Reprint the Commands Menu       [h/help]
Clear Screen                    [cl/clear]
Quit                            [q!]

Cancel Action                   [<ctrl>+c]
```

* Delete clears the contents of the file, but does not remove it.
* Commands are case-insensitive.
* Ctrl+C cancels the current action and returns to the menu.
* Output is colorized using ANSI escape codes.

## Index

    *** Before indexing, make sure the obby can be reverted to how it currently is. ***

Within `config.py`, there are many options related to Index Mode. You will see them in the Index menu along with the keybinds.

### In Obby Creator

Going by default hotkeys, the general flow is clicking `f`, then deleting the part you were selecting, then going to the next part, then clicking `f`, and repeat [`f -> delete -> select -> f -> ...`].

For quality of life and to decrease error, you can enable `AUTO_DELETE` and `AUTO_RESELECT`, and change `ADD_PART_MIN_TIME` to the fastest your able to before the green Deleted Part(s) text blocks any data in properties.

### Default Index Mode Settings and Hotkeys

    REGION_TO_SCREENSHOT <Chosen Screen Region>

    FLIP_AXIS            <True or False>

    AUTO_DELETE          False
    AUTO_RESELECT        False
    ADD_PART_MIN_TIME    0.9 (seconds)
    
    PLAY_SOUNDS:         False

    Add a Part           [f]
    Pause                [c]
    Resume               [<ctrl>+e]
    Reprint Menu         [h]
    Exit                 [<ctrl>+c]

* If `HK_EXIT` is rebound to something else, `<ctrl>+c` will not leave Index Mode, only the chosen keybind will.
* Hotkeys are made with pynput, so keys can be concatenated with `+` and special keys are surrounded by `<>`. (eg `<alt>+x` and `<ctrl>`)

## Save

Leave Index Mode with `<ctrl>+c` or your custom keybind. This may error or crash, but this is fine, just run main.py again (Indexer adds to the files after each part, not at the end). In the console, enter `2` or `s` to save the parts you just indexed. Enter the filename as instructed, and you will see a file pop up in the `Saves` folder.

## Queue

Type `3` or `q` to immediately queue the indexed parts. You can also enter `qs` to queue from a save file. If your saves are in parts, use `qai` to append parts from index mode to queue and `qas` to append parts from a chosen save file to queue. Note, `qa` commands do not currently have duplicate detection.

## Transfer

Enter `4` or `t` to enter Transfer mode which runs a small API server to communicate with Roblox Studios. The server needs to be running at the time the script runs and can be exited/shutdown after the parts and folders appear in Studios.

### In Roblox Studios

Make a new place and copy the contents of `part_placer.lua` into a __Script__ object inside of `ServerScriptService`.

Activate the script by going into __Run__ mode within the Studios place, I don't recommend _Play_ or _Play Here_ since those have less mobility.

In the Studios explorer in `Workspace`, you will see 3 folders that were created. Copy them and then get out of Run mode. Leaving Run or either Play mode will cause all the parts to disappear (parts/folders generated by scripts are not persistent). Finally, paste the folders back into the `Workspace` with `Paste Into At Original Location` and you've transferred it.

### CHECK Folder

You'll see some parts missing or totally messed up. Most if not all of these will be inside of the CHECK folder. Each part will have one or more `Script` objects with error descriptions as names - one Script per property. These were originally made when parsing the image's text.

For example, `Position = HIGH '-9,68,1.608,21.516'`. The `HIGH` indicates too many arguments (too many commas). There is also `LOW` for fewer than expected. In general, Uncertainties follow this structure: `<Property> = '<Input>'`. If there is a tag like `HIGH` or `LOW` it is placed in front of the input.

## Deleting

After you've transferred an obby and want to move on to the next, you'll need to clear out the parts from index mode (`indexed.txt` and `new.txt`) and likely what you had queued (`queued.txt`). Entering `5` or `d` will empty out `indexed.txt` and `dq` will empty `queued.txt`.

## Reminders

* Keep a backup of your obby before indexing.
* You can cancel anytime with `<ctrl>+c`.
* Nothing is lost when the program unexpectedly raises an exception.
* Commands and hotkeys (among other things) can be changed in `config.py`.
* `Current/` holds active files, `Saves/` is for storage, `Debug/` contains error logs.
