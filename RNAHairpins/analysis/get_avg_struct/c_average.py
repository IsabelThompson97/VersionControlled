import pandas as pd
data = pd.read_csv("rmsdfromAvg.out", sep=r'\s+')
data.head()
min = data.loc[data["RMSD_00002"].idxmin()]
print(min)
  

