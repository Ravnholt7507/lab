import pandas as pd

data = pd.read_csv('/home/rune/Desktop/Popper-main/output.txt', header=None)

data.columns = ['Domain','Action','Args','Precision','Recall','TP','FN','TN','FP','Size']

data.to_csv('/home/rune/Desktop/Popper-main/Tests.csv',mode='a', index=None)

