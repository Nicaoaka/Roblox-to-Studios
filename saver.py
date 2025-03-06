
confirm = ""
while confirm != "confirm":
    filename = input("Enter Filename (.csv will be added): ")
    filename += ".csv"
    print(f"Will be named:\n{filename}")
    confirm = input("Type 'confirm': ")

save = ""
with open("indexed_parts.csv", 'r') as f:
    save = f.read()

with open(filename, 'w') as f:
    f.write(save)
