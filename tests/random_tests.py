from rtcwlog.constants.logtext import Const
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

rtcwlogfile = r".\data\test_samples\rtcwconsole-2020-02-17.log"

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

from rtcwlog.clientlog import ClientLogProcessor
from rtcwlog.report.htmlreports import HTMLReport
bucket_name = "rtcw-stats-py-sci"
file_key = "input/2020-06-05-05-29-07-rtcwconsole.log"
debug=True
debug_file = r".\debug_file.txt"



processor = ClientLogProcessor(s3bucket=bucket_name, s3file = file_key, debug = debug, debug_file = debug_file)
result = processor.process_log()
html_report = HTMLReport(result,amendments={"KPM":0.3,"KDR":0.3})
local_file, filename = html_report.report_to_html()


######################
### Best friends #####
######################

pd.set_option('display.max_rows', 500)
pd.set_option("display.max_columns",20)
pd.set_option("display.max_colwidth",15)
pd.set_option("display.width",500)
from rtcwlog.constants.logtext import Const


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

####################################
# See dataset integrity on a graph #
####################################
import seaborn as sns; sns.set()
sns.heatmap(result["stats"].isnull(),yticklabels=False,cbar=False, cmap='viridis')
sns.heatmap(result["matches"].isnull(),yticklabels=False,cbar=False, cmap='viridis')
sns.heatmap(result["logs"].isnull(),yticklabels=False,cbar=False, cmap='viridis')

####################################
# See who hadnt played in a while  #
####################################
import numpy as np
stats = bigresult2020["stats"]
res = stats[["Killer","round_guid","match_date"]].groupby(["Killer"]).agg({'round_guid' : "count",'match_date' : np.max})
res.columns = ["Rounds_played", "Last_seen"]
res[res["Rounds_played"]>20].sort_values("Last_seen").reset_index()

####################################
# ELO to chart                     #
####################################
elo_progress = pd.read_csv("..\data\elo\elo.csv")
games = pd.Series(elo_progress["gameno"].unique())
games = games[games > games.astype(int).quantile(.8)]
elo_progress.index = elo_progress["gameno"].astype(str) + elo_progress["player"]

_data = {}
players = bigresult["stats"].reset_index()["index"].value_counts().nlargest(30).index.values
#players = elo_progress["player"].unique()

for player in players:
    data = []
    elo = 100
    tmp = elo_progress[elo_progress["player"]==player]
    for game in games:
        idx = str(game) + player
        if idx in tmp.index.values:
            elo = tmp.loc[idx, "elo"].astype(int)
        data.append(int(elo))
    _data[player] = data
    
import json

with open(r'..\data\elo\games.txt', 'w') as file:
     file.write(json.dumps(list(games))) # use `json.loads` to do the reverse
with open(r'..\data\elo\elo_json.txt', 'w') as file:
     file.write(json.dumps(_data)) # use `json.loads` to do the reverse
     
from bs4 import BeautifulSoup
from bs4 import Tag

with open(r'..\seasons\elos-template.html', 'r') as f:

    contents = f.read()

    soup = BeautifulSoup(contents, 'lxml')
    tag = soup.body.script
    tag.string = tag.string.replace("@@games",json.dumps(list(games))).replace("@@data",json.dumps(_data))
    print(soup.body.script)
    
with open(r'..\data\elo\elos.html', 'w') as file:
     file.write(soup.prettify()) # use `json.loads` to do the reverse


####################################
# Find zero player stats           #
####################################
for c in playerdf.columns:
    if len(playerdf[c].unique()) < 5:
        print(c, " ", len(playerdf[c].unique()))
        print(playerdf[c].unique())
        
        
####################################
# process guids                    #
####################################
from rtcwlog.utils.rtcwcolors import stripColors , setup_colors
from collections import Counter
colors = setup_colors()

