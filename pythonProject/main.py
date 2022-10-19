import os
import tkinter as tk
from tkinter.filedialog import askdirectory

root = tk.Tk()
root.withdraw()

file_path = askdirectory(title="select folder")

poppercommand = "python3 popper.py -q"

outputfile = ">> popperoutput.txt"

for foldername in os.listdir(file_path):
        f = os.path.join(file_path, foldername)
        if foldername ==".DS_Store":
                continue

        os.system(poppercommand + " " + f + "/100" + " " + outputfile)
