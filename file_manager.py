from pathlib import Path
import os
from config import *


def get_new_filename(directory: Path, ext: str = ".txt") -> Path:
    print(f'Files in {directory.name} directory: {os.listdir(directory)}')
    while True:
        name = input(f"Enter a filename: ").strip()

        if not name:
            print("Filename cannot be empty.")
            continue

        # ensure extension
        if not name.endswith(ext):
            name += ext

        path = directory / name

        if not path.exists():
            return path
        
        if confirm_Yn(f"File {path.name} already exists. Overwrite?"):
            return path
        
def get_existing_file_path(directory: Path) -> Path:
    filenames = os.listdir(directory)
    if not filenames:
        print(f'No files were found in {directory} directory')
    print(f'Files in {directory.name} directory: {os.listdir(directory)}')
    while True:
        name = input(f"Enter a filename: ").strip()
        if name in filenames:
            return directory / name
        print("Filename not found")

def empty_files(paths: Path|list[Path], auto_confirm: bool = False, confirm_if_at_least: int = 1000):
    """ if auto_confirm is True, confirm_threshold does not matter """
    if isinstance(paths, Path):
        paths = [paths]
    for p in paths:
        if not p.exists():
            print(f'{p.name} not found')
            continue
        if not auto_confirm:
            lines = p.read_text().count('\n')
            if lines >= confirm_if_at_least:
                if not confirm_Yn(f'{p.name} has {lines} lines. Delete anyway?'):
                    continue
        with p.open('w'): ...

def confirm_Yn(msg):
    choice = ''
    while choice not in ('Y', 'n'):
        choice = input(msg+" [Y/n]: ")
    return choice == 'Y'



def write_to_file(path: Path, directory: Path) -> None:
    save_path = get_new_filename(directory)
    data = path.read_text()

    with save_path.open("w", encoding="utf-8") as f:
        f.write(data)

def append(path: Path, dst: Path) -> None:
    if not dst.exists():
        print('Append dst path does not exist', dst)
        return
    with dst.open('a') as f:
        f.write(path.read_text())

def move_to_queue(path: Path, mode: str = 'w') -> None:
    if not path.exists():
        print(f'No file was found at {path}')
        return
    if os.path.getsize(QUEUED_PATH) > 0:
        if not confirm_Yn('The queue file is not empty. Overwrite?'):
            return
    with QUEUED_PATH.open(mode) as f:
        f.write(path.read_text())

