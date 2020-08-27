import os, sys
import re
import traceback

from zipfile import ZipFile, is_zipfile
from datetime import datetime
import shutil
import time as _time

import pandas as pd
import numpy as np

from osp.const import Const, OSPFileLine, get_player_castings
from utils.ospstrings import process_OSP_line, osp_token_one_slash_two, osp_token_accuracy_round_num, osp_token_accuracy_playername_round
from utils.ospstrings import get_round_guid_osp
from utils.decorators import decorator_func_timeit

from iortcw.statswriter import StatsWriter

zips = {
        "test" :"..\\test_samples\\playername.zip",
        "donka2019" : r"C:\a\donka-2012-2019.zip",
        "luna" : r"C:\a\lunastats.zip",
        "nigel" : r"C:\a\nigel.zip",
        "donka2020-a" : r"C:\a\donka-2020.01-2020.07.12.zip",
        "donka2005" : r"C:\a\donka-2005.04-2005.08.zip",
        "donka2004" : r"C:\a\donka-2004.12-2005.4.zip",
        "donka2006-b" : r"C:\a\donka-2006.12.zip",
        "donka2003" : r"C:\a\donka-2003.10-2004.10.zip",
        "donka2006-a" : r"C:\a\donka-2005.01.01-2006.03.07.zip",
        "miles" : r"C:\a\miles-to-2020.07.10.stats.zip",
        "conscious" : r"C:\a\conscious-2020.04.17-2020.07.09.zip"  ,  
        "murkey" : r"C:\a\murkey.zip",
        "cypher" : r"C:\a\cypher.zip",
        "kittens" : r"C:\a\kittens.zip",
        "source-a":r"C:\a\source-2017.11.07-2019.09.16.zip",
        "source-b":r"C:\a\source-2019.01.03-2020.04.24.zip",
        "source-c":r"C:\a\source-2020.06.02-2020.07.17.zip"
        }
        
        
#test_dir = "test_samples\stats"

#set relative path
RTCWPY_PATH = os.getcwd()
RTCWPY_PATH = RTCWPY_PATH.replace("\\osp","")
if not RTCWPY_PATH in sys.path:
    sys.path.append(RTCWPY_PATH)

def list_osp_files(path):
    print("[ ] Scanning files in " + path)
    
    osp_files = [] # will contain elements like [filepath,date]
    for subdir, dirs, files in os.walk(path):
            for file in files:
                #print os.path.join(subdir, file)
                filepath = subdir + os.sep + file

                if filepath.endswith(".txt"):
                    file_date_str = filepath.replace(path,"")[-22:]
                    file_date_dt = datetime.strptime(file_date_str, "\\%Y.%m.%d\\%H%M%S.txt" )
                    osp_files.append([filepath,file_date_dt])
    #print(osp_files)
    sorted_osp_files = sorted(osp_files,  key=lambda x: x[1])
    return sorted_osp_files

def get_osp_files(path):
    t1 = _time.time()
    print("[ ] Using path : " + path)
    filename, file_extension = os.path.splitext(path)
    
    main_file_name = os.path.split(path)[1].replace(".zip","")
    extract_to = "..\\temp" + "\\" + main_file_name + "\\"
    force_delete = False
    
    if(file_extension == ""):
        return os.path.abspath(path)
    
    #get tbw file from the tbwx
    if file_extension == ".zip" or file_extension == ".7z":
        if(is_zipfile(path) == False):
            print("[x] Not recognized zipfile")
            exit()
        with ZipFile(os.path.abspath(path), 'r') as zipObj:
            # Extract all the contents of zip file into a temp directory
            
            if os.path.isdir(extract_to):
                if force_delete:
                    try:
                        print("[ ] Deleting previous path: " + extract_to)
                        shutil.rmtree(extract_to)
                    except OSError as e:
                        print ("Error: %s - %s." % (e.filename, e.strerror))
                else:
                    print("[ ] Using previous extract folder: " + extract_to)
                    return os.path.abspath(extract_to)
            else: 
                try:
                    os.mkdir(extract_to)
                except:
                    print("Could not create a directory to write stats out to : " + extract_to)
            
            print("[ ] Extracting " + path + " to " + extract_to)
            zipObj.extractall(extract_to)
    t2 = _time.time()
    print ("[t] Time to unzip " + str(round((t2 - t1),3)) + " s")              
    return os.path.abspath(extract_to)