guids = {}
with open(r"C:\a\2019-2020-guids.txt","r") as file:
    for line in file:      
        line = stripColors(line, colors)
        guid = line.replace("PunkBuster Client:","").strip()[3:11]
        player = line.replace("PunkBuster Client:","").strip()[31:]
        print(line.replace("PunkBuster Client:","").strip()[3:11], line.replace("PunkBuster Client:","").strip()[31:].ljust(20), line.strip())
        if guid not in guids:
            guids[guid] = Counter()
        guids[guid][player] +=1

for g in guids:
    print("\"", g, "\" : \"", guids[g].most_common(1)[0][0], "\",", sep="")

guids = {}
with open(r"C:\a\201x-guids-unlisted.txt","r") as file:
    for line in file:
        tokens = line.strip().split(" ")
        guid = tokens[1][0:8]
        player = tokens[-1]
        print(guid, player.ljust(20), line.strip())
        if guid not in guids:
            guids[guid] = Counter()
        guids[guid][player] +=1

for g in guids:
    print("\"", g, "\" : \"", guids[g].most_common(1)[0][0], "\",", sep="")
        
        
#for i, l in enumerate("14 19ce8ec3(-) OK   3.1 0{0|0} [>>] Cliffdark"): print(i,l)

import requests
import time as _time
t1 = _time.time()
response = requests.get("https://a1xebidwfb.execute-api.us-east-1.amazonaws.com/default/rtcw-guids?guids=349004f0,3c155812,0471e175,72b633a9")
t2 = _time.time()
print ("[t] Time to call API: " + str(round((t2 - t1),3)) + " s")
# Print the status code of the response.
print(json.loads(response.text))


import re 
x = re.search("[A-Fa-f0-9]{8}\(-\) OK   (.*)} (.*)","12 0471e175(-) OK   3.0 0{0|0} donka")
print(x[0][0:8] + " : " + x[2])

