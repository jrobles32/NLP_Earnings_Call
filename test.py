import pandas as pd
import glob
import os


# df = pd.DataFrame()

# files = os.path.join('data*.csv')
# files = glob.glob(files)

# df = pd.concat(map(pd.read_csv, files), ignore_index=True)

# df.to_csv('all_transcripts.csv', index=False)


dict = {'key1':['dfdaf', 'adadcadf'], 'key2':['davcx', 'adfad'], 'key3':['daadfa', 'dafda']}
dict2 = {'key1':['dfdaf', 'adadcadf'], 'key2':['davcx', 'adfad'], 'key3':['daadfa', 'dafda']}

df = pd.DataFrame()

for dicts in [dict, dict2]:
   df = pd.concat([df, pd.DataFrame(dicts)], ignore_index=True)

print(df)