def osp_test(sorted_osp_files):
    osp_stats_begun = False
    lines = []
    for osp_file in sorted_osp_files:
        with open(osp_file[0],"r") as file:
                for line in file:
                    if line[0:26] == "TEAM   Player          Kll":
                        osp_stats_begun = True
                    if osp_stats_begun and (line[0:7] == 'Axis   ' or line[0:7] ==  'Allies '):
                        if line[7:13] != 'Totals':
                            lines.append(line.strip())
                    if line[0:24] == 'Allies Totals           ':
                        osp_stats_begun = False
                    if not osp_stats_begun:
                        #print(line.strip())
                        "kek"
                    if line[9:11] == ': ':
                        print(line.strip())
    print(*lines, sep = "\n")

def process_osp_files(sorted_osp_files):
    t1 = _time.time()
    players_all = {}
    rounds  = []
    i = 1
    for osp_file in sorted_osp_files:
        i +=1
        if i%1000 == 0:
            print("[ ] Processing file: " + str(i))
        try:
            osp_guid, osp_round, players =  process_osp_file(osp_file[0])
        except:
            print("[x] Failed to process " + osp_file[0] + " with the following error:\n\n")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback, limit=4, file=sys.stdout)
            continue

        players_all[osp_guid]= players
        rounds = rounds+ osp_round
    t2 = _time.time()
    print ("[t] Time to process " + str(round((t2 - t1),3)) + " s")
    return (players_all, rounds)

def get_new_player_stat(file_name):
    player_stat = Const.player_stat.copy()
    player_stat["file"] = file_name[-21:-4]
    archive = file_name.split("\\")[-3]
    if archive == "stats":
        archive = file_name.split("\\")[-4]
    player_stat["archive"] = archive
    return player_stat

def process_osp_file(file_name):
    #debug file_name = sorted_osp_files[0][0]
    with open(file_name,"r") as file:
        
        #init loop variables
        players = {}
        player_stat = get_new_player_stat(file_name)
        osp_round  = []
        osp_raw_lines = []
        current_player = None
        rounds = 1
        match_date = ""
        
        #go through each line in the file
        for line in file:
            line = line.strip()
            if len(line) == 0:
                continue
            
            osp_lines = OSPFileLine.LoadOSPLines()
            line_matched = False
            
            #for that line loop through all possible log line types and see which type of line it is
            for key, value in osp_lines.items():
                                
                x = re.search(value.regex, line)
                #print("Checking  " + value.regex)
                #if it looks like something we recognize (x is not None) then add this line appropriately
                if x:
                    line_matched = True
                    
                    if value.event == Const.EVENT_OSP_STATS_ACCURACY:
                        current_player, rounds = osp_token_accuracy_playername_round(x[1])
                        player_stat["rounds"] = rounds
                        break
                                   
                    if value.event == Const.EVENT_PLAYER_DMR or value.event == Const.EVENT_OSP_STATS_START:
                        if current_player and len(player_stat) > 0:
                            players[current_player] = player_stat #store the processed player
                            #reset & start new
                            current_player = None
                            player_stat = get_new_player_stat(file_name)
                        break
                    
                    if value.event == Const.EVENT_PLAYER_ACC:
                        hits,attacks = osp_token_one_slash_two(x[1][5:15].strip())

                        player_stat[value.mod + "_Accuracy"] =  x[1][0:5].strip()
                        player_stat[value.mod + "_Hits"] =  hits
                        player_stat[value.mod + "_Attacks"] =  attacks
                        if value.mod != Const.WEAPON_SYRINGE:
                            player_stat[value.mod + "_Kills"] =  x[1][15:19].strip()
                            player_stat[value.mod + "_Deaths"] =  x[1][19:23].strip() 
                        if value.mod in Const.YES_HEADSHOT:
                            player_stat[value.mod + "_HeadShots"] =  x[1][23:27].strip() 
                        

                        break
                     
                    if value.event == Const.EVENT_PLAYER_EXTRA:
                        if value.mod == Const.STAT_OSPFILE_PU_HEALTHPACK or value.mod == Const.STAT_OSPFILE_PU_AMMOPACK:
                            given, dropped = osp_token_one_slash_two(x[1].strip())
                            packtype = "Health" if value.mod == Const.STAT_OSPFILE_PU_HEALTHPACK else "Ammo"
                            player_stat[packtype + "Given"]= given
                            player_stat[packtype + "Dropped"]= dropped
                        if value.mod == Const.STAT_OSPFILE_PU_REVIVE:
                            player_stat["Revivals"] = x[1].strip()
                        break
                    
                    if value.event == Const.EVENT_OSP_STATS_ALLIES or value.event == Const.EVENT_OSP_STATS_AXIS: #OSP team stats per player
                        if re.search(osp_lines["ospend"].regex, line) or re.search(osp_lines["ospmid"].regex, line):
                            break
                        osp_player, osp_line = process_OSP_line(line)
                        if osp_line is None:
                            break #rest not executed
                        osp_round.append(osp_line)
                        osp_raw_lines.append(line.strip())   
                        break
                    
                    if value.event == Const.EVENT_PLAYER_TS:
                        match_date = str(datetime.strptime(x[1], "%H:%M:%S (%d %b %Y)"))
                        for p in players:
                            players[p]["match_date"] = match_date
                        break
                    
                    if value.event == Const.EVENT_OSP_STATS_NO_INFO: 
                        current_player = None
                        break
                    
                    
                    #print("re.search('"+value.regex+"','"+line+"') worked" + x[0])
                    break
                else:
                    #print("re.search('"+value.regex+"','"+line+"') didnt work")
                    ""
                    
            if not line_matched and len(line.strip()) > 0:
                print("[!] " + line + " was not processed. File: " + file_name)

        osp_guid = get_round_guid_osp(osp_raw_lines)
        
        for i in osp_round:
            i.append(osp_guid)    
            i.append(match_date)    
        return (osp_guid, osp_round, players)

