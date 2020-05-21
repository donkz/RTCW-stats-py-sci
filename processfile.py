import sys
import re
import pandas as pd
import os.path
from datetime import datetime
import time as _time
import traceback
from importlib import import_module


from utils.rtcwcolors import stripColors , setup_colors
from constants.logtext import Const, LogLine
from textsci.teams import add_team_name, get_round_guid_client_log, get_round_guid_osp, get_player_list
from constants.maps import ConstMap
from collections import Counter
from textsci.matchstats import MatchStats


class StatLine:
    
    def __init__(self, round_guid, line_order, round_order,round_num, killer, event, mod, victim):
         self.round_guid=round_guid
         self.line_order=line_order
         self.round_order=round_order
         self.round_num=round_num
         self.killer=killer
         self.event=event
         self.mod=mod
         self.victim=victim
    
    def toString(self):
        vars =  [str(self.round_guid),str(self.line_order),str(self.round_order),str(self.round_num), str(self.killer),str(self.event),str(self.mod),str(self.victim)]
        return ",".join(vars)

class MatchLine:
      
    def __init__(self, file_date, match_date, file_size, round_guid, osp_guid, round_order, round_num, players, defense_hold, winner, round_time, round_diff, map_):
         self.file_date = file_date
         self.match_date = match_date
         self.file_size = file_size
         self.round_guid = round_guid
         self.osp_guid = osp_guid
         self.round_order=round_order
         self.round_num=round_num
         self.players = players
         self.defense_hold = defense_hold
         self.winner = winner
         self.round_time = round_time
         self.round_diff = round_diff
         self.map = map_

