import os
import tkinter as tk
from tkinter.filedialog import askdirectory

root = tk.Tk()
root.withdraw()

file_path = askdirectory(title="select folder")
poppercommand = "python3 popper.py"
messyOutputFile = ">> popper-messy-output.txt"

f = open("popper-output.txt", "w")
f.write("")
f.close()

# print the popper output into a .txt file, the file will me cleaned later
if file_path != '':
    for current_folder in os.listdir(file_path):
        f = os.path.join(file_path, current_folder)
        if current_folder == ".DS_Store":
            continue

        os.system(poppercommand + " " + f + "/100" + " --timeout 10000" + " " + messyOutputFile)
else:
    print("Error: Please select a folder")

# We now want to clean the messy output file in order to get rid of no solutions
deleteWord = "NO SOLUTION"

with open("popper-messy-output.txt") as inputFile, open("popper-output.txt", "w+") as outputFile:
    for line in inputFile:
        if not line.__contains__(deleteWord):
            outputFile.write(line)

os.remove("popper-messy-output.txt")
