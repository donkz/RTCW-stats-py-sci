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

#########
# PATH  #
#########
os.getcwd()



############
# S# File  #
############

from processfile import FileProcessor
from utils.htmlreports import HTMLReport
bucket_name = "rtcw-stats-py-sci"
file_key = "input/donka4-04-27-2020-06-20-31.log"
debug=True
debug_file = r".\debug_file.txt"

processor = FileProcessor(s3bucket=bucket_name, s3file = file_key, debug = debug, debug_file = "/tmp/debug_file.txt")
result = processor.process_log()
html_report = HTMLReport(result)
local_file, filename = html_report.report_to_html(folder="/tmp/", filenoext = os.path.basename(file_key).replace(".log",""))


######################
### Best friends #####
######################

pd.set_option('display.max_rows', 500)
pd.set_option("display.max_columns",20)
pd.set_option("display.max_colwidth",15)
pd.set_option("display.width",300)
from constants.logtext import Const


stats = result["stats"].copy()
sr2 = stats[stats["round_num"]==2][["game_result", "round_guid", Const.STAT_OSP_SUM_TEAM]]
sr2 = sr2.reset_index()
sr2 = sr2.dropna()
sr2.columns = ['friend', 'game_result', 'round_guid', "team"]
sr2b = sr2.copy()

joined = sr2.merge(sr2b, left_on=['team', 'round_guid'], right_on = ['team', 'round_guid'], how='left', suffixes=('-a','-b'))
joined = joined.drop(["game_result-b"],axis=1).rename(columns={"game_result-a" : "game_result"})
joined = joined[joined["friend-a"] != joined["friend-b"]]
joined["key"] = joined["friend-a"] + joined["friend-b"] + joined["round_guid"] + joined['team']
joined["keysort"] = ["".join(sorted(a)) for a in joined["key"]]
joined["num"] = 1

no_dups = joined.sort_values(by=["friend-a","round_guid"]).drop_duplicates(subset = ["keysort"], keep = "first", inplace=False)

pairgames = no_dups[["friend-a","friend-b","num"]].groupby(["friend-a","friend-b"]).sum().reset_index()
wins = no_dups[no_dups["game_result"]=="WON"][["friend-a","friend-b","num"]].groupby(["friend-a","friend-b"]).sum().reset_index()
losses = no_dups[no_dups["game_result"]=="LOST"][["friend-a","friend-b","num"]].groupby(["friend-a","friend-b"]).sum().reset_index()
fh = no_dups[no_dups["game_result"]=="FULLHOLD"][["friend-a","friend-b","num"]].groupby(["friend-a","friend-b"]).sum().reset_index()


pairgames.columns = ['friend-a', 'friend-b', 'games']
wins.columns = ['friend-a', 'friend-b', 'won']
losses.columns = ['friend-a', 'friend-b', 'lost']
fh.columns = ['friend-a', 'friend-b', 'fullhold']

final = pairgames.merge(wins, left_on=['friend-a', 'friend-b'], right_on = ['friend-a', 'friend-b'], how='left').merge(losses, left_on=['friend-a', 'friend-b'], right_on = ['friend-a', 'friend-b'], how='left').merge(fh, left_on=['friend-a', 'friend-b'], right_on = ['friend-a', 'friend-b'], how='left')
final = final.fillna(0)
final["win%"] = final["won"]/final["games"]*100
final["loss%"] = final["lost"]/final["games"]*100
final["fullhold%"] = final["fullhold"]/final["games"]*100

desired_num_rows = 30 
min_games_together = 20 
min_win_ratio = 50

#topx = final["games"].sort_values().tail(desired_num_rows).min()
#topx = topx if topx > min_games_together else min_games_together
final = final[(final["games"]>=min_games_together) & (final["win%"]>= min_win_ratio)]

final = final.round(1)
final["won"] = final["won"].astype(int)
final["lost"] = final["lost"].astype(int)
final["fullhold"] = final["fullhold"].astype(int)
final = final.sort_values(by="win%", ascending=False).head(desired_num_rows).reset_index().drop(["index"],axis=1)
final[['friend-a', 'friend-b', 'games', 'win%', 'loss%', 'fullhold%']]