def build_osp_df(osp_rounds):
    t1 = _time.time()
    columns = Const.osp_columns.copy()
    columns.append("osp_guid")
    columns.append("match_date")
    
    try:
        ospDF = pd.DataFrame(osp_rounds, columns = columns)
    except ValueError:
        print("[x] Failed to build osp dataframe.")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback, limit=10, file=sys.stdout)
        return pd.DataFrame(columns = columns)
    describe_df(ospDF, "OSP")
    ospDF.reset_index(drop=True, inplace=True)
    
    t2 = _time.time()
    print ("[t] Time to build ospDF " + str(round((t2 - t1),3)) + " s")
    
    return ospDF

def build_player_df(players_all):
    t1 = _time.time()
    flatten_players = {}
    i=0
    for osp_guid in players_all:
        i = i + 1
        for player in players_all[osp_guid]:
            one_player = players_all[osp_guid][player]
            one_player["osp_guid"] = osp_guid
            one_player["player"] = player
            flatten_players[i] = one_player
    playerdf = pd.DataFrame.from_dict(flatten_players, orient='index')
    playerdf.replace('', np.nan, inplace=True)
    playerdf.fillna(0,inplace=True)
    
    playerdf["submitter"] = playerdf["player"].value_counts().sort_values().tail(1).index.values[0]
    describe_df(playerdf, "player")
    t2 = _time.time()
    print ("[t] Time to build playerdf " + str(round((t2 - t1),3)) + " s")
    return playerdf

def describe_df(df, name):
    rows = str(len(df))
    size = str(round(df.size/1024/1024,1))
    print(f"[ ] Built {name} dataframe with {rows} rows and {size} MB in size.")

def process_zip_file(zip_file_path):
        
    path = get_osp_files(zip_file_path)
    #path = get_osp_files(test_dir)
    
    sorted_osp_files = list_osp_files(path)
    print("[ ] Found " + str(len(sorted_osp_files)) + " files in " + path)

    players_all, rounds = process_osp_files(sorted_osp_files)
    ospDF = build_osp_df(rounds)
    playerdf = build_player_df(players_all)
    
    #for r in rounds:
    #    print(build_osp_df([r]))
    
    archive = playerdf["archive"][0:1].values[0]
    castings = {}
    defaults = {}
    defaults["player"] = Const.player_stat
    castings["player"] = get_player_castings()
    
    writer = StatsWriter(media="disk", rootpath=RTCWPY_PATH, subpath=r"\output")
    writer.write_player({"osponly" : ospDF, "player" : playerdf}, archive, castings, defaults)
    
    return (playerdf, ospDF)

