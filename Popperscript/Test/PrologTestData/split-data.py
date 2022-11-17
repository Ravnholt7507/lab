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
	#TTdir = args[2]
	
	for foldername in os.listdir(src):
		TrainSet,TestSet = args[0].split("-")
		f = os.path.join(src, foldername)
		Traindst = f + '/' + str(TrainSet)
		Testdst = f + '/' + str(TestSet)
		
		shutil.copytree(f +"/100", Traindst, dirs_exist_ok=True) #copies from file containing all data 
		shutil.copytree(f +"/100", Testdst, dirs_exist_ok=True)

		with open(Traindst + "/exs.pl", "r") as fr:
			LinesinFile = fr.readlines()
			TrainSet = len(LinesinFile) * int(TrainSet)/100
			TrainSet = math.ceil(TrainSet)
			LineofProblem = TrainSet-1
		
		ExProblem = LinesinFile[LineofProblem].split(",")
		ExProblem = ExProblem[-1].replace(")).", "")
		EndProblem = LinesinFile[-1].split(",")
		EndProblem = EndProblem[-1].replace(")).", "")
		x = ExProblem
		
		if ExProblem == EndProblem:
			while x == ExProblem:
				x = LinesinFile[LineofProblem].split(",")
				x = x[-1].replace(")).", "")
				LineofProblem -= 1
			LineofProblem += 2
		else:	
			while x == ExProblem:
				x = LinesinFile[LineofProblem].split(",")
				x = x[-1].replace(")).", "")
				LineofProblem += 1
			LineofProblem -= 1
		 
		#Train mappe
		with open(Traindst + "/exs.pl", "w") as fw:
			fw.writelines(LinesinFile[:LineofProblem])
		
		#Test mappe
		with open(Testdst + "/exs.pl", "w") as fw:
			fw.writelines(LinesinFile[LineofProblem:])
else:
	print("Dats the wrong number, Monogl")
