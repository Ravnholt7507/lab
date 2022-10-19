import os
import tkinter as tk
from tkinter.filedialog import askdirectory

root = tk.Tk()
root.withdraw()

file_path = askdirectory(title="select folder")

poppercommand = "python3 popper.py"

outputfile = ">> popperoutput.txt"

with open('popperoutput.txt', 'w') as ofile:
        ofile.write('')

for foldername in os.listdir(file_path):
        f = os.path.join(file_path, foldername)
        if foldername ==".DS_Store":
                continue
        with open('popperoutput.txt', 'a') as ofile:
                ofile.write(foldername+":")
                ofile.write('\n')

        os.system(poppercommand + " " + f + "/100" + " " + outputfile)