teststr = """
^55  ae2a45bc(-) OK   3.0 0{0|0} ^n.:.^7spaztik
^56  e79bf650(-) OK   3.0 0{0|0} ^cf^0es^ctus
^57  39c94359(-) OK   3.0 0{0|0} ^ecaffbe ^3bryant
^58  0471e175(-) OK   3.0 0{0|0} ^1N^7/^4A ^1d^7onk^4z
^59  9379b5c9(-) OK   3.0 0{0|0} ^7Pasek^3*
^510 1fd439bb(-) OK   3.0 0{0|0} ^7n/a SOURCE
^511 90d3a7c2(-) OK   3.0 0{0|0} ^>C^7y^>pher
^512 cbd47303(-) OK   3.0 0{0|0} ^5-^0eh^5-^7bri^5an
^513 d1a52e5f(-) OK   3.0 0{0|0} ^3reker
^514 f0e29ead(-) OK   3.0 0{0|0} ^1N^7/^4A ^7Ra!ser
^515 bc975af2(-) OK   3.0 0{0|0} ^3teker
^516 2a463009(-) OK   3.0 0{0|0} ^0e^3X^0e^7|^3F^0logzero
^517 f742e062(-) OK   3.0 0{0|0} ^0-^1=^7prowler^1=^0-
^518 19ce8ec3(-) OK   3.0 0{0|0} ^0[^7>>^0] Cliffdark
^519 6191c31f(-) OK   3.0 0{0|0} ^6parhcer
^520 2354ba51(-) OK   3.2 0{0|0} ^nnigel
^521 bc2042f9(-) OK   3.2 0{0|0} ^5.^5:^5.^7Meanguine
^522 9f1c131c(-) OK   4.2 0{0|0} shoot^0z
^55  6de54f4d(-) OK   3.0 0{0|0} ^0.:.^7c@k-el
^56  ae2a45bc(-) OK   3.0 0{0|0} ^0.:.^7spaztik
^57  0656b8b9(-) OK   3.0 0{0|0} ^>Joh^4n_M^dull^uins
^58  2354ba51(-) OK   3.0 0{0|0} ^nnigel
^59  69c691cd(-) OK   3.0 0{0|0} ^>fister^0Miagi
^510 e79bf650(-) OK   3.0 0{0|0} ^2.:.^6^1^7festus
^511 1fd439bb(-) OK   3.0 0{0|0} ^7SOURCE
^512 17e888cc(-) OK   3.0 0{0|0} ^1D^2i^3l^4l^5W^6e^7e^8d
^513 2a463009(-) OK   3.0 0{0|0} ^0e^3X^0e^7|^3F^0logzero
^514 0471e175(-) OK   3.0 0{0|0} donka
^516 f0e29ead(-) OK   3.0 0{0|0} ^1N^7/^4A ^7Ra!ser
^55  17e888cc(-) OK   3.0 0{0|0} ^1D^2i^3l^4l^5W^6e^7e^8d
^56  0471e175(-) OK   3.0 0{0|0} donka
^57  1fd439bb(-) OK   3.0 0{0|0} SOURCE
^58  2354ba51(-) OK   3.0 0{0|0} ^nnigel
^59  4df83547(-) OK   2.9 0{0|0} parcher
^510 ae2a45bc(-) OK   3.0 0{0|0} ^ospaztik
^511 f0e29ead(-) OK   3.0 0{0|0} ^0Ra!ser
^512 26732ba8(-) OK   3.0 0{0|0} Kittens
^513 19ce8ec3(-) OK   3.0 0{0|0} ^0[^7>>^0] Cliffdark
^514 727a2b29(-) OK   3.0 0{0|0} ^pTK^w|^PPOW
^515 90d3a7c2(-) OK   3.0 0{0|0} ^>C^7y^>pher
^516 69c691cd(-) OK   3.0 0{0|0} ^0-[^1x^0]-DeadEye
^517 eec144bf(-) OK   3.0 0{0|0} Marcus ^5Mariguta
^518 dda4d8d9(-) OK   3.0 0{0|0} ^0e^1X*^7Fe^0st^2^1us
^519 9379b5c9(-) OK   3.0 0{0|0} ^eSKOL^3|^eBoo^37^ey
^520 3c155812(-) OK   3.3 0{0|0} elsa
^521 fa8da266(-) OK   3.1 0{0|0} ^0tweek
^55  2a463009(-) OK   3.0 1{0|0} ^0e^3X^0e^7|^0Flog^3z^0ero
^56  6e79c99b(-) OK   3.0 1{0|0} ^0magik
^57  d61dff40(-) OK   3.0 1{0|0} ^ifromiam
^58  57e36653(-) OK   3.0 1{0|0} spaztik
^59  6de54f4d(-) OK   3.0 1{0|0} c@k-el
^510 3c155812(-) OK   3.0 1{0|0} LLM ^vBecky ^cG
^511 c0c35219(-) OK   3.0 1{0|0} miles
^512 70bbe988(-) OK   3.0 1{0|0} ^cconsc^7i^cous^7*
^513 d0af5e20(-) OK   3.0 1{0|0} ^0fonze^1*
^514 0471e175(-) OK   3.0 1{0|0} donka
^515 39c94359(-) OK   3.0 1{0|0} fuck it caff
^516 69c691cd(-) OK   3.0 1{0|0} ^0Fister^1Miagi
^55  6de54f4d(-) OK   3.0 0{0|0} ^0.:.^7c@k-el
^56  ae2a45bc(-) OK   3.0 0{0|0} ^0.:.^7spaztik
^57  0656b8b9(-) OK   3.0 0{0|0} ^>Joh^4n_M^dull^uins
^58  2354ba51(-) OK   3.0 0{0|0} ^nnigel
^59  69c691cd(-) OK   3.0 0{0|0} ^>fister^0Miagi
^510 e79bf650(-) OK   3.0 0{0|0} ^2.:.^6^1^7festus
^511 1fd439bb(-) OK   3.0 0{0|0} ^7SOURCE
^512 17e888cc(-) OK   3.0 0{0|0} ^1D^2i^3l^4l^5W^6e^7e^8d
^513 2a463009(-) OK   3.0 0{0|0} ^0e^3X^0e^7|^3F^0logzero
^514 0471e175(-) OK   3.0 0{0|0} donka
^516 f0e29ead(-) OK   3.0 0{0|0} ^1N^7/^4A ^7Ra!ser
"""

