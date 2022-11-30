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


def Remove_last_arg(line):
    head = line.split(":- ")
    head_args = head[0].split(",")
    last_arg = head_args[len(head_args)-1]
    last_arg = last_arg.replace(")", "")
    return last_arg

# print the popper output into a .txt file
if file_path != '':
    for current_folder in os.listdir(file_path):
        f = os.path.join(file_path, current_folder)
        if current_folder == ".DS_Store":
            continue

        os.system(poppercommand + " " + f + "/100" + " --timeout 10000" + " " + outputFile)
else:
    print("Error: Please select a folder")

# format popper-output.txt in order to fit fast-downward

with open("popper-output.txt", "r") as file :
    file_data = file.read()
file_data = file_data.replace("),", ");")
file_data = file_data.replace("l_", "l:")
file_data = file_data.replace("t_", "t:")
new_file_data = ""
for line in file_data.split("\n"):
          Last_arg = Remove_last_arg(line)
          line = line.replace(","+Last_arg, "")
          new_file_data += line + "\n"
file_data = new_file_data

i = 0
j = 0
head = []

while i < len(file_data):
    head.append(file_data[i])
    if head.__contains__(")"):
        break
    i += 1

variables = []
for char in head:
    if char.isupper():
        variables.append(char)

tmp_print = file_data.split(".")
print_to_file = []

for line in tmp_print:
    for char in line:
        if char.isupper() and not variables.__contains__(char) and line.count(char) == 1:
            line = line.replace(char, "_")

    print_to_file.append(line)

# change variables from A to ?A as that is what our planner expects in order to identify variables
refactor_variables = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S",
                      "T", "V", "W", "Y", "Q", "Z", "X"]
replaces = ["?A", "?B", "?C", "?D", "?E", "?F", "?G", "?H", "?I", "?J", "?K", "?L", "?M", "?N", "?O", "?P", "?Q", "?R",
            "?S", "?T", "?V", "?W", "?Y", "?Q", "?Z", "?X"]

i = 0
while i < len(refactor_variables):
    print_to_file = [line.replace(refactor_variables[i], replaces[i]) for line in print_to_file]
    i += 1

with open("popper-output.txt", "w") as file:
    for line in print_to_file:
        file.write(line)
