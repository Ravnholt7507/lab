import os
import shutil
import sys
import math

#Argumenter kommer i rækkefælge af "Procent", "Src dir", "dest dir"
args = sys.argv

#Skrives "70-30"
args.pop(0)

TrainSet,TestSet = args[0].split("-")
if (int(TrainSet) + int(TestSet)) == 100:
	#"/home/bskovl/Desktop/domainfiles/depots/drive"
	src = args[1]

	#"/home/bskovl/Desktop/domainfiles" (Opretter de nødvendige mapper)
	TTdir = args[2]

	Traindst = TTdir + "/Train"
	Testdst = f"{TTdir}/Test"

	shutil.copytree(src, Traindst, dirs_exist_ok=True)
	shutil.copytree(src, Testdst, dirs_exist_ok=True)

	with open(Traindst + "/exs.pl", "r") as fr:
		LinesinFile = fr.readlines()
		TrainSet = len(LinesinFile) * int(TrainSet)/100
		TrainSet = math.ceil(TrainSet)
		
	#Train mappe
	with open(Traindst + "/exs.pl", "w") as fw:
		fw.writelines(LinesinFile[:TrainSet])
		
	#Test mappe
	with open(Testdst + "/exs.pl", "w") as fw:
		fw.writelines(LinesinFile[TrainSet:])
else:
	print("Dats the wrong number, Monogl")