class FileProcessor:

    def __init__(self,**kwargs):
        
        self.lines = []
        self.debug_time = False
        
        if "local_file" in kwargs and ("s3bucket" in kwargs or "s3file" in kwargs):
            print("[x] Provide either local_file or s3 information (s3bucket and s3file)")
            return None
    
        if "local_file" in kwargs:
            self.local_file = kwargs.get("local_file")
            self.file_date = self.get_file_date()
            self.file_size = self.get_file_size()
            self.lines = self.get_log_lines_local()
            self.medium_agnostic_file_name = self.local_file
            
        if "debug" in kwargs:
            self.debug = kwargs.get("debug")
            if self.debug and "debug_file" in kwargs:
                self.debug_file = kwargs.get("debug_file")             
            else:
                self.debug_file = "testfile.txt"
    
        if "s3bucket" in kwargs:
            if "s3file" in kwargs:
                self.lines = self.get_log_lines_s3(kwargs.get("s3bucket"), kwargs.get("s3file"))
                self.file_date = "" #TODO: get cloud filesize and date
                self.file_size = "" #TODO: _
                self.medium_agnostic_file_name = "s3://" + kwargs.get("s3bucket") + "/" + kwargs.get("s3file")
            else:
                print("[x] You have provided s3bucket, but not s3file")
    
    
    def get_file_date(self):
        return str(datetime.fromtimestamp(os.path.getmtime(self.local_file)).strftime('%Y-%m-%d'))
    
    def get_file_size(self):
        return str(os.path.getsize(self.local_file))

    #Disassemble the following lines into a tuple of (player,statline)
    #                                Kll Dth Sui TK Eff Gib DG    DR      TD  Score
    #line = "Allies /mute doNka      19   3   0  0  86   5  2367  1435    0     48"
    #line = "Allies /mute sem        19  10   2  2  65   4  3588  2085  226     46"
    def process_OSP_line(self,line):
        tokens = re.split("\s+", line)
        if len(tokens) < 10:
            return (None, None)
        player = " ".join(tokens[1:len(tokens)-10])
        return (player, [player, tokens[0],tokens[-10],tokens[-9],tokens[-8],tokens[-7],tokens[-6],tokens[-5],tokens[-4],tokens[-3],tokens[-2],tokens[-1]])
    
    
    def get_log_lines_local(self):    
        with open(self.local_file,"r", encoding='cp1252') as file:
            lines = []
            for line in file:
                lines.append(line.rstrip())
        return lines
    
    def get_log_lines_s3(self, bucket_name, file_key):
        try:
            module = "boto3"
            boto3 = import_module(module)
        except ModuleNotFoundError:
            print("[!] Cannot find module {module}. Install it in your python environment before interacting with AWS.")
            return None
        
        s3 = boto3.client('s3')
         
        try:
            obj = s3.get_object(Bucket=bucket_name, Key=file_key)
        except s3.exceptions.ClientError as err:
            if err.response['Error']['Code'] == 'EndpointConnectionError':
                print("[!] Connection could not be established to AWS. Possible firewall or proxy issue. " + str(err))
            elif err.response['Error']['Code'] == 'ExpiredToken':
                print("[!] Credentials for AWS S3 are not valid. " + str(err))
            elif err.response['Error']['Code'] == 'AccessDenied':
                print("[!] Current credentials to not provide access to read the file. " + str(err))
            else:
                print("[!] Unexpected error: %s" % err)
            return None
            
        lines = obj['Body'].read().decode('cp1252').split('\r\n')
        
        print("[ ] FOUND LINES with rn: " + str(len(lines)))
        
        if len(lines) == 1:
            print("[!] Unusual line separators. Splitting by n")
            lines = lines[0].split('\n')
            
        return lines
    
    # Rename players in the datasets as they change their names in game
    # Params:
    # renames : dictionary of name changes
    # columns to rename
    # dataframe
    def handle_renames(self, renames, columns, df, index):
        df = df.replace(renames, regex=False)
        if index:
            #print(df.index.unique())
            #print(renames)
            df.index = df.reset_index().replace(renames, regex=False)["index"].values #because stupid regex does not work in df.rename
        return df
        
    def summarize_round_base(self, logdf):
        t1 = _time.time()
        kills = logdf[logdf["event"].isin([Const.EVENT_TEAMKILL,Const.EVENT_SUICIDE,Const.EVENT_KILL])].groupby(["killer","event"])["event"].count().unstack()
        deaths = logdf[logdf["event"].isin([Const.EVENT_TEAMKILL,Const.EVENT_SUICIDE,Const.EVENT_KILL])].groupby(["victim","event"])["event"].count().unstack()

        ################################
        # Stats collected from logs    #
        ################################
        
        #make a blank dataframe with index = playernames (anybody who killed or died)
        stats = pd.DataFrame(index = kills.append(deaths).index.unique())
        
        #add columns for kills and deaths
        stats[Const.STAT_BASE_KILL]  = kills[Const.EVENT_KILL]
        stats[Const.STAT_BASE_DEATHS]= deaths[Const.EVENT_KILL]

        #append columns for TK, TKd, SUI. There's a chance there was a round when none happened, so check first
        if(Const.EVENT_TEAMKILL in kills):
            stats[Const.STAT_BASE_TK]  = kills[Const.EVENT_TEAMKILL]
        else:
            stats[Const.STAT_BASE_TK] = 0
        
        if(Const.EVENT_TEAMKILL in deaths):
            stats[Const.STAT_BASE_TKd]= deaths[Const.EVENT_TEAMKILL]
        else:
            stats[Const.STAT_BASE_TKd]=0
        
        if(Const.EVENT_SUICIDE in deaths):
            stats[Const.STAT_BASE_SUI]= deaths[Const.EVENT_SUICIDE]
        else: 
            stats[Const.STAT_BASE_SUI] = 0
            
        #make alldeaths column = sum of all death types
        stats[Const.STAT_BASE_ALLDEATHS]= stats[Const.STAT_BASE_DEATHS].fillna(0) + stats[Const.STAT_BASE_SUI].fillna(0) + stats[Const.STAT_BASE_TKd].fillna(0)
        #print(stats[[Const.STAT_BASE_DEATHS, Const.STAT_BASE_SUI, Const.STAT_BASE_TKd, Const.STAT_BASE_ALLDEATHS]])
        
        #drop rows with empy player names and fill NaN values with 0
        if '' in stats.index.values:
            stats = stats.drop(index='') 
        stats = stats.fillna(0).astype(int)
        
        t2 = _time.time()
        if self.debug_time: print ("[t] Time to build base_stats " + str(round((t2 - t1),2)) + " s")
        return stats
    
    def summarize_round_join_osp(self, base_stats, osp_stats):
        t1 = _time.time()
        #######################################
        # Join log stats with OSP stats       #
        #######################################
        base_stats = base_stats.reset_index() #stash valid player names in "index" column
        base_stats.index = base_stats['index'].str[0:15] #because OSP names are 15 chars only
        stats_all = base_stats.join(osp_stats) #Totals fall out naturally
        stats_all.index = stats_all['index'] #go back
        del stats_all["index"]

        if False: #TODO: disabling this costly operation for now
            stats_all = add_team_name(stats_all) #adds up to 0.15s processing (200% per round)
        else:
            #trying not to break anything
            stats_all["player_strip"] = "notused"
            stats_all["team_name"] = "notused"
      
        t2 = _time.time()
        if self.debug_time: print ("[t] Time to join base and osp stats " + str(round((t2 - t1),2)) + " s")
        return stats_all
    
    def add_classes(self, logdf, stats_all):
        t1 = _time.time()
        #debug: logdf = results[0]["logs"][results[0]["logs"]["round_num"] == 1]
        #debug: stats_all = results[0]["stats"][results[0]["stats"]["round_num"] == 1]
        match_stats = MatchStats()
        pivoted_weapons = match_stats.weapon_pivot(logdf)
        
        stats_all["class"] = ""
        stats_all = stats_all.join(pivoted_weapons) #tested to be a left join, so nothing is lost
        #and if it is, it's not sttatistically significant
        
        #panzer
        allied_panzer_index =  stats_all[(stats_all[Const.STAT_OSP_SUM_TEAM] == "Allies") & (stats_all[Const.WEAPON_PANZER] > 0)][Const.WEAPON_PANZER].sort_values(ascending=False).head(1).index.values
        axis_panzer_index =    stats_all[(stats_all[Const.STAT_OSP_SUM_TEAM] == "Axis") & (stats_all[Const.WEAPON_PANZER] > 0)][Const.WEAPON_PANZER].sort_values(ascending=False).head(1).index.values
        stats_all.loc[allied_panzer_index, "class"] = Const.CLASS_PANZER
        stats_all.loc[axis_panzer_index,   "class"] = Const.CLASS_PANZER
        
        #LT
        lt_index =  stats_all[(stats_all[Const.WEAPON_AS] + stats_all[Const.WEAPON_ART]) > 0].index.values    
        stats_all.loc[lt_index, "class"] = Const.CLASS_LEUTENANT
        
        #Sniper
        sniper_index =  stats_all[stats_all[Const.WEAPON_SNIPER] > 0].index.values    
        stats_all.loc[sniper_index, "class"] = Const.CLASS_SNIPER
        
        #Flamer
        flamer_index =  stats_all[stats_all[Const.WEAPON_FLAME] > 0].index.values    
        stats_all.loc[flamer_index, "class"] = Const.CLASS_FLAMER
        
        #Venom
        venom_index =  stats_all[stats_all[Const.WEAPON_VENOM] > 0].index.values    
        stats_all.loc[venom_index, "class"] = Const.CLASS_VENOM
        
        t2 = _time.time()
        if self.debug_time: print ("[t] Time to process classes is " + str(round((t2 - t1),2)) + " s")
        return stats_all
    
    def select_time(self, osp_demo_date, osp_demo_time, osp_map_date, osp_map_time, osp_stats_date, osp_stats_time, osp_jpeg_date, osp_jpeg_time, log_date):
        if osp_demo_date is not None:
            round_datetime = osp_demo_date + " " + osp_demo_time
        elif osp_map_date is not None: 
            round_datetime = osp_map_date + " " + osp_map_time
        elif osp_stats_date is not None: 
            round_datetime = osp_stats_date + " " + osp_stats_time
        elif osp_jpeg_date is not None: 
            round_datetime = osp_jpeg_date + " " + osp_jpeg_time
        else: 
            round_datetime = log_date
        return round_datetime

    def fix_renames(self,renames):
        newdict = {}
        appended = False
        for original in renames:
            #print("\n\n\n",original," renamed to ",d[original])
            #print(newdict)
            appended = False
            if original not in newdict:
                for k1 in newdict:
                    if newdict[k1][-1] == original:
                        #print("\n------------Found " + original + " in " + ",".join(newdict[k1]))
                        newdict[k1].append(renames[original])
                        #print(newdict)
                        appended = True
                    else:
                        appended = False
                        #print("\n not Found in " + original + " in " + ",".join(newdict[k1]))
                if not appended:
                    newdict[original] = [renames[original]]
                    #print("+Started " + original)
            else:
                newdict[original] = [renames[original]] #disregard previous renames
                #print("\n++replaced " + original)
       
        #flatten dict into array
        arr = []
        for k in newdict:
            arr.append([k] + newdict[k])
       
        #exclude nicknames that are circular
        arr2 = []
        for i in arr:
            arr2.append([])
            for j in i:
                if j != i[-1]:
                    arr2[-1].append(j)
            arr2[-1].append(i[-1])
           
        #transform array back to dict for pandas the rename function
        final_dict = {}
        for i in arr2:
            for j in i[0:-1]:
                final_dict[j] = i[-1]
        return final_dict
    
    def impute_osp_variables(self, tmp_base_stats, round_time, round_number, logdf):
        #tmp_base_stats = bigresult["stats"][['Kills','Deaths','TK','Suicides']].reset_index()
        #round_time = 600
        #logdf = result["logs"]
        #logdf = logdf[logdf["round_order"]==16]
        #import random
        #test_teams = ["Axis","Allies"]
        #...random.choice(test_teams)
        
        teams = self.guess_team(logdf)
        if teams == None:
            return None
        
        tmp_base_stats = tmp_base_stats.reset_index()
        osp_rows = {}
        for index, base in tmp_base_stats.iterrows():
            STAT_OSP_SUM_PLAYER = base["index"]
            
            team = None
            try:
                team = teams[STAT_OSP_SUM_PLAYER]
            except:
                print("[!] Player's team is undetermined: " + STAT_OSP_SUM_PLAYER)
                print(teams)
            finally:
                team = team if team else "Allies" # stick them on offence
                
            STAT_OSP_SUM_TEAM = team
            STAT_OSP_SUM_FRAGS = base["Kills"]*round_number
            STAT_OSP_SUM_DEATHS = base["Deaths"]*round_number
            STAT_OSP_SUM_SUICIDES = base["Suicides"]*round_number
            STAT_OSP_SUM_TK = base["TK"]*round_number
            STAT_OSP_SUM_EFF = int(100.0*STAT_OSP_SUM_FRAGS/(STAT_OSP_SUM_FRAGS + STAT_OSP_SUM_DEATHS+1))
            STAT_OSP_SUM_GIBS = int(STAT_OSP_SUM_FRAGS*Const.EXTRAPOLATE_GIB_PER_KILL*round_number)
            STAT_OSP_SUM_DMG = int(STAT_OSP_SUM_FRAGS*Const.EXTRAPOLATE_DG_PER_KILL*round_number)
            STAT_OSP_SUM_DMR = int(STAT_OSP_SUM_DEATHS*round_number*Const.EXTRAPOLATE_DR_PER_DEATH)
            STAT_OSP_SUM_TEAMDG = int(Const.EXTRAPOLATE_TEAM_DMG_PER_SEC*round_time)
            STAT_OSP_SUM_SCORE = int(Const.EXTRAPOLATE_SCORE_PER_SEC*round_time) + base["Kills"] - base["Suicides"]*3 - base["TK"]*3
            
            osp_rows[STAT_OSP_SUM_PLAYER]=[STAT_OSP_SUM_PLAYER, STAT_OSP_SUM_TEAM, STAT_OSP_SUM_FRAGS, STAT_OSP_SUM_DEATHS, STAT_OSP_SUM_SUICIDES, STAT_OSP_SUM_TK, STAT_OSP_SUM_EFF, STAT_OSP_SUM_GIBS, STAT_OSP_SUM_DMG, STAT_OSP_SUM_DMR, STAT_OSP_SUM_TEAMDG, STAT_OSP_SUM_SCORE]
        
        ospDF = pd.DataFrame.from_dict(osp_rows, orient='index', columns=Const.osp_columns)
        return ospDF
    
    def guess_team(self, logdf):
        #test
        #logdf = result["logs"]
        #logdf = logdf[logdf["round_order"]==35]
        #test
        
