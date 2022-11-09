import os
import tkinter as tk
from tkinter.filedialog import askdirectory
import fileinput

root = tk.Tk()
root.withdraw()

file_path = askdirectory(title="select folder")
poppercommand = "python3 popper.py"
outputFile = ">> popper-output.txt"

f = open("popper-output.txt", "w")
f.write("")
f.close()

# print the popper output into a .txt file
if file_path != '':
    for current_folder in os.listdir(file_path):
        f = os.path.join(file_path, current_folder)
        if current_folder == ".DS_Store":
            continue

        os.system(poppercommand + " " + f + "/100" + " --timeout 10000" + " " + outputFile)
else:
    print("Error: Please select a folder")

#format popper-output.txt in order to fit fast-downward
get_head = []
with open("popper-output.txt", "r") as file :
    file_data = file.read()
    while not get_head.__contains__(")"):
        get_head = file.read(1)
file_data = file_data.replace("),", ");")
file_data = file_data.replace("_", ":")
file_data = file_data.replace(",E", "")

#change variables from A to ?A as that is what our planner expects in order to identify variables
refactor_variables = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "V", "W", "Y", "Q", "Z", "X"]
replaces = ["?A", "?B", "?C", "?D", "?E", "?F", "?G", "?H", "?I", "?J", "?K", "?L", "?M", "?N", "?O", "?P", "?Q", "?R", "?S", "?T", "?V", "?W", "?Y", "?Q", "?Z", "?X"]

i = 0
for letter in refactor_variables:
    file_data = file_data.replace(letter, replaces[i])
    i += 1




with open("popper-output.txt", "w") as file:
    file.write(file_data)





