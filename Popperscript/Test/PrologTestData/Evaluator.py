from pyswip import Prolog
import os
import time
import pathlib
import sys
import math
import shutil

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

prolog = Prolog()
PosOrNeg=[]
TrueOrFalse=[]
poppercommand = "python3 popper.py -q"

file_path = '/home/mikkel/Skrivebord/Popper-main/examples/domainfiles/depots'
TrainPath = '/70'
TestPath = '/30'

with open('prolog-facts.pl', 'w') as output:
	output.truncate()
    
with open('output.txt', 'w') as output:
	output.truncate()

strargs = " ".join(str(x) for x in args)

parent = pathlib.PurePath(file_path).name
print('Domain:', parent)

def exampleFormatter(Fromfile, ToFile):
	fr = open(Fromfile, "r")
	fw = open(ToFile, "a")
	next(fr)
	for line in fr:
		if "pos" in line:
			PosOrNeg.append("pos")
		if "neg" in line:
			PosOrNeg.append("neg")
		line = line.replace("pos(","query(").replace("neg(","query(")
		fw.write(line)


def PrintNoSolution(foldername):
	with open('output.txt', 'a') as output:
		output.write(f'{parent},{foldername},No Sol,,,,,,,, \n')

def PrologValidator(PrologFacts, Popperstats, foldername, time):  #Calculates precision and recall and writes to output
	stats = Popperstats.split(',')
	tp,tn,fp,fn = 0,0,0,0
	size=stats[6]
	exampleFormatter(f+TestPath+"/exs.pl", PrologFacts)
	
	prolog.consult(PrologFacts)
	prolog.consult('PrologRun.pl')
	
	with open("Answer.txt") as Output:
		for line in Output:
			TrueOrFalse.append(line)
	i=0
	while i < (len(PosOrNeg)):
		if "pos" in PosOrNeg[i] and "yes" in TrueOrFalse[i]: tp += 1
		if "pos" in PosOrNeg[i] and "no" in TrueOrFalse[i]: fn += 1
		if "neg" in PosOrNeg[i] and "yes" in TrueOrFalse[i]: fp += 1
		if "neg" in PosOrNeg[i] and "no" in TrueOrFalse[i]: tn += 1
		i += 1
	precision = 'n/a'
	if (tp+fp) > 0:
		precision = f'{tp / (tp+fp):0.2f}'
	recall = 'n/a'
	if (tp+fn) > 0:
		recall = f'{tp / (tp+fn):0.2f}'
	with open('output.txt', 'a') as output:
		output.write(f"{parent},{foldername},{strargs},{precision},{recall},{tp},{fn},{tn},{fp},{time},{size}")
	PosOrNeg.clear()
	TrueOrFalse.clear()

for foldername in os.listdir(file_path):
	f = os.path.join(file_path, foldername)
	PrologFacts = f+'/prolog-facts.pl'
	print('Action: ', foldername)
	
	shutil.copy(f+TestPath+"/bk.pl", PrologFacts)
	
	start = time.time()
	os.system(poppercommand + " " + f + TrainPath + strargs + " " + ">>" + 'tempfile.txt') #print rules to prolog file
	
	end = time.time()
	timeTaken = round(end-start, 2)
	print('in:', timeTaken, 'seconds')
	
	
	with open('tempfile.txt', 'r+') as tempfile:
		 temp = tempfile.read()
		 data = temp.split('#')  #data[0]=stats, data[1]=regler
	with open('tempfile.txt', 'w') as tempfile:
		 tempfile.truncate()
	
	if "NO SOLUTION" in data[0]:
		PrintNoSolution(foldername)
	else:
		with open(PrologFacts, 'a') as file:
			file.write(data[1])
		PrologValidator(PrologFacts, data[0], foldername, timeTaken) #Evaluate with prolog. Takes the path to the prolog file
	
