import os
import tkinter as tk
from tkinter.filedialog import askdirectory

root = tk.Tk()
root.withdraw()

file_path = askdirectory(title="select folder")

poppercommand = "python3 popper.py"

outputfile = "> popperoutput.txt"

os.system(poppercommand+" "+file_path+" "+outputfile)
