import sys
import re
import pandas as pd
import os.path
from datetime import datetime
import time as _time
import traceback
from importlib import import_module
from collections import Counter


from rtcwlog.utils.rtcwcolors import stripColors, setup_colors
from rtcwlog.utils.ospstrings import process_OSP_line, process_pro_line, osp_token_one_slash_two, osp_token_accuracy_playername_round
from rtcwlog.constants.logtext import Const, LogLine
from rtcwlog.constants.const_osp import ConstOsp, OSPFileLine
from rtcwlog.textsci.teams import add_team_name, get_round_guid_client_log, get_player_list, guess_team
from rtcwlog.utils.ospstrings import get_round_guid_osp, build_player_df
from rtcwlog.constants.maps import ConstMap

from rtcwlog.report.matchstats import MatchStats


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
      
    def __init__(self, file_name, file_date, match_date, file_size, round_guid, osp_guid, round_order, round_num, players, defense_hold, winner, round_time, round_diff, map_):
         self.file_name = file_name
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

class Round:
      
    def __init__(self, round_order):
         self.round_order = round_order
         self.tmp_log_events = []
         self.stats_lines = []
         self.round_num = 1
         self.game_started = False
         self.game_paused = False
         self.game_finished = False
         self.game_happened = False
         self.stats_dict = {}
         self.tmp_stats_all = None
         self.map_counter = Counter()
         self.obj_counter = Counter()
         self.map_info = None
         self.defense_hold = None
         self.round_time = None
         self.round_diff = None
         self.round_guid = None
         self.osp_guid = None
         self.round_datetime = None
         self.winner = None
         self.osp_jpeg_date = None
         self.osp_jpeg_time = None
         self.osp_stats_date = None
         self.osp_stats_time = None
         self.round_start_time = None
         self.round_end_time = None
         self.exact_map_ss = None
         self.exact_map_load = None
         self.player_stats = {}
         self.round_stats_team_line = None
         self.round_stats_confidence = 0


