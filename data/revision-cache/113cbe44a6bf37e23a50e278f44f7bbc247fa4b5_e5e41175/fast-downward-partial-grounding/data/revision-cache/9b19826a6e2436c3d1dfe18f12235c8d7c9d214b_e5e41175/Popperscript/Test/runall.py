import os
import time
import pathlib
import sys
import math

args = sys.argv
args.pop(0)

#--max-examples (default: 10000)
#--max-vars (default: 6)
#--max-body (default: 6)
#--max-literals (default: 40)
#allow_singletons. to your bias file.
#--eval-timeout (default: 0.001 seconds)
#--quiet (default: False)
#--debug (default: false)
#--stats (default: false)

#file_path =  '/Users/minmacbook/Documents/Popper-main/domainfiles/depots'
file_path =  '/Users/minmacbook/Documents/Popper-main/domainfiles/blocksworld'
#file_path =  '/home/rune/Desktop/domainfiles/caldera'

poppercommand = "python3 popper.py -q"

outputfile = ">> output.txt"

currentLine = 0

directories = []

num_lines = [[],[]]

percent = False
percent_amount = 1

def func(percent):
    os.walk(file_path)

    for subfolders in os.listdir(file_path):
        path = file_path+'/'+subfolders+'/100/exs.pl'
        directories.append(path)

    for x in directories:
        amount = math.floor(int((sum(1 for line in open(x)))*float(percent)))
        num_lines[0].append(str(x))
        num_lines[1].append(str(amount))

for x in args:
    if x == '--percent':
        percent_amount = args[1]
        func(args[1])
        args.pop(0)
        args.pop(0)
        percent = True
        args.append('--max-examples')

#print(num_lines)

strargs = " ".join(str(x) for x in args)

with open('output.txt', 'w') as output:
    output.truncate()

parent = pathlib.PurePath(file_path).name
print('Domain:', parent)

for foldername in os.listdir(file_path):

    start = time.time()

    f = os.path.join(file_path, foldername)
    if foldername ==".DS_Store":
        continue

    print('Action: ', foldername)

    with open('output.txt', 'a') as output:
        output.write(parent)
        output.write(',')
        output.write(foldername)
        output.write(',')
        if percent == True:
            output.write(strargs + ' --percent ' + percent_amount)
        if percent == False:
            output.write(strargs)
        output.write(',')

    if percent == True:
        for x in num_lines[0]:
            if foldername in x:
                index = num_lines[0].index(x)
                os.system(poppercommand + " " + f +"/100 " + strargs + ' ' + num_lines[1][index] + " " + outputfile)
    #os.system(poppercommand + " " + f + " " + outputfile)
    else:
        os.system(poppercommand + " " + f +"/100 " + strargs + " " + outputfile)


    end = time.time()
    timeTaken = round(end-start, 2)
    print('in:', timeTaken, 'seconds')

    with open("output.txt", "r") as f:
        lines = f.readlines()

    lines[currentLine] = lines[currentLine].strip('\n') + ',' + str(timeTaken) + '\n'
    with open("output.txt", "w") as f:
        f.writelines(lines)

    currentLine = currentLine+1