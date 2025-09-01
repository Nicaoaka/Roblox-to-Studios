'''
main.py

Unified entry point for OC to Studios.
Choose what to do from the menu, then interact via hotkeys/terminal.
'''

import os
import time
import traceback

import indexer              # OCR/indexing logic
import file_manager         # copy/move files between Active / Saves / Queue
import HTTP_handler         # FastAPI server
from config import *


# --- ANSI Colors ---
RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[92m"
CYAN = "\033[96m"
YELLOW = "\033[93m"
RED = "\033[91m"

# --- Menu Text ---
MENU_TEXT = f"""
{ GREEN}=== OC to Studios ==={RESET}

{ RESET}Index Mode                   {RESET}[{CYAN}{f'{RESET}/{CYAN}'.join(COMMAND_ALIASES['index'])}{RESET}]

{ RESET}Save Indexed to file         {RESET}[{CYAN}{f'{RESET}/{CYAN}'.join(COMMAND_ALIASES['save_idx'])}{RESET}]
{ RESET}Save Queue to file           {RESET}[{CYAN}{f'{RESET}/{CYAN}'.join(COMMAND_ALIASES['save_queue'])}{RESET}]

{ RESET}Queue Indexed                {RESET}[{CYAN}{f'{RESET}/{CYAN}'.join(COMMAND_ALIASES['queue_idx'])}{RESET}]
{ RESET}Queue a Saved file           {RESET}[{CYAN}{f'{RESET}/{CYAN}'.join(COMMAND_ALIASES['queue_saved'])}{RESET}]
{ RESET}Append Indexed to Queue      {RESET}[{CYAN}{f'{RESET}/{CYAN}'.join(COMMAND_ALIASES['queue_append_idx'])}{RESET}]
{ RESET}Append Saved file to Queue   {RESET}[{CYAN}{f'{RESET}/{CYAN}'.join(COMMAND_ALIASES['queue_append_saved'])}{RESET}]

{ RESET}Transfer Mode (API server)   {RESET}[{CYAN}{f'{RESET}/{CYAN}'.join(COMMAND_ALIASES['transfer'])}{RESET}]

{   RED}Delete Indexed               {RESET}[{RED}{f'{RESET}/{RED}'.join(COMMAND_ALIASES['delete_idx'])}{RESET}]
{   RED}Delete New                   {RESET}[{RED}{f'{RESET}/{RED}'.join(COMMAND_ALIASES['delete_new'])}{RESET}]
{   RED}Delete Queue                 {RESET}[{RED}{f'{RESET}/{RED}'.join(COMMAND_ALIASES['delete_queue'])}{RESET}]

{YELLOW}Reprint this Menu            {RESET}[{YELLOW}{f'{RESET}/{YELLOW}'.join(COMMAND_ALIASES['help'])}{RESET}]
{YELLOW}Clear Screen                 {RESET}[{YELLOW}{f'{RESET}/{YELLOW}'.join(COMMAND_ALIASES['clear'])}{RESET}]
{YELLOW}Quit                         {RESET}[{YELLOW}{f'{RESET}/{YELLOW}'.join(COMMAND_ALIASES['quit'])}{RESET}]

{YELLOW}Cancel Action                {RESET}[{YELLOW}<ctrl>+c{RESET}]
{ RESET}Note: If the program crashes no data will be lost.
"""


def main():
    '''
    Top-level interactive menu loop.
    User chooses what action to run; Ctrl+C always returns to this menu.
    '''

    # create one Indexer instance per session
    Indexer = indexer.PartIndexer()

    # make required directories if missing
    ACTIVE_DIR.mkdir(exist_ok=True)
    SAVES_DIR.mkdir(exist_ok=True)
    DEBUG_DIR.mkdir(exist_ok=True)
    has_quit = False

    while not has_quit:

        print(MENU_TEXT)
        while True:
            try:
                choice = input(':').strip().lower()

                # --- Indexing ---
                if choice in COMMAND_ALIASES["index"]:
                    Indexer.start_session()
                    print("(BUG: next command may be cancelled so just press enter, sorry)")

                # --- Saving ---
                elif choice in COMMAND_ALIASES["save_idx"]:
                    file_manager.write_to_file(INDEXED_PARTS_PATH, SAVES_DIR)

                elif choice in COMMAND_ALIASES["save_queue"]:
                    file_manager.write_to_file(QUEUED_PATH, SAVES_DIR)

                # --- Queue ---
                elif choice in COMMAND_ALIASES["queue_idx"]:
                    file_manager.move_to_queue(INDEXED_PARTS_PATH)

                elif choice in COMMAND_ALIASES["queue_saved"]:
                    file_manager.move_to_queue(file_manager.get_existing_file_path(SAVES_DIR))

                elif choice in COMMAND_ALIASES["queue_append_idx"]:
                    file_manager.append(INDEXED_PARTS_PATH, QUEUED_PATH)

                elif choice in COMMAND_ALIASES["queue_append_saved"]:
                    file_manager.append(file_manager.get_existing_file_path(SAVES_DIR), QUEUED_PATH)

                # --- Transfer ---
                elif choice in COMMAND_ALIASES["transfer"]:
                    HTTP_handler.start_dev_server()

                # --- Delete ---
                elif choice in COMMAND_ALIASES["delete_idx"]:
                    file_manager.empty_files(INDEXED_PARTS_PATH, confirm_if_at_least=1)

                elif choice in COMMAND_ALIASES["delete_new"]:
                    file_manager.empty_files(NEW_PARTS_PATH, auto_confirm=True)

                elif choice in COMMAND_ALIASES["delete_queue"]:
                    file_manager.empty_files(QUEUED_PATH, confirm_if_at_least=500)

                # --- Utility ---
                elif choice in COMMAND_ALIASES["help"]:
                    break

                elif choice in COMMAND_ALIASES["clear"]:
                    os.system('cls' if os.name == 'nt' else 'clear')

                # --- Exit ---
                elif choice in COMMAND_ALIASES["quit"]:
                    print('Exitted program. Goodbye user.')
                    has_quit = True
                    break

                else:
                    print(f'\033[A\33[{len(choice)}C\t{RED}Unknown Command{RESET}')

            except KeyboardInterrupt:
                print(f'{YELLOW}\tCanceled{RESET}')
            except Exception as e:
                print(f'{RED}An error occurred: {e}\n{traceback.format_exception(e)}{RESET}')


if __name__ == '__main__':
    main()