from rtcwlog.utils.rtcwcolors import stripColors , setup_colors
colors = setup_colors()
strings = teststr.split("\n")
for s in strings:
    s = stripColors(s, colors) 
    x = re.search("[A-Fa-f0-9]{8}\(-\) OK   (.*)} (.*)",s)
    if x is not None:
        print("String: " + s.ljust(70) + " found: " + x[0][0:8] + " : " + x[2])
    

##
#List of people who played more than 20 rounds this year attached with ELO
#
rounds2020 = bigresult2020["stats"].groupby(level=0).count()["round_guid"]
rounds2020elo = rounds2020.to_frame().join(elos)
rounds2020elofilt  = rounds2020elo[rounds2020elo["round_guid"]>20].reset_index().sort_values("index")
rounds2020elofilt.columns = ['player', 'rounds', 'elo', 'kek']
rounds2020elofilt["elo"] = rounds2020elofilt["elo"].astype(int)
rounds2020elofilt.index = rounds2020elofilt['player']
rounds2020elofilt[['rounds', 'elo']]

###
#dAYS OF WEEK
###
stats = bigresult2020["stats"]
stats["match_date_date"] = pd.to_datetime(stats["match_date"], format='%Y-%m-%d %H:%M:%S', errors="raise")
stats["year"] = stats["match_date_date"].dt.year.astype(int)
stats["month"] = stats["match_date_date"].dt.month.astype(int)
stats["weekday"] = stats["match_date_date"].dt.dayofweek
recent = stats[(stats["month"] == 10) | (stats["month"] == 9)][["Killer","weekday"]].copy()
recent["rounds"] = 1
recent_grouped = recent.groupby(["Killer", "weekday"]).count().reset_index()
print("The day of the week with Monday=0, T=1,W=2,Th=3,F=4,Sat=5, Sunday=6")
df = recent_grouped.reset_index().pivot(index='Killer', columns='weekday', values='rounds')
df.fillna(0).astype(int).sort_values(by=[3,6], ascending=False)


###
#Guid checks
###
pd.set_option('display.max_rows', 500)
pd.set_option("display.max_columns",30)
pd.set_option("display.max_colwidth",20)
pd.set_option("display.width",300)

s = bigresult2020["stats"]
guids = s.groupby(["Killer","pb_guid"]).count()["side"].reset_index()
guids = guids[~guids["pb_guid"].isin([""," "])]
print(guids.sort_values(by="pb_guid"))

guids_dup = guids.groupby(["pb_guid"]).count()["Killer"].reset_index()
guids_dup = guids_dup[guids_dup["Killer"]>1]
print(guids[guids["pb_guid"].isin(guids_dup["pb_guid"].values)].sort_values(by="pb_guid"))

duplicates = s[s["pb_guid"].isin(guids_dup["pb_guid"].values)][["round_guid","match_date","Killer","pb_guid"]].sort_values(by=["pb_guid", "match_date"])
print(duplicates)

#get only right guids
guids_sorted = guids.sort_values(by=["pb_guid","side"], ascending = False)
guids_unique = guids_sorted.drop_duplicates(["pb_guid"], keep="first")
print("Writing guids pickle to: " + os.path.abspath(r'..\seasons\guids.pkl'))
guids_unique.to_pickle(r'..\seasons\guids.pkl')


#player sanity check - not as important
players_dup = guids_unique.groupby(["Killer"]).count()["pb_guid"].reset_index()
players_dup = players_dup[players_dup["pb_guid"]>1]

duplicate_players = guids_unique[guids_unique["Killer"].isin(players_dup["Killer"].values)].sort_values(by=["Killer"])
print(duplicate_players)
s[s["pb_guid"]=="3bcbcf14"][["round_guid","match_date","Killer","pb_guid"]].sort_values(by=["pb_guid", "match_date"])