#        match_stats = MatchStats()
#        pivoted_weapons = match_stats.weapon_pivot(logdf)
#        pivoted_weapons["Allies"] =  pivoted_weapons[Const.WEAPON_THOMPSON] + pivoted_weapons[Const.WEAPON_COLT]
#        pivoted_weapons["Axis"] =  pivoted_weapons[Const.WEAPON_MP40] + pivoted_weapons[Const.WEAPON_LUGER]
#        pivoted_weapons = pivoted_weapons[pivoted_weapons.columns[-2:]]
        
        kills = logdf[logdf["event"].isin(["kill","Team kill"])][['event', 'killer', 'mod', 'victim']]
        kills["count"]=1
        kills["WeaponSide"] = kills["mod"].replace("MP40","-1").replace("Luger","-100").replace("Thompson","4").replace("Colt","100")
        kills["WeaponSide"] = pd.to_numeric(kills["WeaponSide"], errors='coerce').fillna(0).astype(int)
        kills.drop(["mod"], axis=1, inplace=True)
        kills = kills.groupby(['event', 'killer', 'victim']).sum().reset_index().sort_values("count", ascending = False)
                
        player0 = kills[["killer","count"]].groupby("killer").sum().sort_values("count", ascending=False).index.values[0]
        
        kills.loc[kills[(kills["killer"]==player0) & (kills["event"]=="kill")].index,"VicTeam"] = "B"
        kills.loc[kills[(kills["killer"]==player0) & (kills["event"]=="Team kill")].index,"VicTeam"] = "A"
        kills.loc[kills[(kills["killer"]==player0) & (kills["event"]=="kill")].index,"KilTeam"] = "A"
        kills.loc[kills[(kills["killer"]==player0) & (kills["event"]=="Team kill")].index,"KilTeam"] = "B"
        
        for x in range(5): # 2 works. 5 is safer
            teamB = kills[kills["VicTeam"]=="B"]["victim"].unique()        
            for p in teamB:
                kills.loc[kills[(kills["killer"]==p) & (kills["event"]=="kill")].index,"VicTeam"] = "A"
                kills.loc[kills[(kills["killer"]==p) & (kills["event"]=="kill")].index,"KilTeam"] = "B"
                       
                kills.loc[kills[(kills["killer"]==p) & (kills["event"]=="Team kill")].index,"KilTeam"] = "B"
                
                kills.loc[kills[(kills["victim"]==p) & (kills["event"]=="kill")].index,"KilTeam"] = "A"

            
            teamA = kills[kills["KilTeam"]=="A"]["killer"].unique() 
            for p in teamA:
                kills.loc[kills[(kills["killer"]==p) & (kills["event"]=="kill")].index,"VicTeam"] = "B"
                kills.loc[kills[(kills["killer"]==p) & (kills["event"]=="kill")].index,"KilTeam"] = "A"
                
                kills.loc[kills[(kills["killer"]==p) & (kills["event"]=="Team kill")].index,"KilTeam"] = "A"   

                kills.loc[kills[(kills["victim"]==p) & (kills["event"]=="kill")].index,"KilTeam"] = "B"
        
        #plug holes
        kills.loc[kills[(kills["KilTeam"]=="A") & (kills["event"]=="kill")].index,"VicTeam"] = "B"
        kills.loc[kills[(kills["KilTeam"]=="A") & (kills["event"]=="Team kill")].index,"VicTeam"] = "A"
        kills.loc[kills[(kills["KilTeam"]=="B") & (kills["event"]=="kill")].index,"VicTeam"] = "A"
        kills.loc[kills[(kills["KilTeam"]=="B") & (kills["event"]=="Team kill")].index,"VicTeam"] = "B"
        
        
        playersraw = kills[["killer","KilTeam"]].rename(columns={"killer": "player", "KilTeam": "Team"}).append(kills[["victim","VicTeam"]].rename(columns={"victim": "player", "VicTeam": "Team"}))
        players = playersraw.groupby(["player","Team"]).size().reset_index()
        players.drop(players.columns[-1], axis=1, inplace=True)
        players.index = players["Team"]
        teams = kills[['WeaponSide', 'VicTeam']].groupby("VicTeam").sum()
        res = players.join(teams)
        res.loc[res[res["WeaponSide"] == res["WeaponSide"].min()].index,"TeamName"] = "Axis"
        res.loc[res[res["WeaponSide"] == res["WeaponSide"].max()].index,"TeamName"] = "Allies"
        res.index = res["player"]
        
        if res["TeamName"].nunique() < 2: 
            print("[!] Could not guess teams while imputing variables. Skipping this round")
            return None
        
        return res["TeamName"].to_dict()
    
    def process_log(self):
        """ 
        The constructor for ComplexNumber class. 
  
        Parameters: 
           real (int): The real part of complex number. 
           imag (int): The imaginary part of complex number.    
        """
        result = {}
        try:
            result = self.process_log_worker()
        except:
            print(f"[x] Failed to process {self.medium_agnostic_file_name} with the following error:\n\n")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
            limit=4, file=sys.stdout)
        return result     
        
    def process_log_worker(self):
        time_start_process_log = _time.time()
        #Initialize local variables
        line_order = 0
        round_order = 0
        round_num = 1
        game_started = False
        game_paused = False
        game_finished = False
        reading_osp_stats = False
        line_num = 0
        matches = []
        osp_lines = []
        log_date = None
        osp_map_date = osp_map_time = osp_demo_time = osp_jpeg_date = osp_demo_date = osp_jpeg_time= osp_stats_date = osp_stats_time = None
        
        tmp_r1_fullhold = None
        last_known_map = None
        
        
        tmp_log_events = []
        renames = {}
        line_event = "Nothing"
        
        #Load in Constants
        colors = setup_colors()
        log_lines = LogLine.LoadLogLines()
        
        #Load in map constants
        map_class = ConstMap
        map_class.load_maps(map_class)
        announcements = map_class.transpose_by_obj(map_class)
        map_counter = Counter()
    
        #Prep debug log
        if self.debug:
            try:
                debug_log = open(self.debug_file,"w")
            except:
                print("[!] Cannot write to the debug file. Is it already open? File: " + self.debug_file)
            debug_log.write("line".ljust(5) + "roundNum " + "##".ljust(2)  + "Event".ljust(20) + "Action".ljust(10) + "LineText".rstrip() + "\n")
        
        if self.lines is None:
            print("[!] No lines have been returned from the data source.")
            return None
        #################################
        ###  Start processing lines    ##
        #################################
        #go through each line in the file
        for i, val in enumerate(self.lines):
            #strip color coding
            line = stripColors(val, colors)       
            #init loop variables
            stat_entry = None
            osp_line_processed = False
            
            #for that line loop through all possible log line types and see which type of line it is
            for key, value in log_lines.items():
                                
                x = re.search(value.regex, line)
                #if it looks like something we recognize (x is not None) then add this line appropriately
                if x:
                    