def load_parquet_extracts(subfolder):
    path = "..\\output\\" + subfolder
    players_all = None
    for subdir, dirs, files in os.walk(path):
            for file in files:
                #print os.path.join(subdir, file)
                print("Loading: " + subdir + os.sep + file)
                tmp = pd.read_parquet(subdir + os.sep + file)
                try:
                    players_all = players_all.append(tmp)
                except:
                    players_all = tmp
    return players_all

def weapon_accuracy(players_all, weapon, maxgames, headshot=False):
    headshots = weapon + '_HeadShots'
    attacks = weapon + '_Attacks'
    hits =  weapon + '_Hits'
    body =  weapon + '_Body'
    df = players_all[(players_all["rounds"]==2) & (players_all[hits] > 0)]
    
    agg_parms = {headshots:sum, hits:sum, attacks : sum,  "player" : "count"}
    if not headshot:
        agg_parms.pop(headshots)
        
    dfsum = df.groupby(["submitter"]).agg(agg_parms)
    
    columns = list(dfsum.columns)[:-1]  
    columns.append("games")
    
    dfsum.columns = columns
    dfsumfilt = dfsum[dfsum["games"] > maxgames].copy()
    if headshot:
        dfsumfilt["%hsratio"] = dfsumfilt[headshots]/dfsumfilt[hits]
        dfsumfilt[body] = dfsumfilt[hits] - dfsumfilt[headshots]
        dfsumfilt["dmg/bullet"] = (dfsumfilt[body]*Const.bullet_dmg[weapon][0] + dfsumfilt[headshots]*Const.bullet_dmg[weapon][1])/dfsumfilt[attacks]
    dfsumfilt["accuracy"] = dfsumfilt[hits]/dfsumfilt[attacks]
    #print(dfsumfilt.sort_values(by=["%hsratio"], ascending=True))
    #print(dfsumfilt.sort_values(by=["accuracy"], ascending=True))
    return dfsumfilt.sort_values(by=["accuracy"], ascending=True)
    

if __name__ == "__main__":
    
