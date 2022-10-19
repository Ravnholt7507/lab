import os
import tkinter as tk
from tkinter.filedialog import askdirectory

root = tk.Tk()
root.withdraw()

file_path = askdirectory(title="select folder")

poppercommand = "python3 popper.py"

outputfile = ">> popperoutput.txt"


if file_path != '':
    with open('popperoutput.txt', 'w') as ofile:
        ofile.write('')

    for current_folder in os.listdir(file_path):
        f = os.path.join(file_path, current_folder)
        if current_folder == ".DS_Store":
            continue
        with open('popperoutput.txt', 'a') as ofile:
            ofile.write("ACTION:"+current_folder +'\n')

        os.system(poppercommand + " " + f + "/100" + " " + outputfile)
else:
    print("Error: Please select a folder")
