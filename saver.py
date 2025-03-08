
def save():
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

def main():
    save()

if __name__ == "__main__":
    main()