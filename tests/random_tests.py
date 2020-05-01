from constants.logtext import Const
import pandas as pd
import numpy as np


df = pd.DataFrame()
df["a"] = [1,2,3,4,5,6,7]
df["b"] = [0,2,np.nan,4,5,6,7]
df["c"] = df["a"]/df["b"]
df["c"].astype(int) #error
df["c"].round(1)


nonadf = df.fillna(0)
nonadf["c"].astype(int) #still error on inf

pd.options.mode.use_inf_as_na = True
nonadf["c"].astype(int) #still error on inf because it's not autoreplaced

import numpy as np
df = pd.DataFrame()
df["a"] = [1,2,3,4,5,6,7]
df["b"] = [0,2,np.nan,4,5,6,7]
df["c"] = df["a"]/df["b"]
df = df.fillna(0)
df["c"].astype(int)
df.shift(-2).loc[1,"c"] == df.loc[1,"c"]


#######################################################################
#                    ENCODING                                         #
#######################################################################

rtcwlogfile = r".\test_samples\rtcwconsole-2020-02-17.log"

with open(rtcwlogfile,"r") as file:
    lines = file.readlines()
            
with open(rtcwlogfile,"rb") as file:
    lines1 = [l.decode('utf-8', 'ignore') for l in file.readlines()]
            
for i in range(0,len(lines)):
    if (lines[i] == lines1[i]):
        if(i%500 == 0):
            print("Equal")
    else:
        print(str(i))
        print(lines[i][0:100])
        print(lines1[i][0:100])

import codecs
encodings = ["utf-8","iso8859-1","cp1252"]
for e in encodings:
    try:
        fd = codecs.open(rtcwlogfile,'r',encoding=e)
        data = fd.read()
        print(e + " encoding worked")
    except UnicodeDecodeError as err:
        print("Encoding failed: ", err)

#######################################################################
#                    Kwargs                                           #
#######################################################################

def kek(**kwargs):
    if "local_file" in kwargs and ("s3bucket" in kwargs or "s3file" in kwargs):
        print("Provide either local_file or s3 information (s3bucket and s3file)")
        return None
    
    if "local_file" in kwargs:
        return "Process using " + kwargs.get("local_file")
    
    if "bucket" in kwargs:
        return "Process using " + kwargs.get("bucket")


#######################################################################
#                    Average values for panz, sniper, smokes          #
#######################################################################
stats_copy = bigresult["stats"].copy()
stats = stats_copy[["Kills","Panzerfaust", "class"]]
stats = stats[stats["Panzerfaust"]>0]
stats["ratio"] = stats["Panzerfaust"]/stats["Kills"]
stats["ratio"].hist()
print("Panz mean: " + str(stats.mean()["ratio"]))
print("Panz median: " + str(stats.mean()["ratio"]))

stats = stats_copy[["Kills","Sniper", "class"]]
stats = stats[stats["Sniper"]>0]
stats["ratio"] = stats["Sniper"]/stats["Kills"]
stats["ratio"].hist()
print("Sniper mean: " + str(stats.mean()["ratio"]))
print("Sniper median: " + str(stats.mean()["ratio"]))

stats = stats_copy[["Kills","Airstrike", "Artillery", "class"]]
stats = stats[(stats["Airstrike"]>0) | (stats["Artillery"]>0)]
stats["ratio"] = (stats["Airstrike"] + stats["Artillery"])/stats["Kills"]
stats["ratio"].hist()
print("LT mean: " + str(stats.mean()["ratio"]))
print("LT median: " + str(stats.mean()["ratio"]))


#######################################################################
#                    Average values DMG, gibs, scores, etc            #
#######################################################################
s = bigresult["stats"].copy()
s = s[['OSP_Damage_Given', 'OSP_Damage_Received', 'OSP_Deaths', 'OSP_Gibs', 'OSP_Kills', 'OSP_Score','OSP_Suicides', 'OSP_TK', 'OSP_Team_Damage','round_time']].dropna()
#s["OSP_Damage_Given"] = s["OSP_Damage_Given"].astype(int)
#s["OSP_Damage_Received"] = s["OSP_Damage_Received"].astype(int)
s = s.astype(float)
s["dg"] = s["OSP_Damage_Given"]/s["OSP_Kills"]
s["dr"] = s["OSP_Damage_Received"]/s["OSP_Deaths"]
s["gib"] = s["OSP_Gibs"]/s["OSP_Kills"]
s["score"] = (s[Const.STAT_OSP_SUM_SCORE] - s[Const.STAT_OSP_SUM_FRAGS] + s[Const.STAT_OSP_SUM_SUICIDES]*3 + s[Const.STAT_OSP_SUM_TK]*3)/s["round_time"]
s["td"] = s["OSP_Team_Damage"]/s["round_time"]
ssum = s[['dg', 'dr', 'gib', 'score', 'td']].mean(axis=0)


############################################
#    Check if panda objects are immutable  #
############################################
import pandas as pd
df = pd.DataFrame([[1,2],[3,4],[5,6]], columns = ["col1","col2"])

def other_func(df_param):
    df_param["new_column"] = df_param["col1"].add(10)

print("Dataframe before passing to function")
print(df)
other_func(df)
print("Dataframe after being used in the function")
print(df)

'''
Dataframe before passing to function
   col1  col2
0     1     2
1     3     4
2     5     6
Dataframe after being used in the function
   col1  col2  new_column
0     1     2          11
1     3     4          13
2     5     6          15
'''