#                    if "Allies" in value.regex and "Allies" in line:
#                        print("Comparing")
#                        print(value.regex)
#                        print(line)
#                        print("Result")
#                        print(x[0])
                    
                    
                    line_event = value.event
                    line_order = line_order + 1
                    
                    #player renames in game. Store old and new name in doct for later processing
                    if value.event == Const.EVENT_RENAME:
                        renames[x[1]] = x[2]
                        break
                    
                    #beginning of every logfile
                    if value.event == Const.EVENT_LOGFILE_TIMESTAMP: 
                        log_date = str(datetime.strptime(x[1].strip(), "%a %b %d %H:%M:%S %Y" )) #Sun Apr 08 18:51:44 2018
                        break
                    
                    #Match starting...recording to demos/2019-10-24/214736-donka-mp_ice.dm_60.
                    if value.event == Const.EVENT_DATETIME_DEMO:
                        osp_demo_date = x[1].split("/")[1]
                        temp_time = x[1].split("/")[2].split("-")[0]
                        osp_demo_time = temp_time[0:2] + ":" + temp_time[2:4] + ":" + temp_time[4:6]
                        break
                    
                    #[skipnotify]Current time: 20:54:01 (24 Oct 2019)
                    #x[1] = '20:54:01 (24 Oct 2019)'
                    if value.event == Const.EVENT_DATETIME_OSP_MAP_LOAD:
                        osp_map_date = datetime.strptime(x[1].split("(")[1].split(")")[0], "%d %b %Y" ).strftime("%Y-%m-%d")
                        osp_map_time = x[1].split(" ")[0]
                        break
                    
                    #Wrote screenshots/2019-10-24/215503-donka-mp_ice.jpg
                    #x[1] = '2019-10-24'
                    #x[2] = '215503-donka-mp_ice.jpg'
                    if value.event == Const.EVENT_DATETIME_SCREENSHOT:
                        osp_jpeg_date = x[1]
                        time_name_map = x[2]
                        osp_jpeg_time = time_name_map[0:2] + ":" + time_name_map[2:4] + ":" + time_name_map[4:6]          
                        break
                    
                    #^3>>> Stats recorded to: ^7stats/2019.10.24/215502.txt
                    #x[1] = 'stats/2019.10.24/215502.txt'
                    if value.event == Const.EVENT_DATETIME_OSP_SAVE_STATS:
                        osp_stats_date = x[1].split("/")[1].replace(".","-")
                        temp_time = x[1].split("/")[2][0:6]
                        osp_stats_time = temp_time[0:2] + ":" + temp_time[2:4] + ":" + temp_time[4:6]
                        break
                    
                    #FIGHT!
                    if value.event == Const.EVENT_START:
                        round_start_time = _time.time()
                        if game_paused:
                            game_paused = False
                        else:
                            if (game_started): #round aborted or otherwise interrupted
                                tmp_log_events = []                        
                            game_started = True
                            game_finished = False
                            round_order = round_order + 1
                            osp_stats_dict = {}
                            tmp_log_events = []
                            tmp_stats_all = []
                            map_counter = Counter() #reset it
                            
                            #start new match class
                            new_match_line = MatchLine(self.file_date,   # date of file creation
                                                       None,    # date from the text of the log itself
                                                       self.file_size,   # file size
                                                       "new_guid",  # match guid - processed at the end
                                                       "osp_guid",  # osp stats guid - processed at the end
                                                       round_order, # order of the round in the log file
                                                       None,        # round num 1 or 2 (first or final) - processed at the end
                                                       None,        # players - processed at the end
                                                       None,        # defence hold - processed at the end
                                                       None,        # winner - processed at the end
                                                       None,        # round time - processed at the end
                                                       None,        # round difference - processed at the end
                                                       None)        # map - processed at the end
                        break
                    
                    #game paused. Unpause will result in FIGHT line again                    
                    if game_started and value.event == Const.EVENT_PAUSE: 
                        game_paused = True
                        break
                    
                    #Accuracy info for: /mute doNka (2 Rounds)
                    if game_started and value.event == Const.EVENT_OSP_STATS_ACCURACY: #happens at the end of every round for a player that is ON A TEAM
                        new_match_line.round_num = int(line.split("(")[-1].split(" ")[0])
                        break
                    
                    #^7TEAM   Player          Kll Dth Sui TK Eff ^3Gib^7    ^2DG    ^1DR   ^6TD  ^3Score
                    if game_started and value.event == Const.EVENT_OSP_STATS_START and reading_osp_stats == False:
                        reading_osp_stats = True
                        break
                    
                    #^4Allies^7 ^5Totals           49  70  14  2^5  41^3  27^2 10969^1 12154^6  197^3     48
                    if value.event == Const.EVENT_OSP_STATS_END:
                        if game_started:
                            reading_osp_stats = False
                            osp_guid = get_round_guid_osp(osp_lines)
                            #print("Processing OSP stats id: " + osp_guid)
                            #print("Osp stats for guid calculation. Round: " + str(round_order))
                            #print(*osp_lines, sep = "\n")
                            osp_lines = []
                        else:
                            if game_finished:
                                print("[!] Processing OSP stats after OSP objective time string. This should never* happen")
                            else:
                                print("[!] Ignoring OSP stats because log of the first round is incomplete")
                        break
                    
                    #^1Axis^7   ^5Totals           59  67  20  3^5  46^3  22^2 12154^1 10969^6  844^3     32
                    if game_started and value.event == Const.EVENT_OSP_STATS_MID:
                        #do nothing for this line
                        break
                    
                    #^1Axis^7   ^7Fister Miagi   ^3   7  12   1  1^7  36^3   1^2  1305^1  1917^6  123^3      6
                    #^4Allies^7 ^7bru            ^3   7  16   0  0^7  30^3   2^2  1442^1  2840^6    0^3     11
                    if value.event == Const.EVENT_OSP_STATS_ALLIES or value.event == Const.EVENT_OSP_STATS_AXIS: #OSP team stats per player
                        if game_started:
                            osp_player, osp_line = self.process_OSP_line(line)
                            if osp_line is None: #someone echoes "Axis" ... thx Cliffdark
                                break
                            osp_stats_dict[osp_player] = osp_line
                            osp_lines.append(line.strip())   
                            osp_line_processed = True
                        break
                    
                    #^\[skipnotify\]Timelimit hit\.
                    if game_started and value.event == Const.EVENT_MAIN_TIMELIMIT: #happens before OSP stats if the time ran out
                        #game_started = False # we still have OSP stats to process
                        game_finished = True
                        new_match_line.defense_hold = 1
                        # implement timelimit hit. It appears before OSP stats only when clock ran out
                        break
                    
                    #[skipnotify]Server: timelimit changed to 3.347367                       
                    #if value.event == Const.EVENT_MAIN_SERVER_TIME:  #this can be invoked anytime by rcon or ref or map restart
                        #happens after OSP stats, but not when map changes
                        #also happens anytime ref changes timelimit 
                        #game_started = False
                        #game_finished = True
                        #new_match_line.round_time = int(float(x[1])*60) # this comes after OSP stats and fucks everything up
                        #break
                    
                    #[skipnotify]>>> ^3Objective reached at 1:36 (original: 6:49)
                    if game_started and value.event == Const.EVENT_OSP_REACHED: #osp round 2 defense lost
                        game_started = False
                        game_finished = True
                        new_match_line.defense_hold = 0
                        time1 = x[1].strip().split(":")
                        round_time = int(time1[0])*60 + int(time1[1])
                        #print("round 2 time is " + str(roundtime))
                        time2 = x[2].strip().split(":")
                        round_diff = int(time2[0])*60 + int(time2[1]) - round_time
                        
                        new_match_line.round_time = round_time 
                        new_match_line.round_diff = round_diff
                        #print("round times(t1,t2,diff) " + x[1].strip() + " " + x[2].strip() + " " + str(new_match_line.round_diff))
                        new_match_line.round_num = 2
                        #break # do not
                    
                    #[skipnotify]>>> ^3Objective NOT reached in time (3:20)
                    if game_started and value.event == Const.EVENT_OSP_NOT_REACHED: #osp round 2 defense lost
                        game_started = False
                        game_finished = True
                        time = x[1].strip().split(":")
                        
                        round_time = int(time[0])*60 + int(time[1])
                        round_diff = 0
                        
                        new_match_line.defense_hold = 1
                        new_match_line.round_num = 2
                        new_match_line.round_time = round_time
                        new_match_line.round_diff = round_diff
                        #break # do not
                    
                    #Always Round 1
                    #[skipnotify]>>> Clock set to: 10:00
                    #[skipnotify]>>> Clock set to: 6:56
                    if game_started and value.event == Const.EVENT_OSP_TIME_SET: #osp round 1 end.
                        game_started = False
                        game_finished = True
                        
                        if (new_match_line.defense_hold != 1): #do we know that it was fullhold from "Timelimit hit"?
                            new_match_line.defense_hold = 0
                        
                        #Get time from that line
                        time = x[1].strip().split(":")
                        round_time = int(time[0])*60 + int(time[1])
                        new_match_line.round_time = round_time
                        
                        new_match_line.round_num = 1
                        #TEMP_STORAGE
                        #tmp_r1_time = new_match_line.round_time
                        tmp_r1_fullhold = new_match_line.defense_hold
                        #break # do not
                    
                    if value.event == Const.CONSOLE_PASSWORD_RCON or (value.event == Const.CONSOLE_PASSWORD_REF and x[1].strip().split(" ")[0] not in Const.REF_COMMANDS) or value.event == Const.CONSOLE_PASSWORD_SERVER:
                        print("[!] Log contains sensitive information! Edit the log before sharing!")
                        print(line)
                        
                    
                    ######################################################################
                    #####################wrap up the round################################
                    ######################################################################
                    if game_finished and (value.event == Const.EVENT_OSP_REACHED or value.event == Const.EVENT_OSP_NOT_REACHED or value.event == Const.EVENT_OSP_TIME_SET):
                        round_end_time = wrap_start_time = _time.time()                       
                        #Determine the map                        
                        del map_counter["anymap"]
                        if(len(map_counter) > 1):
                            print("[!] Multiple objectives related to maps: " + str(dict(map_counter)))
                        
                        if(len(map_counter) == 0):
                            map_code = None
                            if last_known_map:
                                map_code = last_known_map
                                tmp_map = map_class.maps[map_code]
                                print("[!] No current map information found. Assumed the map is previous: " + last_known_map)
                            else:
                                map_name = "No info"
                                tmp_map = map_class.maps["anymap"]
                        elif(map_counter.most_common(1)[0][0] == "Not listed"):
                            map_code = None
                            map_name = "Not listed"
                            tmp_map = map_class.maps["anymap"]
                        else:
                            map_code = map_counter.most_common(1)[0][0]
                            tmp_map = map_class.maps[map_code]
                            last_known_map = map_code
                            map_name = tmp_map.name
                            
                        #round up all events and join them with OSP
                        tmp_logdf = pd.DataFrame([vars(e) for e in tmp_log_events])

                        
                        tmp_base_stats = self.summarize_round_base(tmp_logdf)
                        
                        if len(osp_stats_dict) == 0:
                            print ("[!] Missing OSP stats. Imputing variables.")
                            # TODO: impute individual missing players
                            #break
                            osp_guid = "imputed"
                            ospDF = self.impute_osp_variables(tmp_base_stats, round_time, new_match_line.round_num, tmp_logdf)
                        else:
                            ospDF = pd.DataFrame.from_dict(osp_stats_dict, orient='index', columns = Const.osp_columns)
                        
                        if ospDF is None:
                            break
                        
                        tmp_stats_all = self.summarize_round_join_osp(tmp_base_stats, ospDF)
                        tmp_stats_all = self.add_classes(tmp_logdf,tmp_stats_all)
                        tmp_stats_all["round_order"] = round_order

                        round_guid = get_round_guid_client_log(tmp_stats_all)

                        tmp_stats_all["round_guid"] = round_guid
                        tmp_stats_all["osp_guid"] = osp_guid
                        tmp_stats_all["round_num"] = new_match_line.round_num
                        
                        tmp_stats_all["map"] = map_name
                        new_match_line.map = map_name 
                        
                        #Recalculated scores (substract kills and suicides)
                        tmp_stats_all[Const.STAT_POST_ADJSCORE] = tmp_stats_all[Const.STAT_OSP_SUM_SCORE].fillna(0).astype(int) - tmp_stats_all[Const.STAT_BASE_KILL].fillna(0).astype(int) + tmp_stats_all[Const.STAT_BASE_SUI].fillna(0).astype(int)*3 + tmp_stats_all[Const.STAT_BASE_TK].fillna(0).astype(int)*3
                        #some OSP scores are incorrect and end up having ADJ score -1. Fix them
                        #debug line: stats[[Const.STAT_POST_ADJSCORE,Const.STAT_OSP_SUM_SCORE,Const.STAT_BASE_KILL,Const.STAT_BASE_SUI,Const.STAT_BASE_TK]].sort_values(by=[Const.STAT_POST_ADJSCORE,Const.STAT_OSP_SUM_SCORE])
                        tmp_stats_all.loc[tmp_stats_all[tmp_stats_all[Const.STAT_POST_ADJSCORE] < 0].index, Const.STAT_POST_ADJSCORE] = 0
                        
                        #Crossreference maps data and determine if current team (axis or allies) is offense or defence
                        tmp_stats_all.loc[tmp_stats_all[tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == tmp_map.defense].index,"side"] = "Defense"
                        tmp_stats_all.loc[tmp_stats_all[tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == tmp_map.offense].index,"side"] = "Offense"
                        
                        #If side is not populated with allies and axis don't do this logic
                        if(tmp_stats_all["side"].isnull().sum() == len(tmp_stats_all)):
                            #print(tmp_stats_all[["side",Const.STAT_BASE_KILLER,Const.STAT_OSP_SUM_TEAM]])
                            #IF OSP Stats are not joined (player is spectator)
                            #THEN there is no information about SIDE(Offense/Defense) or TEAM(Allies/Axis)
                            print("[!] No teams found. OSP stats not joined for round " + str(tmp_stats_all["round_order"].min()))
                        else: 
                            new_match_line.players = get_player_list(tmp_stats_all)
                                            
                        #wrap up round one only
                        if value.event == Const.EVENT_OSP_TIME_SET:
                            #round 1. Time set is not indicative of win or loss. It could be set in result of a cap(5:33) or result of hold(10:00)
                            round_diff = tmp_map.timelimit*60 - new_match_line.round_time
                            new_match_line.round_diff = round_diff
                            tmp_stats_all.loc[tmp_stats_all[tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == tmp_map.offense].index,"round_win"] = 1 - new_match_line.defense_hold
                            tmp_stats_all.loc[tmp_stats_all[tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == tmp_map.defense].index,"round_win"] = new_match_line.defense_hold
                            tmp_stats_all["game_result"] = "R1MSB"
                            if int(tmp_map.timelimit*60) == int(new_match_line.round_time):
                                new_match_line.winner = tmp_map.defense
                            else:
                                new_match_line.winner = tmp_map.offense
                        
                        #wrap up round two only 
                        if value.event == Const.EVENT_OSP_NOT_REACHED:
                            #round 2 DEFENSE HELD (WON OR DRAW)
                            if tmp_r1_fullhold is None:
                                tmp_r1_fullhold = 0
                            if tmp_r1_fullhold == 1:
                                tmp_stats_all.loc[tmp_stats_all[tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == tmp_map.offense].index,"round_win"] = 0 
                                tmp_stats_all.loc[tmp_stats_all[tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == tmp_map.defense].index,"round_win"] = 1 #they get a round win , but a game win is full hold
                                tmp_stats_all["game_result"] = "FULLHOLD"
                                #new_match_line.winner = "Draw"
                                new_match_line.winner = tmp_map.defense
                            elif tmp_r1_fullhold == 0:
                                tmp_stats_all.loc[tmp_stats_all[tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == tmp_map.offense].index,"round_win"] = 0 
                                tmp_stats_all.loc[tmp_stats_all[tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == tmp_map.defense].index,"round_win"] = 1
                                tmp_stats_all.loc[tmp_stats_all[tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == tmp_map.defense].index,"game_result"] = "WON"
                                tmp_stats_all.loc[tmp_stats_all[tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == tmp_map.offense].index,"game_result"] = "LOST"
                                new_match_line.winner = tmp_map.defense
                            else:
                                print("[!] Bad round 2 winner status for round #" + str(round_order) + " map: " + map_name)

                        #wrap up round two only     
                        if value.event == Const.EVENT_OSP_REACHED:
                            #round 2 DEFENSE LOST THE GAME
                            tmp_stats_all.loc[tmp_stats_all[tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == tmp_map.offense].index,"round_win"] = 1 
                            tmp_stats_all.loc[tmp_stats_all[tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == tmp_map.defense].index,"round_win"] = 0 
                            tmp_stats_all.loc[tmp_stats_all[tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == tmp_map.defense].index,"game_result"] = "LOST"
                            tmp_stats_all.loc[tmp_stats_all[tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == tmp_map.offense].index,"game_result"] = "WON"
                            new_match_line.winner = tmp_map.offense
                            #del tmp_r1_fullhold
                        
                        #print("Thinking offence team is " + tmp_map.offense)
                        #print("Thinking defence team is " + tmp_map.defense)
                        #print(tmp_stats_all.sort_values(Const.STAT_OSP_SUM_TEAM)[[Const.STAT_OSP_SUM_PLAYER,Const.STAT_OSP_SUM_TEAM,"round_num","round_win","game_result", "map"]])      
                        
                        tmp_logdf["round_num"] = new_match_line.round_num
                        tmp_logdf["round_guid"] = round_guid
                        tmp_stats_all["round_diff"] = round_diff
                        tmp_stats_all["round_time"] = round_time
                        
                        new_match_line.round_guid = round_guid
                        new_match_line.osp_guid = osp_guid
                        

                        round_datetime = self.select_time(osp_demo_date, osp_demo_time, osp_map_date, osp_map_time, osp_stats_date, osp_stats_time, osp_jpeg_date, osp_jpeg_time, log_date)
                        new_match_line.match_date = round_datetime
                        tmp_stats_all[Const.NEW_COL_MATCH_DATE] = round_datetime
                        
                        
                        matches.append(new_match_line)
                       
                        #append event log and stats sum to the match dataframe
                        try:
                            logdf
                        except NameError:
                            logdf = tmp_logdf
                        else:
                            logdf = logdf.append(tmp_logdf,sort=False)
                            
                        try:
                            stats_all
                        except NameError:
                            stats_all = tmp_stats_all
                        else:
                            stats_all = stats_all.append(tmp_stats_all,sort=False)

                        wrap_end_time = _time.time()  
                        print("[ ] Proccessed round " + str(new_match_line.round_order).ljust(2) + " winner " + new_match_line.winner.ljust(6) + " on " + new_match_line.map[0:10].ljust(11) + ". Events: " + str(len(tmp_logdf)).ljust(6) + ". Players: " + str(len(tmp_stats_all)).ljust(2) + "(Linestime: " + str(round((round_end_time - round_start_time),2)) + " s " + "Wraptime: " + str(round((wrap_end_time - wrap_start_time),2)) + " s)")
                        
                        ######################################################################
                        ##############END of wrap up the round################################
                        ######################################################################
                        
                   
                    
                    #something was matched at this point
                    #IF the line relates to stats (kills, suicides, etc), write a stat_entry
                    #ELSE go through objective checks and write an objective entry
                    if not game_finished and game_started and value.stats:
                        if len(x.groups()) > 0:
                            victim = x[1]
                        else: 
                            victim = ""
                        if len(x.groups()) > 1:
                            killer = x[2]
                        else: 
                            killer = ""
                        stat_entry = StatLine("temp",line_order, round_order,round_num,killer,value.event, value.mod, victim)
                    elif not game_finished and game_started and value.event == Const.EVENT_OBJECTIVE:
                        #insert processing here for who and what
                        #print(str(type(x[1])) + " : " + x[1])
                        if(x[1] in announcements):   
                            announcement_values = announcements[x[1]]
                            map_info= map_class.maps[announcement_values[1]]  
                            obj_offender = map_info.offense
                            obj_defender = map_info.defense
                            obj_type = announcement_values[0]
                            if ("Allies transmitted the documents!" not in x[1] and "Forward Bunker" not in x[1] and "Dynamite planted near the Service Door!" not in x[1]):
                                #Frostbite and beach same objectives
                                #Delivery and beach same objectives
                                map_counter[map_info.code] +=1
                            #print("Known objective: ".ljust(20) + x[1] + " map: " + map_info.name)
                            stat_entry = StatLine("temp",line_order, round_order,round_num,obj_offender,"Objective", obj_type, obj_defender)
                        else:
                            if ("the War Documents" in x[1]):
                                "This objective repeats in various maps so we are going to skip it"
                            elif ("Axis have returned the objective!" in x[1]):
                                "Generic message, skip it"
                            elif ("Allies have returned the objective!" in x[1]):
                                "Generic message, skip it"
                            else:
                                print("[!] -----------Unknown objective: ".ljust(20) + x[1])
                                map_counter["Not listed"] +=1
                    else:
                        stat_entry = None
                    break
            
            
            #if did not match any regex    
            else:
                #did not match any lines
                line_event = "Nothing"
                #bad panzer special handling
                y = re.search("^\[skipnotify\](.*) was killed by (.*)",line)  
                if not game_finished and y:
                    value.event = Const.EVENT_KILL
                    stat_entry = StatLine("temp",line_order, round_order,1,y[2],value.event, Const.WEAPON_PANZER, y[1])
                    line_event = "Bad panzer"
                    #print("Bad console line: " + line + "--- processed as " + stat_entry.toString())
                #end of bad panzer handling
            
            if stat_entry:
                processedLine = "Logged" 
                tmp_log_events.append(stat_entry)
                line_num = line_num + 1
            elif osp_line_processed:
                processedLine = "Osp added"
            elif x:
                processedLine = "Processed"
            else:
                #
                processedLine = "Ignored"
           
            #write the line processing notes into the debig file
            write_line = str(line_order).ljust(5) + "roundNum " + str(round_order).ljust(3)  + line_event.ljust(20) + processedLine.ljust(10) + line.rstrip() + "\n"
            if self.debug:
                debug_log.write(write_line)
        
        #close debig file        
        if self.debug:
            debug_log.close() 
        
        #logdf = pd.DataFrame([vars(e) for e in log_events])
        #print(matches[1].round_diff)
        #print([vars(e) for e in matches])
        
        try:
            matches
            logdf
            stats_all
            renames
        except NameError:
            print("[x] Nothing was processed")
            exit()
            return None
        else:
            try:
                fixed_renames = self.fix_renames(renames)
            except:
                fixed_renames = renames
                print("[!] fix_renames did not work for dictionary")
                print(renames)
                
            matchesdf = pd.DataFrame([vars(e) for e in matches])
            logdf = self.handle_renames(fixed_renames, ["killer","victim"], logdf, False)
            stats_all = self.handle_renames(fixed_renames, ['player_strip','Killer','team_captain','OSP_Player'], stats_all, True)            
            logdf = logdf[['round_guid','line_order','round_order','round_num','event','killer','mod','victim']]
            
            if(len(renames) > 0):
                renameDF = pd.DataFrame.from_dict(renames, orient='index').reset_index()
                renameDF.columns = ["original","renamed_to"]
            else:
                renameDF = None
            
            time_end_process_log = _time.time()
            print ("[ ] File processed " + self.medium_agnostic_file_name + ". Total time is " + str(round((time_end_process_log - time_start_process_log),2)) + " s")
            return {"logs":logdf, "stats":stats_all, "matches":matchesdf, "renames" : renameDF}
            
        
        
