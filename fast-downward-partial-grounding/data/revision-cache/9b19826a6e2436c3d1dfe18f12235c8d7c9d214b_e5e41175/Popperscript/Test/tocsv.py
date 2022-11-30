import pandas as pd

data = pd.read_csv('/Users/minmacbook/Documents/Popper-main/output.txt', header=None)

data.columns = ['Domain','Action','Args','Precision','Recall','TP','FN','TN','FP','Size','Time']

data.to_csv('/Users/minmacbook/Documents/Popper-main/Tests.csv',mode='a', index=None)