class ClientLogProcessor:
    
    def __init__(self,**kwargs):     
        self.lines = []
        self.debug_time = False
        self.log_date = None
        self.osp_demo_date = None
        self.osp_demo_time = None
        self.osp_map_date = None
        self.osp_map_time = None
        self.pb_players = {}
        self.renames = {}
        self.matchesdf = pd.DataFrame()
        self.logdf = pd.DataFrame()
        self.statsdf = pd.DataFrame()
        self.playersdf = pd.DataFrame()
        self.tmp_r1_fullhold = None
        self.last_known_map = None
        self.tmp_exact_map = None
        self.tmp_submitter = "UnnamedPlayer"
        self.submitter = "?"
        self.match_type = "?"
        
        if "local_file" in kwargs and ("s3bucket" in kwargs or "s3file" in kwargs):
            print("[x] Provide either local_file or s3 information (s3bucket and s3file)")
            return None
    
        if "local_file" in kwargs:
            self.local_file = kwargs.get("local_file")
            self.file_date = self.get_file_date()
            self.file_size = self.get_file_size()
            self.lines = self.get_log_lines_local()
            self.medium_agnostic_file_name = self.local_file
            self.match_type = "local"
            
        if "debug" in kwargs:
            self.debug = kwargs.get("debug")
            if self.debug and "debug_file" in kwargs:
                self.debug_file = kwargs.get("debug_file")             
            else:
                self.debug_file = "testfile.txt"
    
        if "s3bucket" in kwargs:
            if "s3file" in kwargs:
                self.lines = self.get_log_lines_s3(kwargs.get("s3bucket"), kwargs.get("s3file"))
                self.medium_agnostic_file_name = "s3://" + kwargs.get("s3bucket") + "/" + kwargs.get("s3file")
                try:
                    self.match_type = "/".join(kwargs.get("s3file").split("/")[1:3])
                except:
                    print("[!] Type could not be derived from " + kwargs.get("s3file"))
            else:
                print("[x] You have provided s3bucket, but not s3file")
    
    
    def get_file_date(self):
        return str(datetime.fromtimestamp(os.path.getmtime(self.local_file)).strftime('%Y-%m-%d'))
    
    def get_file_size(self):
        return str(os.path.getsize(self.local_file))

    
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
            print("[x] Cannot find module {module}. Install it in your python environment before interacting with AWS.")
            return None

        s3 = boto3.client('s3')
        
        try:
            obj = s3.get_object(Bucket=bucket_name, Key=file_key)
            self.file_date = obj['ResponseMetadata']['HTTPHeaders']['last-modified']
            self.file_size = obj['ResponseMetadata']['HTTPHeaders']['content-length']
        except s3.exceptions.ClientError as err:
            if err.response['Error']['Code'] == 'EndpointConnectionError':
                print("[x] Connection could not be established to AWS. Possible firewall or proxy issue. " + str(err))
            elif err.response['Error']['Code'] == 'ExpiredToken':
                print("[x] Credentials for AWS S3 are not valid. " + str(err))
            elif err.response['Error']['Code'] == 'AccessDenied':
                print("[x] Current credentials to not provide access to read the file. " + str(err))
            else:
                print("[x] Unexpected error: %s" % err)
            return None
            
        lines = obj['Body'].read().decode('cp1252').replace('\r\n','\n').split('\n')  
        print("[ ] Number of lines in the file: " + str(len(lines)))

        return lines
    
    # Rename players in the datasets as they change their names in game
    # Params:
    # renames : dictionary of name changes
    # columns to rename
    # dataframe
    def handle_renames(self, renames, columns, df, index):
        try:
            for col in columns:
                df[col] = df[col].replace(renames, regex=False)
            if index:
                #print(df.index.unique())
                #print(renames)
                df.index = df.reset_index().replace(renames, regex=False)["index"].values #because stupid regex does not work in df.rename
        except:
            print("[x] Failed to process renames: ", sys.exc_info()[0])
        return df
    
    def populate_guids(self, stats_all, pb_players, renames):
        '''
        if any pb_plist results were found, match players with their punkbuster guids
        '''
        
        if len(pb_players) > 0:
            pb_players_df = pd.DataFrame.from_dict(pb_players, orient='index')
            pb_players_df.columns = ["pb_guid"]
            pb_players_df = self.handle_renames(renames, [], pb_players_df, True)
            pb_players_df.drop_duplicates(["pb_guid"], keep="first", inplace=True)
            stats_all =  stats_all.join(pb_players_df)
        else:
            stats_all["pb_guid"] = ""
        
        return stats_all
        
    def summarize_round_base(self, logdf):
        t1 = _time.time()
        if len(logdf) == 0:
            print("[!] Nothing was logged this round")
            return None
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
        if self.debug_time: print ("[t] Time to build base_stats " + str(round((t2 - t1),3)) + " s")
        return stats
    
    def summarize_round_join_osp(self, base_stats, osp_stats):
        t1 = _time.time()
        base_stats = base_stats.reset_index() #stash valid player names in "index" column
        base_stats.index = base_stats['index'].str[0:15].str.lower() #because OSP names are 15 chars only. lower because RTCW PRO just fuckin decided we are doing this now
        
        osp_stats.index = osp_stats.index.str.lower()
        stats_all = base_stats.join(osp_stats) #Totals fall out naturally
        #print("[Debug] indexes on join\n", base_stats.index, osp_stats.index)

        stats_all.index = stats_all['index'] #go back
        del stats_all["index"]

        if False: #TODO: disabling this costly operation for now
            stats_all = add_team_name(stats_all) #adds up to 0.15s processing (200% per round)
        else:
            #trying not to break anything
            stats_all["player_strip"] = "notused"
            stats_all["team_name"] = "notused"
      
        # print("\n[Debug]\n", base_stats.loc["source","Kills"], "\n[Debug]\n", osp_stats.loc["source","OSP_Kills"])
        t2 = _time.time()
        if self.debug_time: print ("[t] Time to join base and osp stats " + str(round((t2 - t1),3)) + " s")
        return stats_all
    
    def add_classes(self, logdf, stats_all):
        t1 = _time.time()
        #debug: logdf = results[0]["logs"][results[0]["logs"]["round_num"] == 1]
        #debug: stats_all = results[0]["stats"][results[0]["stats"]["round_num"] == 1]
        match_stats = MatchStats()
        pivoted_weapons = match_stats.weapon_pivot(logdf)
        
        stats_all["class"] = ""
        stats_all = stats_all.join(pivoted_weapons).fillna(0) #tested to be a left join, so nothing is lost
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
        if self.debug_time: print ("[t] Time to process classes is " + str(round((t2 - t1),3)) + " s")
        return stats_all
    
    # TODO rethink this again
    def select_time(self, osp_demo_date, osp_demo_time, osp_map_date, osp_map_time, osp_stats_date, osp_stats_time, osp_jpeg_date, osp_jpeg_time, log_date):
        if osp_stats_date is not None: 
            round_datetime = osp_stats_date + " " + osp_stats_time
        elif osp_jpeg_date is not None: 
            round_datetime = osp_jpeg_date + " " + osp_jpeg_time
        elif osp_demo_date is not None:
            round_datetime = osp_demo_date + " " + osp_demo_time
        elif osp_map_date is not None: 
            round_datetime = osp_map_date + " " + osp_map_time
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

        # exclude nicknames that are circular
        arr2 = []
        for i in arr:
            arr2.append([])
            for j in i:
                if j != i[-1]:
                    arr2[-1].append(j)
            arr2[-1].append(i[-1])

        # transform array back to dict for pandas the rename function
        final_dict = {}
        for i in arr2:
            for j in i[0:-1]:
                final_dict[j] = i[-1]
        return final_dict

    def impute_osp_variables(self, tmp_base_stats, round_time, round_number, logdf):
        """If the OSP/Pro totals are missing, trying to fill in the gaps."""
        t1 = _time.time()
        # tmp_base_stats = bigresult["stats"][['Kills','Deaths','TK','Suicides']].reset_index()
        # round_time = 600
        # logdf = result["logs"]
        # logdf = logdf[logdf["round_order"]==16]
        # import random
        # test_teams = ["Axis","Allies"]
        # ...random.choice(test_teams)

        teams = guess_team(logdf, 4, True, self.debug_time)
        if not teams:
            return None

        tmp_base_stats = tmp_base_stats.reset_index()
        osp_rows = {}
        for index, base in tmp_base_stats.iterrows():
            STAT_OSP_SUM_PLAYER = base["index"][0:15]  # OSP Limitation

            team = None
            try:
                team = teams[base["index"]]
            except:
                print("[!] Player's team is undetermined: " + STAT_OSP_SUM_PLAYER)
                print(teams)
            finally:
                team = team if team else "Allies"  # stick them on offence

            if round_time is None:
                print("[!] Closing a round without exact round time")
                round_time = 600

            STAT_OSP_SUM_TEAM = team
            STAT_OSP_SUM_FRAGS = base["Kills"] * round_number
            STAT_OSP_SUM_DEATHS = base["Deaths"] * round_number
            STAT_OSP_SUM_SUICIDES = base["Suicides"] * round_number
            STAT_OSP_SUM_TK = base["TK"] * round_number
            STAT_OSP_SUM_EFF = int(100.0*STAT_OSP_SUM_FRAGS/(STAT_OSP_SUM_FRAGS + STAT_OSP_SUM_DEATHS+1))
            STAT_OSP_SUM_GIBS = int(STAT_OSP_SUM_FRAGS*Const.EXTRAPOLATE_GIB_PER_KILL * round_number)
            STAT_PRO_ACC = 30.0 # semi science
            STAT_PRO_HEADSHOTS = int(STAT_OSP_SUM_FRAGS*Const.EXTRAPOLATE_GIB_PER_KILL * round_number)
            STAT_OSP_SUM_DMG = int(STAT_OSP_SUM_FRAGS*Const.EXTRAPOLATE_DG_PER_KILL * round_number)
            STAT_OSP_SUM_DMR = int(STAT_OSP_SUM_DEATHS*round_number * Const.EXTRAPOLATE_DR_PER_DEATH)
            STAT_OSP_SUM_TEAMDG = int(Const.EXTRAPOLATE_TEAM_DMG_PER_SEC * round_time)
            STAT_PRO_REVIVES = int(STAT_OSP_SUM_FRAGS*Const.EXTRAPOLATE_REV * round_number)
            STAT_OSP_SUM_SCORE = int(Const.EXTRAPOLATE_SCORE_PER_SEC*round_time) + base["Kills"] - base["Suicides"]*3 - base["TK"]*3
            
            osp_rows[STAT_OSP_SUM_PLAYER]=[STAT_OSP_SUM_PLAYER, STAT_OSP_SUM_TEAM, STAT_OSP_SUM_FRAGS, STAT_OSP_SUM_DEATHS, STAT_OSP_SUM_SUICIDES, STAT_OSP_SUM_TK, STAT_OSP_SUM_EFF, STAT_OSP_SUM_GIBS, STAT_PRO_ACC, STAT_PRO_HEADSHOTS, STAT_OSP_SUM_DMG, STAT_OSP_SUM_DMR, STAT_OSP_SUM_TEAMDG, STAT_PRO_REVIVES, STAT_OSP_SUM_SCORE]
        
        ospDF = pd.DataFrame.from_dict(osp_rows, orient='index', columns=Const.stat_columns)
        t2 = _time.time()
        if self.debug_time: print ("[t] Time to impute OSP stats " + str(round((t2 - t1),3)) + " s")
        return ospDF

    def determine_current_map(self, currentRound):
        del currentRound.map_counter["anymap"]
        
        #print(currentRound.exact_map_load , currentRound.exact_map_ss)
        if currentRound.exact_map_load and (currentRound.exact_map_load == currentRound.exact_map_ss):
            try: 
                tmp_map = self.map_class.maps[currentRound.exact_map_ss.lower()]  #lower because some ppl have MP_SUB
                return tmp_map
            except KeyError:
                print("[!] Map " + currentRound.exact_map_ss + " was not found")
                
            self.last_known_map = currentRound.exact_map_ss
            
        for objective_line in currentRound.obj_counter:
            if(objective_line in self.announcements): 
                announcement_values = self.announcements[objective_line]
                map_info= self.map_class.maps[announcement_values[1]]
                if ("Allies transmitted the documents!" not in objective_line and "Forward Bunker" not in objective_line and "Dynamite planted near the Service Door!" not in objective_line):
                    #Frostbite and beach same objectives
                    #Delivery and beach same objectives
                    currentRound.map_counter[map_info.code] += currentRound.obj_counter[objective_line]
            else: #things that are not in the announcemenets
                if ("the War Documents" in objective_line):
                    "This objective repeats in various maps so we are going to skip it"
                elif ("Axis have returned the objective!" in objective_line):
                    "Generic message, skip it"
                elif ("Allies have returned the objective!" in objective_line):
                    "Generic message, skip it"
                else:
                    print("[!] -----------Unknown objective: ".ljust(20) + objective_line)
                    currentRound.map_counter["Not listed"] +=1
        
        if(len(currentRound.map_counter) > 1):
            print("[!] Multiple objectives related to maps: " + str(dict(currentRound.map_counter)))
        
        if(len(currentRound.map_counter) == 0):
            if self.last_known_map:
                map_code = self.last_known_map
                tmp_map = self.map_class.maps[map_code]
                print("[!] No current map information found. Assumed the map is previous: " + self.last_known_map)
            else:
                tmp_map = self.map_class.maps["anymap"]
                tmp_map.name = "No info"
        elif(currentRound.map_counter.most_common(1)[0][0] == "Not listed"):
            tmp_map = self.map_class.maps["anymap"]
            tmp_map.name = "Not listed"
        else:
            map_code = currentRound.map_counter.most_common(1)[0][0]
            tmp_map = self.map_class.maps[map_code]
            self.last_known_map = map_code
        return tmp_map
    
    def build_osp_stats_dataframe(self, currentRound, tmp_base_stats, tmp_logdf):
        if len(currentRound.stats_dict) == 0:
            print ("[!] Missing OSP stats. Imputing variables.")
            # TODO: impute individual missing players
            #break
            currentRound.osp_guid = "imputed"
            #print("[Debug] current round time: " + str(currentRound.round_time))
            #print("[Debug]\n", vars(currentRound))
            if currentRound.round_time is None:
                print("[!] Round did not fully report itself. Skipping.")
                return None
            ospDF = self.impute_osp_variables(tmp_base_stats, currentRound.round_time, currentRound.round_num, tmp_logdf)
        else:
            try: 
                ospDF = pd.DataFrame.from_dict(currentRound.stats_dict, orient='index', columns = Const.stat_columns)
            except:
                print(currentRound.stats_dict)
            finally:
                return ospDF
        return ospDF
    
    def determine_round_result(self,currentRound, event):
        #wrap up round one only
        if event == Const.EVENT_OSP_TIME_SET:                     
            currentRound.tmp_stats_all.loc[currentRound.tmp_stats_all[currentRound.tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == currentRound.map_info.offense].index,"round_win"] = 1 - currentRound.defense_hold
            currentRound.tmp_stats_all.loc[currentRound.tmp_stats_all[currentRound.tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == currentRound.map_info.defense].index,"round_win"] = currentRound.defense_hold
            currentRound.tmp_stats_all["game_result"] = "R1MSB"
        
        #wrap up round two not reached
        if event == Const.EVENT_OSP_NOT_REACHED:
            #round 2 DEFENSE HELD (WON OR DRAW)
            if self.tmp_r1_fullhold is None:
                self.tmp_r1_fullhold = 0
            if self.tmp_r1_fullhold == 1:
                currentRound.tmp_stats_all.loc[currentRound.tmp_stats_all[currentRound.tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == currentRound.map_info.offense].index,"round_win"] = 0 
                currentRound.tmp_stats_all.loc[currentRound.tmp_stats_all[currentRound.tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == currentRound.map_info.defense].index,"round_win"] = 1 #they get a round win , but a game win is full hold
                currentRound.tmp_stats_all["game_result"] = "FULLHOLD"
                currentRound.winner = currentRound.map_info.defense
            elif self.tmp_r1_fullhold == 0:
                currentRound.tmp_stats_all.loc[currentRound.tmp_stats_all[currentRound.tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == currentRound.map_info.offense].index,"round_win"] = 0 
                currentRound.tmp_stats_all.loc[currentRound.tmp_stats_all[currentRound.tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == currentRound.map_info.defense].index,"round_win"] = 1
                currentRound.tmp_stats_all.loc[currentRound.tmp_stats_all[currentRound.tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == currentRound.map_info.defense].index,"game_result"] = "WON"
                currentRound.tmp_stats_all.loc[currentRound.tmp_stats_all[currentRound.tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == currentRound.map_info.offense].index,"game_result"] = "LOST"
                currentRound.winner = currentRound.map_info.defense
            else:
                print("[!] Bad round 2 winner status for round #" + str(currentRound.round_order) + " map: " + currentRound.map_info.name)
        
        #wrap up round two reached   
        if event == Const.EVENT_OSP_REACHED:
            #round 2 DEFENSE LOST THE GAME
            currentRound.tmp_stats_all.loc[currentRound.tmp_stats_all[currentRound.tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == currentRound.map_info.offense].index,"round_win"] = 1 
            currentRound.tmp_stats_all.loc[currentRound.tmp_stats_all[currentRound.tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == currentRound.map_info.defense].index,"round_win"] = 0 
            currentRound.tmp_stats_all.loc[currentRound.tmp_stats_all[currentRound.tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == currentRound.map_info.defense].index,"game_result"] = "LOST"
            currentRound.tmp_stats_all.loc[currentRound.tmp_stats_all[currentRound.tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == currentRound.map_info.offense].index,"game_result"] = "WON"
            currentRound.winner = currentRound.map_info.offense
        
        #print("Thinking offence team is " + tmp_map.offense)
        #print("Thinking defence team is " + tmp_map.defense)
        #print(currentRound.tmp_stats_all.sort_values(Const.STAT_OSP_SUM_TEAM)[[Const.STAT_OSP_SUM_PLAYER,Const.STAT_OSP_SUM_TEAM,"round_num","round_win","game_result", "map"]])   
        return currentRound
    
    def build_matchdf(self, currentRound):
        #If side is not populated with allies and axis don't do this logic
        if(currentRound.tmp_stats_all["side"].isnull().sum() == len(currentRound.tmp_stats_all)):
            #print(currentRound.tmp_stats_all[["side",Const.STAT_BASE_KILLER,Const.STAT_OSP_SUM_TEAM]])
            #IF OSP Stats are not joined (player is spectator)
            #THEN there is no information about SIDE(Offense/Defense) or TEAM(Allies/Axis)
            print("[!] No teams found. OSP stats not joined for round " + str(currentRound.tmp_stats_all["round_order"].min()))
        else: 
            players = get_player_list(currentRound.tmp_stats_all)
        
        new_match_line = MatchLine(self.medium_agnostic_file_name,
                                   self.file_date,                 # date of file creation
                                   currentRound.round_datetime,    # date from the text of the log itself
                                   self.file_size,                 # file size
                                   currentRound.round_guid,        # match guid - processed at the end
                                   currentRound.osp_guid,          # osp stats guid - processed at the end
                                   currentRound.round_order,                    # order of the round in the log file
                                   currentRound.round_num,         # round num 1 or 2 (first or final) - processed at the end
                                   players,                        # players - processed at the end
                                   currentRound.defense_hold,      # defence hold - processed at the end
                                   currentRound.winner,            # winner - processed at the end
                                   currentRound.round_time,        # round time - processed at the end
                                   currentRound.round_diff,        # round difference - processed at the end
                                   currentRound.map_info.name)          # map - processed at the end
        tmp_matchdf = pd.DataFrame([vars(new_match_line)])
        return tmp_matchdf
    
    def round_close(self,currentRound):
        """ 
        Once the round is finished, close it by summarizing kills, map objectives, identity properties
  
        Parameters: 
           self (ClientLogProcessor) with match-long values
           currentRound - class of parameters extracted only for this current round
        """       
        #print("[Debug] CurrentRound contents\n",[vars(currentRound)])
        if not currentRound.game_happened:
            return None
        
        if not currentRound.game_finished:
            print("[!] Round did not finish. Aborting.")
            return None
            
        currentRound.round_end_time = wrap_start_time = _time.time() 
        if not currentRound.game_happened:
            return None                      
        currentRound.map_info = self.determine_current_map(currentRound)
            
        #round up all events and join them with OSP
        tmp_logdf = pd.DataFrame([vars(e) for e in currentRound.tmp_log_events])
        tmp_base_stats = self.summarize_round_base(tmp_logdf)
        if tmp_base_stats is None:
            return None
            
        ospDF = self.build_osp_stats_dataframe(currentRound, tmp_base_stats, tmp_logdf)   
        if ospDF is None:
            #break # TODO test this
            print("[x] Round could not be summarized, aborting this round.")
            return None
        
        cp0 = _time.time()
        if self.debug_time: print ("[t] Checkpoint0 " + str(round((cp0  - wrap_start_time),3)) + " s")
        
        currentRound.tmp_stats_all = self.summarize_round_join_osp(tmp_base_stats, ospDF)
        
        currentRound.tmp_stats_all = self.add_classes(tmp_logdf,currentRound.tmp_stats_all)
        currentRound.tmp_stats_all["round_order"] = currentRound.round_order

        currentRound.round_guid = get_round_guid_client_log(currentRound.tmp_stats_all)
        currentRound.tmp_stats_all["round_guid"] = currentRound.round_guid
        
        currentRound.tmp_stats_all["osp_guid"] = currentRound.osp_guid
        currentRound.tmp_stats_all["round_num"] = currentRound.round_num
        
        currentRound.tmp_stats_all["map"] = currentRound.map_info.name
        
        cp1 = _time.time()
        if self.debug_time: print ("[t] Checkpoint1 " + str(round((cp1  - cp0),3)) + " s")
        
        #Recalculated scores (substract kills and suicides)
        currentRound.tmp_stats_all[Const.STAT_POST_ADJSCORE] = currentRound.tmp_stats_all[Const.STAT_OSP_SUM_SCORE].fillna(0).astype(int) - currentRound.tmp_stats_all[Const.STAT_BASE_KILL].fillna(0).astype(int) + currentRound.tmp_stats_all[Const.STAT_BASE_SUI].fillna(0).astype(int)*3 + currentRound.tmp_stats_all[Const.STAT_BASE_TK].fillna(0).astype(int)*3
        #some OSP scores are incorrect and end up having ADJ score -1. Fix them
        #debug line: stats[[Const.STAT_POST_ADJSCORE,Const.STAT_OSP_SUM_SCORE,Const.STAT_BASE_KILL,Const.STAT_BASE_SUI,Const.STAT_BASE_TK]].sort_values(by=[Const.STAT_POST_ADJSCORE,Const.STAT_OSP_SUM_SCORE])
        currentRound.tmp_stats_all.loc[currentRound.tmp_stats_all[currentRound.tmp_stats_all[Const.STAT_POST_ADJSCORE] < 0].index, Const.STAT_POST_ADJSCORE] = 0
        
        #Crossreference maps data and determine if current team (axis or allies) is offense or defence
        currentRound.tmp_stats_all.loc[currentRound.tmp_stats_all[currentRound.tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == currentRound.map_info.defense].index,"side"] = "Defense"
        currentRound.tmp_stats_all.loc[currentRound.tmp_stats_all[currentRound.tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == currentRound.map_info.offense].index,"side"] = "Offense"
        
        cp2 = _time.time()
        if self.debug_time: print ("[t] Checkpoint2 " + str(round((cp2  - cp1),3)) + " s")
        
        if currentRound.result_type == Const.EVENT_OSP_TIME_SET:
            #round 1. Time set is not indicative of win or loss. It could be set in result of a cap(5:33) or result of hold(10:00)
            round_diff = currentRound.map_info.timelimit*60 - currentRound.round_time
            currentRound.round_diff = round_diff
            
            if int(currentRound.map_info.timelimit*60) == int(currentRound.round_time):
                currentRound.winner = currentRound.map_info.defense
            else:
                currentRound.winner = currentRound.map_info.offense
              
        currentRound = self.determine_round_result(currentRound, currentRound.result_type)
        
        cp3 = _time.time()
        if self.debug_time: print ("[t] Checkpoint3 " + str(round((cp3  - cp2),3)) + " s")
        
        tmp_logdf["round_num"] = currentRound.round_num
        tmp_logdf["round_guid"] = currentRound.round_guid
        currentRound.tmp_stats_all["round_diff"] = currentRound.round_diff
        currentRound.tmp_stats_all["round_time"] = currentRound.round_time
        currentRound.round_datetime = self.select_time(self.osp_demo_date, self.osp_demo_time, self.osp_map_date, self.osp_map_time, currentRound.osp_stats_date, currentRound.osp_stats_time, currentRound.osp_jpeg_date, currentRound.osp_jpeg_time, self.log_date)
        currentRound.tmp_stats_all[Const.NEW_COL_MATCH_DATE] = currentRound.round_datetime
        
        cp4 = _time.time()
        if self.debug_time: print ("[t] Checkpoint4 " + str(round((cp4  - cp3),3)) + " s")
        
        
        if len(currentRound.player_stats) == 0:
            print("[!] No player stats for this match")
        else:
            players_all = {}
            players_all[currentRound.osp_guid] = currentRound.player_stats
            tmp_playersdf = build_player_df(players_all)
            self.submitter = tmp_playersdf.iloc[0,]["submitter"]
            tmp_playersdf["match_date"] = currentRound.round_datetime
            self.playersdf = self.playersdf.append(tmp_playersdf)
            
        self.matchesdf = self.matchesdf.append(self.build_matchdf(currentRound),sort=False) 
        self.logdf= self.logdf.append(tmp_logdf,sort=False)
        self.statsdf = self.statsdf.append(currentRound.tmp_stats_all,sort=False)
        #print(self.statsdf[["round_guid","Killer", "round_order"]].sort_values(by="round_order"))
        
        cp5 = _time.time()
        if self.debug_time: print ("[t] Checkpoint5 " + str(round((cp5  - cp4),3)) + " s")
        
        wrap_end_time = _time.time()
        #print(currentRound.tmp_stats_all[["round_guid","Killer", "round_order"]].sort_values(by="round_order"))
        print("[ ] Rnd " + str(currentRound.round_order).ljust(2) + " winner " + currentRound.winner.ljust(6) + " on " + currentRound.map_info.name[0:10].ljust(11) + ". Events: " + str(len(tmp_logdf)).ljust(4) + ". Players:" + str(len(currentRound.tmp_stats_all)).ljust(2) + "(Lines: " + str(round((currentRound.round_end_time - currentRound.round_start_time),2)) + " s " + "Wrap: " + str(round((wrap_end_time - wrap_start_time),2)) + " s)")                       
    
    def process_log(self):
        """ 
        Exception wrapper for the process_log_worker   
        """
        result = {}
        try:
            result = self.process_log_worker()
        except:
            print(f"[x] Failed to process {self.medium_agnostic_file_name} with the following error:\n\n")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,
            limit=5, file=sys.stdout)
        return result     
        
    def process_log_worker(self):
        """ 
        Walk through the file line by line, extract rounds, players, guids, renames into self.dataframes
  
        Parameters: 
           initial params stored in ClientLogProcessor
        
        Returns:
            dictionary of dataframes with game normalized lines
        """
        time_start_process_log = _time.time()
        #Initialize local variables
        line_event = "Nothing"
        round_order = 0
        line_order = 0
        current_player = None
        tmp_player_stat = ConstOsp.player_stat.copy()
        
        currentRound = Round(round_order) #likely garbage round because FIGHT did not happen yet
        
        #Load in Constants
        colors = setup_colors()
        log_lines = LogLine.LoadLogLines()
        
        osp_accuracy_lines = OSPFileLine.LoadOSPLines()
        for key in osp_accuracy_lines:
            if key[0:6] == 'ospacc':
                log_lines[key] = osp_accuracy_lines[key]
        
        #Load in map constants
        self.map_class = ConstMap
        self.map_class.load_maps(self.map_class)
        self.announcements = self.map_class.transpose_by_obj(self.map_class)

        #Prep debug log
        if self.debug:
            try:
                debug_log = open(self.debug_file,"w")
                debug_log.write("line".ljust(5) + "roundNum " + "##".ljust(3)  + "Event".ljust(20) + "Action".ljust(10) + "LineText".rstrip() + "\n")
            except:
                print("[!] Cannot write to the debug file. Is it already open? File: " + self.debug_file)
            
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
            stat_line_processed = False
                 
            if (line[1:3] == ":\\" and line[-6:] == "files)") or line == "    not on the pure list" or line == "    on the pure list" or len(line) == 0 or (line[0:10] == "LOADING..." and line[11:16] != "maps/"):
                #print("[Debug] Skipping " + line)
                continue
            
            if currentRound.round_stats_confidence == 4:
                if line == "--------------------------------------------------------------------------":
                    currentRound.round_stats_confidence = 0
                    continue
                if currentRound.game_happened:
                    pro_player, pro_line = process_pro_line(line,currentRound.round_stats_team_line) #for now just conform to osp
                    if pro_line is None:
                        currentRound.round_stats_confidence = 0 #this does not work
                    else:
                        currentRound.stats_dict[pro_player] = pro_line
                        currentRound.stats_lines.append(line.strip())   
                        stat_line_processed = True
                continue
                
            #for that line loop through all possible log line types and see which type of line it is
            for key, value in log_lines.items():
                                
                x = re.search(value.regex, line)
                #if it looks like something we recognize (x is not None) then add this line appropriately
                if x:                    
                    line_event = value.event
                    line_order = line_order + 1
                    
                     #################################
                     ###  OSP accuracies            ##
                     #################################
                    if value.event == ConstOsp.EVENT_PLAYER_ACC:
                        #print("[Debug] 1.5 " + line)
                        hits,attacks = osp_token_one_slash_two(x[1][5:15].strip())
                        rest_tokens = x[1][15:].split()

                        tmp_player_stat[value.mod + "_Accuracy"] =  x[1][0:5].strip()
                        #print("Acc:",x[1][0:5])
                        tmp_player_stat[value.mod + "_Hits"] =  hits
                        #print("Hits:",hits)
                        tmp_player_stat[value.mod + "_Attacks"] =  attacks
                        #print("Att:",attacks)
                        if value.mod != ConstOsp.WEAPON_SYRINGE and len(rest_tokens)>1:
                            tmp_player_stat[value.mod + "_Kills"] =  rest_tokens[0]
                            #print("Kills:",rest_tokens[0])
                            tmp_player_stat[value.mod + "_Deaths"] =  rest_tokens[1]
                            #print("Deaths:",rest_tokens[1])
                        if value.mod in ConstOsp.YES_HEADSHOT and len(rest_tokens)>2:
                            tmp_player_stat[value.mod + "_HeadShots"] =  rest_tokens[2]
                            #print("HS:",rest_tokens[2])
                        break
                    
                    if value.event == ConstOsp.EVENT_PLAYER_EXTRA:
                        if value.mod == ConstOsp.STAT_OSPFILE_PU_HEALTHPACK or value.mod == ConstOsp.STAT_OSPFILE_PU_AMMOPACK:
                            given, dropped = osp_token_one_slash_two(x[1].strip())
                            packtype = "Health" if value.mod == ConstOsp.STAT_OSPFILE_PU_HEALTHPACK else "Ammo"
                            tmp_player_stat[packtype + "Given"]= given
                            tmp_player_stat[packtype + "Dropped"]= dropped
                        if value.mod == ConstOsp.STAT_OSPFILE_PU_REVIVE:
                            tmp_player_stat["Revivals"] = x[1].strip()
                        break
                    
                    if value.event == ConstOsp.EVENT_PLAYER_DMG:
                        if current_player:   
                            #print("[Debug] 2", current_player)#, tmp_player_stat)
                            currentRound.player_stats[current_player] = tmp_player_stat.copy() #store the processed player
                            #print("[Debug] players :",len(currentRound.player_stats))
                            #print(tmp_player_stat)
                            #reset & start new
                            current_player = None
                        break
                    
                    #Accuracy info for: /mute doNka (2 Rounds)
                    if value.event == Const.EVENT_OSP_STATS_ACCURACY: #happens at the end of every round for a player that is ON A TEAM
                        current_player, round_num = osp_token_accuracy_playername_round(x[1])
                        if int(round_num) not in [1, 2]:
                            current_player = None
                            break
                        if currentRound.game_started:
                            self.tmp_submitter = current_player
                        tmp_player_stat = ConstOsp.player_stat.copy()
                        tmp_player_stat["rounds"] = round_num
                        break
                    
                    if value.event == Const.EVENT_PRO_TEAM:
                        #print("team", line)
                        currentRound.round_stats_confidence = 1
                        currentRound.round_stats_team_line = line
                        break
                    
                    if value.event == Const.EVENT_PRO_SEPARATOR:
                        #print("sep", line)
                        if currentRound.round_stats_confidence > 4:
                            print("sep3", line)
                            currentRound.round_stats_confidence = 0
                        currentRound.round_stats_confidence += 1
                        break
                    
                    if value.event == Const.EVENT_PRO_STATS_HEADER:
                        #print("head", line)
                        currentRound.round_stats_confidence += 1
                        break
                    
                    if value.event == Const.EVENT_PRO_STATS_TOTALS:
                        #print("tot", line)
                        currentRound.round_stats_confidence = 0
                        break
                    
                    #player renames in game. Store old and new name in doct for later processing
                    if value.event == Const.EVENT_RENAME:
                        self.renames[x[1]] = x[2]
                        break
                    
                    #beginning of every logfile
                    if value.event == Const.EVENT_LOGFILE_TIMESTAMP: 
                        self.log_date = str(datetime.strptime(x[1].strip(), "%a %b %d %H:%M:%S %Y" )) #Sun Apr 08 18:51:44 2018
                        break
                    
                    #Match starting...recording to demos/2019-10-24/214736-donka-mp_ice.dm_60.
                    if value.event == Const.EVENT_DATETIME_DEMO:
                        self.osp_demo_date = x[1].split("/")[1]
                        temp_time = x[1].split("/")[2].split("-")[0]
                        self.osp_demo_time = temp_time[0:2] + ":" + temp_time[2:4] + ":" + temp_time[4:6]
                        break
                    
                    #[skipnotify]Current time: 20:54:01 (24 Oct 2019)
                    #x[1] = '20:54:01 (24 Oct 2019)'
                    if value.event == Const.EVENT_DATETIME_OSP_MAP_LOAD:
                        self.osp_map_date = datetime.strptime(x[1].split("(")[1].split(")")[0], "%d %b %Y" ).strftime("%Y-%m-%d")
                        self.osp_map_time = x[1].split(" ")[0]
                        break
                    
                    #Wrote screenshots/2019-10-24/215503-donka-mp_ice.jpg
                    #x[1] = '2019-10-24'
                    #x[2] = '215503-donka-mp_ice.jpg'
                    if value.event == Const.EVENT_DATETIME_SCREENSHOT:
                        currentRound.osp_jpeg_date = x[1]
                        time_name_map = x[2]
                        currentRound.osp_jpeg_time = time_name_map[0:2] + ":" + time_name_map[2:4] + ":" + time_name_map[4:6]
                        currentRound.exact_map_ss = time_name_map.split("-")[-1][0:-4]
                        break
                    
                    #^3>>> Stats recorded to: ^7stats/2019.10.24/215502.txt
                    #x[1] = 'stats/2019.10.24/215502.txt'
                    if value.event == Const.EVENT_DATETIME_OSP_SAVE_STATS:
                        currentRound.osp_stats_date = x[1].split("/")[1].replace(".","-")
                        temp_time = x[1].split("/")[2][0:6]
                        currentRound.osp_stats_time = temp_time[0:2] + ":" + temp_time[2:4] + ":" + temp_time[4:6]
                        break
                    
                    #FIGHT!
                    if value.event == Const.EVENT_START:
                        if currentRound.game_paused:
                            currentRound.game_paused = False
                        else:
                            if currentRound.game_started: #round aborted or otherwise interrupted
                                round_order = round_order #start anew
                            else:
                                try:
                                    self.round_close(currentRound)
                                except:
                                    print("[x] Failed to close the round!")
                                    exc_type, exc_value, exc_traceback = sys.exc_info()
                                    traceback.print_exception(exc_type, exc_value, exc_traceback,limit=5, file=sys.stdout)
                                round_order += 1
                            
                            currentRound = Round(round_order) 
                            currentRound.exact_map_load = self.tmp_exact_map
                            currentRound.game_started = True
                            currentRound.game_happened = True
                            currentRound.round_start_time = _time.time()
                        break
                    
                    #game paused. Unpause will result in FIGHT line again                    
                    if currentRound.game_started and value.event == Const.EVENT_PAUSE: 
                        #print("[Debug] detected pause")
                        currentRound.game_paused = True
                        break
                    
                    #^7TEAM   Player          Kll Dth Sui TK Eff ^3Gib^7    ^2DG    ^1DR   ^6TD  ^3Score
                    if value.event == Const.EVENT_OSP_STATS_START:
                        #currentRound.reading_osp_stats = True
                        #nothing to do, just exit
                        break
                    
                    #^4Allies^7 ^5Totals           49  70  14  2^5  41^3  27^2 10969^1 12154^6  197^3     48
                    if value.event == Const.EVENT_OSP_STATS_END:
                        if currentRound.game_happened:
                            #currentRound.reading_osp_stats = False
                            currentRound.osp_guid = get_round_guid_osp(currentRound.stats_lines)
                            #print("Processing OSP stats id: " + osp_guid)
                            #print("Osp stats for guid calculation. Round: " + str(round_order))
                            #print(*currentRound.stats_lines, sep = "\n")
                            currentRound.stats_lines = []
                        else:
                            if currentRound.game_finished:
                                #this will be non-issue after round is processed FIGHT to FIGHT
                                print("[!] Processing OSP stats after OSP objective time string. This should never* happen")
                            else:
                                print("[!] Ignoring OSP stats because log of the first round is incomplete")
                        break

                    #^1Axis^7   ^5Totals           59  67  20  3^5  46^3  22^2 12154^1 10969^6  844^3     32
                    if currentRound.game_started and value.event == Const.EVENT_OSP_STATS_MID:
                        #do nothing, just exit
                        break
                    
                    #^1Axis^7   ^7Fister Miagi   ^3   7  12   1  1^7  36^3   1^2  1305^1  1917^6  123^3      6
                    #^4Allies^7 ^7bru            ^3   7  16   0  0^7  30^3   2^2  1442^1  2840^6    0^3     11
                    if value.event == Const.EVENT_OSP_STATS_ALLIES or value.event == Const.EVENT_OSP_STATS_AXIS: #OSP team stats per player
                        if currentRound.game_happened:
                            osp_player, osp_line = process_OSP_line(line)
                            if osp_line is not None: #someone echoes "Axis" ... thx Cliffdark or someone has 1246 kills (thx scrilla)
                                currentRound.stats_dict[osp_player] = osp_line
                                currentRound.stats_lines.append(line.strip())   
                                stat_line_processed = True
                        break
                    
                    #^\[skipnotify\]Timelimit hit\.
                    if currentRound.game_started and value.event == Const.EVENT_MAIN_TIMELIMIT: #happens before OSP stats if the time ran out
                        #currentRound.game_started = False # we still have OSP stats to process
                        currentRound.game_finished = True
                        currentRound.defense_hold = 1
                        currentRound.result_type = Const.EVENT_OSP_NOT_REACHED
                        # implement timelimit hit. It appears before OSP stats only when clock ran out
                        break
                    
                    #[skipnotify]Server: timelimit changed to 3.347367                       
                    if value.event == Const.EVENT_MAIN_SERVER_TIME:  #this can be invoked anytime by rcon or ref or map restart
                        #happens after OSP stats, but not when map changes
                        #also happens anytime ref changes timelimit 
                        #currentRound.game_started = False
                        #currentRound.game_finished = True
                        #currentRound.round_time = int(float(x[1])*60) # this comes after OSP stats and fucks everything up
                        break
                    
                    #[skipnotify]>>> ^3Objective reached at 1:36 (original: 6:49)
                    if currentRound.game_started and value.event == Const.EVENT_OSP_REACHED: #osp round 2 defense lost
                        currentRound.game_started = False
                        currentRound.game_finished = True
                        currentRound.defense_hold = 0
                        time1 = x[1].strip().split(":")
                        round_time = int(time1[0])*60 + int(time1[1])
                        #print("round 2 time is " + str(roundtime))
                        time2 = x[2].strip().split(":")
                        round_diff = int(time2[0])*60 + int(time2[1]) - round_time
                        
                        currentRound.round_time = round_time 
                        currentRound.round_diff = round_diff
                        #print("round times(t1,t2,diff) " + x[1].strip() + " " + x[2].strip() + " " + str(currentRound.round_diff))
                        currentRound.round_num = 2
                        currentRound.result_type = Const.EVENT_OSP_REACHED
                        break
                    
                    #[skipnotify]>>> ^3Objective NOT reached in time (3:20)
                    if currentRound.game_started and value.event == Const.EVENT_OSP_NOT_REACHED: #osp round 2 defense lost
                        currentRound.game_started = False
                        currentRound.game_finished = True
                        time = x[1].strip().split(":")
                        
                        round_time = int(time[0])*60 + int(time[1])
                        round_diff = 0
                        
                        currentRound.defense_hold = 1
                        currentRound.round_num = 2
                        currentRound.round_time = round_time
                        currentRound.round_diff = round_diff
                        currentRound.result_type = Const.EVENT_OSP_NOT_REACHED
                        break 
                    
                    #Always Round 1
                    #[skipnotify]>>> Clock set to: 10:00
                    #[skipnotify]>>> Clock set to: 6:56
                    if currentRound.game_started and value.event == Const.EVENT_OSP_TIME_SET: #osp round 1 end.
                        currentRound.game_started = False
                        currentRound.game_finished = True
                        
                        if (currentRound.defense_hold != 1): #do we know that it was fullhold from "Timelimit hit"?
                            currentRound.defense_hold = 0
                        
                        #Get time from that line
                        time = x[1].strip().split(":")
                        round_time = int(time[0])*60 + int(time[1])
                        currentRound.round_time = round_time
                        
                        currentRound.round_num = 1
                        self.tmp_r1_fullhold = currentRound.defense_hold
                        currentRound.result_type = Const.EVENT_OSP_TIME_SET
                        break
                    
                    if value.event == Const.CONSOLE_PASSWORD_RCON or (value.event == Const.CONSOLE_PASSWORD_REF and x[1].strip().split(" ")[0] not in Const.REF_COMMANDS) or value.event == Const.CONSOLE_PASSWORD_SERVER:
                        print("[!] Log contains sensitive information! Edit the log before sharing!")
                    
                    if value.event == Const.EVENT_PB_GUID:
                        try:
                            pb_guid = x[0][0:8]
                            pb_player = x[2]
                            self.pb_players[pb_player] = pb_guid
                        except:
                            print("[!] Could not process guid line. Debug info: x = re.search(value.regex,line)")
                    
                    if value.event == Const.EVENT_MAPLOAD:
                        self.tmp_exact_map = x[1]
                        break
                            
                    #if value.event == Const.EVENT_OSP_REACHED or value.event == Const.EVENT_OSP_NOT_REACHED or value.event == Const.EVENT_OSP_TIME_SET: #had and game_finished
                        #self.round_close(currentRound)
                        
                    #something was matched at this point
                    #IF the line relates to stats (kills, suicides, etc), write a stat_entry
                    #ELSE go through objective checks and write an objective entry
                    if not currentRound.game_finished and currentRound.game_started and value.stats:
                        if len(x.groups()) > 0:
                            victim = x[1]
                        else: 
                            victim = ""
                        if len(x.groups()) > 1:
                            killer = x[2]
                        else: 
                            killer = ""
                        stat_entry = StatLine("temp",line_order, round_order,currentRound.round_num,killer,value.event, value.mod, victim)
                    elif not currentRound.game_finished and currentRound.game_started and value.event == Const.EVENT_OBJECTIVE:
                        currentRound.obj_counter[x[1]] += 1
                        if 1==2: #TODO omit this for now
                            if(x[1] in self.announcements): 
                                announcement_values = self.announcements[x[1]]
                                map_info= self.map_class.maps[announcement_values[1]]  
                                obj_offender = map_info.offense
                                obj_defender = map_info.defense
                                obj_type = announcement_values[0]
                                if "Allies transmitted the documents!" not in x[1] and "Forward Bunker" not in x[1] and "Dynamite planted near the Service Door!" not in x[1]:
                                    #Frostbite and beach same objectives
                                    #Delivery and beach same objectives
                                    currentRound.map_counter[map_info.code] +=1
                                #print("Known objective: ".ljust(20) + x[1] + " map: " + map_info.name)
                                stat_entry = StatLine("temp",line_order, round_order,currentRound.round_num,obj_offender,"Objective", obj_type, obj_defender)
                            else: #things that are not in the announcemenets
                                if ("the War Documents" in x[1]):
                                    "This objective repeats in various maps so we are going to skip it"
                                elif ("Axis have returned the objective!" in x[1]):
                                    "Generic message, skip it"
                                elif ("Allies have returned the objective!" in x[1]):
                                    "Generic message, skip it"
                                elif ("Allies have lost" in x[1]):
                                    "Generic message, skip it"
                                elif ("Dynamite planted near" in x[1]):
                                    "Generic message, skip it"
                                elif ("Axis defused dynamite" in x[1]):
                                    "Generic message, skip it"
                                elif ("Axis have lost" in x[1]):
                                    "Generic message, skip it"
                                else:
                                    print("[!] -----------Unknown objective: ".ljust(20) + x[1])
                                    currentRound.map_counter["Not listed"] +=1
                        else: 
                            stat_entry = None
                    else:
                        stat_entry = None
                    break
            
            
            #if did not match any regex    
            else:
                #did not match any lines
                line_event = "Nothing"
                #bad panzer special handling
                y = re.search("^\[skipnotify\](.*) was killed by (.*)",line)  
                if not currentRound.game_finished and y:
                    value.event = Const.EVENT_KILL
                    stat_entry = StatLine("temp",line_order, round_order,1,y[2],value.event, Const.WEAPON_PANZER, y[1])
                    line_event = "Bad panzer"
                #end of bad panzer handling
            
            if stat_entry:
                processedLine = "Logged" 
                currentRound.tmp_log_events.append(stat_entry)
            elif stat_line_processed:
                processedLine = "Osp added"
            elif x:
                processedLine = "Processed"
            else:
                processedLine = "Ignored"
           
            #write the line processing notes into the debig file
            write_line = str(line_order).ljust(5) + "roundNum " + str(round_order).ljust(3)  + line_event.ljust(20) + processedLine.ljust(10) + line.rstrip() + "\n"
            #if round_order==7: print(write_line[0:-1])
            if self.debug:
                debug_log.write(write_line)
        
        #close debug file        
        if self.debug:
            debug_log.close() 
        
        try:
            self.round_close(currentRound) #get last round
        except:
            print("[x] Failed to close the round!")
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback.print_exception(exc_type, exc_value, exc_traceback,limit=5, file=sys.stdout) 

        if self.matchesdf.empty or self.statsdf.empty or self.logdf.empty:
            print("[x] Nothing was processed")
            return None
        else:
            try:
                fixed_renames = self.fix_renames(self.renames)
            except:
                fixed_renames = self.renames
                print("[!] fix_renames did not work for dictionary:")
                print(self.renames)
                

            
            self.logdf = self.handle_renames(fixed_renames, ["killer","victim"], self.logdf, False)
            self.logdf = self.logdf[['round_guid','line_order','round_order','round_num','event','killer','mod','victim']]
            
            self.statsdf = self.handle_renames(fixed_renames, ['player_strip','Killer','OSP_Player'], self.statsdf, True)
            self.statsdf = self.populate_guids(self.statsdf,self.pb_players, fixed_renames)
            
            self.playersdf = self.handle_renames(fixed_renames, ["player"], self.playersdf, False)
            self.playersdf["submitter"] = self.tmp_submitter
            
            if(len(self.renames) > 0):
                renameDF = pd.DataFrame.from_dict(self.renames, orient='index').reset_index()
                renameDF.columns = ["original","renamed_to"]
            else:
                renameDF = None
            
            time_end_process_log = _time.time()
            print ("[ ] File processed " + self.medium_agnostic_file_name + ". Total time is " + str(round((time_end_process_log - time_start_process_log),2)) + " s")
            return {"logs":self.logdf, "stats":self.statsdf, "matches":self.matchesdf, "renames" : renameDF, "players" : self.playersdf, "submitter" : self.submitter, "type" : self.match_type}