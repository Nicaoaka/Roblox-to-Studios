
def save():

    import os
    os.makedirs("saved_data", exist_ok=True)
    
    all_parts_file = "current/indexed_parts.txt"
    new_parts_file = "current/new.txt"
    selected_file = ""
    confirm = ""
    while confirm != "confirm":
        filename = input("Enter to save ('n' for new default all_parts/indexed_parts): ")
        selected_file = new_parts_file if 'n' == filename else all_parts_file
        print(f"File to save = {selected_file}")
        confirm = input("Type 'confirm': ")

    filename = ""
    confirm = ""
    while confirm != "confirm":
        filename = input("Enter Filename (optionally include filetype): ")
        print(f"Will be named:\n{filename}\nLocation: saved_data/{filename}")
        confirm = input("Type 'confirm': ")

    save = ""
    with open(selected_file, 'r') as f:
        save = f.read()

    with open("saved_data/"+filename, 'w') as f:
        f.write(save)

def main():
    save()

if __name__ == "__main__":
    main()