#    playerdf, ospDF = process_zip_file("..\\test_samples\\playername.zip")
#    process_zip_file(zips["donka2020-a"])
#    process_zip_file(zips["donka2005"]) 
#    process_zip_file(zips["donka2004"]) 
#    process_zip_file(zips["donka2006-b"]) 
#    process_zip_file(zips["donka2003"]) 
#    process_zip_file(zips["donka2006-a"]) 
#    process_zip_file(zips["miles"])
#    process_zip_file(zips["conscious"]) 
#    process_zip_file(zips["murkey"]) 
#    process_zip_file(zips["kittens"])
#    process_zip_file(zips["source-a"])
#    process_zip_file(zips["source-b"])
#    process_zip_file(zips["source-c"])
           
    players_all = load_parquet_extracts("player")
    osp  = load_parquet_extracts("osponly")
    
    players_all["match_date_date"] = pd.to_datetime(players_all["match_date"], format='%Y-%m-%d %H:%M:%S', errors="raise") #ignore’, ‘raise’, ‘coerce’} - for now leaving most strict
    osp["match_date_date"] = pd.to_datetime(osp["match_date"], format='%Y-%m-%d %H:%M:%S', errors="raise") #ignore’, ‘raise’, ‘coerce’} - for now leaving most strict
    players_all["year"] = players_all["match_date_date"].dt.year.astype(str)
    players_all["month"] = players_all["match_date_date"].dt.month.astype(str)
    osp["year"] = osp["match_date_date"].dt.year.astype(str)
    osp["month"] = osp["match_date_date"].dt.month.astype(str)
    
    #togetherness before cleanup
    osp_together = osp[["OSP_Player", "osp_guid", "year", "OSP_Damage_Given", "OSP_Damage_Received","match_date"]] \
        .groupby(["osp_guid", "OSP_Player", "year", "OSP_Damage_Given", "OSP_Damage_Received"]) \
        .agg({"match_date":"count"}) \
        .sort_values(by=["match_date"], ascending=True).reset_index()
    osp_together = osp_together.rename(columns={"match_date":"games"})
    osp_together[osp_together["games"]>1]["year"].unique()
    osp_together[(osp_together["games"]>1) & (osp_together["year"].astype(int)==2004)]
    guid = osp_together[(osp_together["games"]>1) & (osp_together["year"].astype(int)==2005)]["osp_guid"].values[-1]
    ######
    
    
    count_archives = players_all[["player", "archive"]].groupby(["archive"]).count().sort_values(by=["archive"]).rename(columns={"player":"archive_count"}).reset_index()
    count_names = players_all[["player", "archive", "match_date"]].groupby(["player", "archive"]).count().sort_values(by=["archive", "match_date"]).rename(columns={"match_date":"round_count"}).reset_index()
    count_names = count_names.merge(count_archives, how="left", on=["archive"])
    count_names["%"] = count_names["round_count"]/count_names["archive_count"]
    players_all = players_all.merge(count_names, how = "left", on=["player", "archive"])
    players_all = players_all[players_all["%"]>0.005]
    
    #same_files = players_all.groupby(["player","file","osp_guid"]).count()["submitter"]
    #same_files = same_files[same_files.ge(2)]
    players_all.drop_duplicates(["player","file","osp_guid"], keep="first", inplace=True)
    #same_files = osp.groupby(["OSP_Player","osp_guid","OSP_Damage_Given", "OSP_Damage_Received"]).count()["match_date"]
    #same_files = osp.groupby(["OSP_Player","osp_guid"]).count()["match_date"]
    #same_files = same_files[same_files.ge(2)]
    osp.drop_duplicates(["OSP_Player","osp_guid"], keep="first", inplace=True) #this does not account for 2 people with the same names, but fuck them anyway
    
    num_players = osp.groupby("osp_guid").count()["OSP_Player"]
    guids = num_players[num_players.le(5)].index
    drop_osp_idx = osp[osp["osp_guid"].isin(guids)].index
    drop_osp_idx = players_all[players_all["osp_guid"].isin(guids)].index
    small_games = osp[osp["osp_guid"].isin(guids)].sort_values(by="osp_guid").head(100)
    osp.drop(drop_osp_idx, axis = 0, inplace=True)
    players_all.drop(drop_osp_idx, axis = 0, inplace=True)
    
    

    renames = {
            'conscious*' : "conscious",
            '-*-doNka' : "donka", 
            '-doNka-'  : "donka",
            '[:X]   doNka'  : "donka",
            'Lunatic ????' : "luna",
            "i'doNka" : "donka",
            "SOURCE" : "source"
            }
    players_all["submitter"] = players_all["submitter"].replace(renames, regex=False)

    players_all["submitter2"]=players_all["submitter"]+players_all["year"]
    
    len_player = str(len(players_all))
    len_osp = str(len(osp))
    osp_player_names = len(osp["OSP_Player"].unique())
    print(f"Summarizing {len_player} individual player stats")
    print(f"Summarizing {len_osp} osp stat lines")
    print(f"OSP stats contain {osp_player_names} unique player names")
    
    mp40acc = weapon_accuracy(players_all, "MP40", 30, headshot=True)
    print(mp40acc)
    
    thomacc = weapon_accuracy(players_all, "Thompson", 30, headshot=True)
    stenacc = weapon_accuracy(players_all, "Sten", 10, headshot=True)
    
    lugeracc = weapon_accuracy(players_all, Const.WEAPON_LUGER, 30, headshot=True)
    print(lugeracc)
    
    snipeacc = weapon_accuracy(players_all, "Sniper", 10, headshot=True)
    print(snipeacc)
    grenacc = weapon_accuracy(players_all, "Grenade", 30, headshot=False)
    print(grenacc)
    panzacc = weapon_accuracy(players_all, "Panzerfaust", 30, headshot=False)
    print(panzacc)
    airacc = weapon_accuracy(players_all, "Airstrike", 30, headshot=False)
    print(airacc)
    artyacc = weapon_accuracy(players_all, "Artillery", 30, headshot=False)
    print(artyacc)
    
    
    rev = players_all[(players_all["rounds"]==2) & (players_all['Syringe_Attacks'] > 0)]
    revsum = rev.groupby(["submitter"]).agg({'Syringe_Hits':sum, 'Syringe_Attacks':sum, "player" : "count"})
    revsum.columns = ['Syringe_Hits', 'Syringe_Attacks', 'games']
    revsumfilt = revsum[revsum["games"] > 30].copy()
    revsumfilt["revpergame"] = revsumfilt['Syringe_Hits']/revsumfilt['games']
    revsumfilt["revaccuracy"] = revsumfilt['Syringe_Hits']/revsumfilt['Syringe_Attacks']
    print(revsumfilt.sort_values(by=["revpergame"], ascending=True))
    #print(revsumfilt.sort_values(by=["revaccuracy"], ascending=True))
    
    ammo = players_all[(players_all["rounds"]==2) & (players_all['AmmoDropped'] > 0)]
    ammosum = ammo.groupby(["submitter"]).agg({'AmmoGiven':sum, 'AmmoDropped':sum, "player" : "count"})
    ammosum.columns = ['AmmoGiven', 'AmmoDropped', 'games']
    ammosumfilt = ammosum[ammosum["games"] > 30].copy()
    ammosumfilt["ammopergame"] = ammosumfilt['AmmoGiven']/ammosumfilt['games']
    ammosumfilt["ammoaccuracy"] = ammosumfilt['AmmoGiven']/ammosumfilt['AmmoDropped']
    print(ammosumfilt.sort_values(by=["ammopergame"], ascending=True))
    #print(ammosumfilt.sort_values(by=["ammoaccuracy"], ascending=True))
    
    
    

    
    #osp.groupby("osp_guid").count()
    osp["match_date_date"] = pd.to_datetime(osp["match_date"], format='%Y-%m-%d %H:%M:%S', errors="raise")
    osp["year"] = osp["match_date_date"].dt.year.astype(str)
    guid = osp["osp_guid"].value_counts().sort_values().tail(1).index.values[0]
    osp[osp["osp_guid"]==guid][["OSP_Player", "OSP_Kills", "match_date"]].sort_values(by=["OSP_Player"], ascending=True)
    osp[osp["osp_guid"]==guid][["OSP_Player", "OSP_Kills", "match_date", "OSP_Team"]] \
        .groupby(["OSP_Player", "OSP_Team"]) \
        .agg({"match_date":"count"}) \
        .sort_values(by=["OSP_Player"], ascending=True)

    
    players_all[players_all["osp_guid"]==guid][["player", "match_date","archive","file"]].sort_values(by=["player"], ascending=True)
   
    players_all["accuracy"] = players_all["MP40_Hits"]/players_all["MP40_Attacks"]
    players_all["%hs"] = players_all["MP40_HeadShots"]/players_all["MP40_Hits"]
    players_all1 = players_all[players_all["MP40_Attacks"]>120]
    players_all1.plot.scatter(x='accuracy', y='%hs',style="o", s=2)
    print("75% percentile headshot ratio: ", "{:.1%}".format(players_all1['%hs'].quantile([.75]).values[0]))
    print("75% percentile accuracy: ", "{:.1%}".format(players_all1['accuracy'].quantile([.75]).values[0]))
    players_all1[players_all["accuracy"]>.5][["player","MP40_Hits","MP40_Attacks", "accuracy", "%hs"]]
    
    
    
    pd.set_option('display.max_rows', 100)
    pd.set_option("display.max_columns",20)
    pd.set_option("display.max_colwidth",25)
    pd.set_option("display.width",300)
    #print(players_all[['rounds', 'match_date', 'MP40_Accuracy', 'MP40_Hits', 'MP40_Attacks', 'MP40_HeadShots',  'AmmoGiven', 'AmmoDropped', 'Thompson_Hits', 'Thompson_Attacks', 'Thompson_Kills', 'Thompson_Deaths', 'Thompson_HeadShots', 'HealthGiven','HealthDropped', 'file', 'archive', 'osp_guid', 'player', 'submitter']])
            