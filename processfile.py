import re
import pandas as pd
import os.path
from datetime import datetime
import time as _time


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

    def __init__(self,read_file, debug_file, debug=True):
            self.read_file = read_file
            self.debug_file = debug_file
    
    def get_file_date(self):
        return str(datetime.fromtimestamp(os.path.getmtime(self.read_file)).strftime('%Y-%m-%d'))
    
    def get_file_size(self):
        return str(os.path.getsize(self.read_file))

    #Disassemble the following lines into a dataframe
    #                                Kll Dth Sui TK Eff Gib DG    DR      TD  Score
    #line = "Allies /mute doNka      19   3   0  0  86   5  2367  1435    0     48"
    #line = "Allies /mute sem        19  10   2  2  65   4  3588  2085  226     46"
    def process_OSP_line(self,line):
        tokens = re.split("\s+", line)    
        player = " ".join(tokens[1:len(tokens)-11])
        temp = pd.DataFrame([[player, tokens[0],tokens[-11],tokens[-10],tokens[-9],tokens[-8],tokens[-7],tokens[-6],tokens[-5],tokens[-4],tokens[-3],tokens[-2]]], columns=Const.osp_columns)
        return temp
    
    def openFile(self):
        with open(self.read_file,"r") as ins:
            lines = []
            for line in ins:
                lines.append(line)
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
            #print(df.index.unique())
        return df
        
    def summarize_round(self, logdf, ospdf):
        kills = logdf[logdf["event"].isin([Const.EVENT_TEAMKILL,Const.EVENT_SUICIDE,Const.EVENT_KILL])].groupby(["killer","event"])["event"].count().unstack()
        deaths = logdf[logdf["event"].isin([Const.EVENT_TEAMKILL,Const.EVENT_SUICIDE,Const.EVENT_KILL])].groupby(["victim","event"])["event"].count().unstack()

        ################################
        # Stats collected from logs    #
        ################################
        stats = pd.DataFrame(index = kills.append(deaths).index.unique())
        
        #there will be some kills and death i'm sure.... 
        stats[Const.STAT_BASE_KILL]  = kills[Const.EVENT_KILL]
        stats[Const.STAT_BASE_DEATHS]= deaths[Const.EVENT_KILL]

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
            
        stats[Const.STAT_BASE_ALLDEATHS]= stats[Const.STAT_BASE_DEATHS].fillna(0) + stats[Const.STAT_BASE_SUI].fillna(0) + stats[Const.STAT_BASE_TKd].fillna(0)
        #print(stats[[Const.STAT_BASE_DEATHS, Const.STAT_BASE_SUI, Const.STAT_BASE_TKd, Const.STAT_BASE_ALLDEATHS]])
        
        stats = stats.drop(index='') #empty players
        stats = stats.fillna(0)

        #pd.options.display.float_format = '{:0,.0f}'.format
        
        #######################################
        # Stats collected from osp summary    #
        #######################################
        ospdf.index = ospdf[Const.STAT_OSP_SUM_PLAYER]
        stats = stats.reset_index()
        stats.index = stats['index'].str[0:15] #because OSP names are 15 chars only
        stats_all = stats.join(ospdf) #Totals fall out naturally
        stats_all.index = stats_all['index'] #go back
        del stats_all["index"]
        #print(stats_all)
        stats_all = add_team_name(stats_all)
        
        return stats_all
    
    def add_classes(self, logdf, stats_all):
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

        return stats_all

    def process_log(self):
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
        collect_events = False
        
        tmp_r1_fullhold = None
        
        
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
        debug_log = open(self.debug_file,"w")
        debug_log.write("line".ljust(5) + "roundNum " + "##".ljust(2)  + "Event".ljust(20) + "Action".ljust(10) + "LineText".rstrip() + "\n")
        log_file_lines = self.openFile()
        fileLen = len(log_file_lines)-1
        
        #Derive log file properties
        file_date = self.get_file_date()
        file_size = self.get_file_size()
    
        #go through each line in the file
        for i in range(0,fileLen):
            #strip color coding
            line = stripColors(log_file_lines[i], colors)          
            #init loop variables
            stat_entry = None
            osp_line_processed = False
            
            #for that line loop through all possible log line types and see which type of line it is
            for key, value in log_lines.items():
                
                x = re.search(value.regex, line)
                #if it looks like something we recognize (x is not None) then add this line appropriately
                if x:
                    line_event = value.event
                    line_order = line_order + 1
                    
                    #player renames in game. Store old and new name in doct for later processing
                    if value.event == Const.EVENT_RENAME:
                        #print("x" + str(x) + " x0: " + x[0] + " x1: " + x[1] + " x2: " + x[2])
                        renames[x[1]] = x[2]
                        break
                    
                    #beginning of every logfile
                    if value.event == Const.EVENT_LOGFILE_TIMESTAMP: 
                        #Sun Apr 08 18:51:44 2018
                        log_date = str(datetime.strptime(x[1].strip(), "%a %b %d %H:%M:%S %Y" ))
                        break
                    
                    #Match starting...recording to demos/2019-10-24/214736-donka-mp_ice.dm_60.
                    if value.event == Const.EVENT_DATETIME_DEMO:
                        #osp_demo_date = datetime.strptime(x[1].split("/")[1], "%Y-%M-%d" )
                        osp_demo_date = x[1].split("/")[1]
                        temp_time = x[1].split("/")[2].split("-")[0]
                        osp_demo_time = temp_time[0:2] + ":" + temp_time[2:4] + ":" + temp_time[4:6]
                        break
                    
                    #[skipnotify]Current time: 20:54:01 (24 Oct 2019)
                    #x[1] = '20:54:01 (24 Oct 2019)'
                    if value.event == Const.EVENT_DATETIME_OSP_MAP_LOAD:
                        osp_map_date = datetime.strptime(x[1].split("(")[1].strip(")"), "%d %b %Y" ).strftime("%Y-%m-%d")
                        osp_map_time = x[1].split(" ")[0]
# =============================================================================
#                         print("map load")
#                         print(osp_map_time)
#                         print(osp_map_date)
# =============================================================================
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
                    
                    #^1FIGHT!
                    if value.event == Const.EVENT_START and game_paused == False:
                        #round aborted or otherwise interrupted
                        if (game_started): #round aborted or otherwise interrupted
                            tmp_log_events = []                        
                        game_started = True
                        collect_events = True
                        round_order = round_order + 1
                        ospDF = pd.DataFrame(columns=Const.osp_columns)
                        tmp_log_events = []
                        tmp_stats_all = []
                        map_counter = Counter() #reset it
                        
                        #start new match class
                        new_match_line = MatchLine(file_date,   # date of file creation
                                                   None,    # date from the text of the log itself
                                                   file_size,   # file size
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
                    
                    #^7Accuracy info for: ^3KrAzYkAzE ^7(^22^7 Rounds)
                    if game_started and value.event == Const.EVENT_OSP_STATS_ACCURACY: #happens aat the end of every round for a player that is ON A TEAM
                        #Accuracy info for: /mute doNka (2 Rounds)
                        #get round number
                        collect_events = False
                        new_match_line.round_num = int(line.split("(")[-1].split(" ")[0])
                        break
                    
                    #^7TEAM   Player          Kll Dth Sui TK Eff ^3Gib^7    ^2DG    ^1DR   ^6TD  ^3Score
                    if game_started and value.event == Const.EVENT_OSP_STATS_START and reading_osp_stats == False:
                        collect_events = False
                        reading_osp_stats = True
                        break
                    
                    #^4Allies^7 ^5Totals           49  70  14  2^5  41^3  27^2 10969^1 12154^6  197^3     48
                    if game_started and value.event == Const.EVENT_OSP_STATS_END:
                        reading_osp_stats = False
                        osp_guid = get_round_guid_osp(osp_lines)
                        #print("Processing OSP stats id: " + osp_guid)
                        #print("Osp stats for guid calculation. Round: " + str(round_order))
                        #print(*osp_lines, sep = "\n")
                        osp_lines = []
                        break
                    
                    #^1Axis^7   ^5Totals           59  67  20  3^5  46^3  22^2 12154^1 10969^6  844^3     32
                    if game_started and value.event == Const.EVENT_OSP_STATS_MID:
                        #do nothing for this line
                        break
                    
                    #^1Axis^7   ^7Fister Miagi   ^3   7  12   1  1^7  36^3   1^2  1305^1  1917^6  123^3      6
                    #^4Allies^7 ^7bru            ^3   7  16   0  0^7  30^3   2^2  1442^1  2840^6    0^3     11
                    if value.event == Const.EVENT_OSP_STATS_ALLIES or value.event == Const.EVENT_OSP_STATS_AXIS: #OSP team stats per player
                        if game_started == False:
                            if game_finished == True:
                                print("Warning: processing OSP stats after OSP objective time string. This should never* happen")
                            else:
                                print("Warning: ignoring OSP stats because log of the first round is incomplete")
                        else:
                            osp_line = self.process_OSP_line(line)
                            #typing /scores in the middle of the game can double the stats. 
                            #Make sure to drop intermediary line
                            if(osp_line[Const.STAT_OSP_SUM_PLAYER].values[0] in ospDF[Const.STAT_OSP_SUM_PLAYER].values):
                                ospDF = ospDF.drop(osp_line.index)
                            ospDF = ospDF.append(osp_line,sort=False)
                            osp_lines.append(line.strip())   
                            osp_line_processed = True
                        break
                    
                    #^\[skipnotify\]Timelimit hit\.
                    if game_started and value.event == Const.EVENT_MAIN_TIMELIMIT: #happens before OSP stats if the time ran out
                        #game_started = False # we still have OSP stats to process
                        game_paused = False
                        game_finished = True
                        collect_events = False
                        new_match_line.defense_hold = 1
                        # implement timelimit hit. It appears before OSP stats only when clock ran out
                        break
                    
                    #[skipnotify]Server: timelimit changed to 3.347367                       
                    #if value.event == Const.EVENT_MAIN_SERVER_TIME:  #this can be invoked anytime by rcon or ref or map restart
                        #happens after OSP stats, but not when map changes
                        #also happens anytime ref changes timelimit 
                        #game_started = False
                        #game_paused = False
                        #game_finished = True
                        #new_match_line.round_time = int(float(x[1])*60) # this comes after OSP stats and fucks everything up
                        #break
                    
                    #[skipnotify]>>> ^3Objective reached at 1:36 (original: 6:49)
                    if game_started and value.event == Const.EVENT_OSP_REACHED: #osp round 2 defense lost
                        game_started = False
                        game_paused = False
                        game_finished = True
                        collect_events = False
                        new_match_line.defense_hold = 0
                        time1 = x[1].strip().split(":")
                        roundtime = int(time1[0])*60 + int(time1[1])
                        #print("round 2 time is " + str(roundtime))
                        new_match_line.round_time = roundtime 
                        time2 = x[2].strip().split(":")
                        new_match_line.round_diff = int(time2[0])*60 + int(time2[1]) - roundtime
                        #print("round times(t1,t2,diff) " + x[1].strip() + " " + x[2].strip() + " " + str(new_match_line.round_diff))
                        new_match_line.round_num = 2
                        #break # do not
                    
                    #[skipnotify]>>> ^3Objective NOT reached in time (3:20)
                    if game_started and value.event == Const.EVENT_OSP_NOT_REACHED: #osp round 2 defense lost
                        game_started = False
                        game_paused = False
                        game_finished = True
                        collect_events = False
                        time = x[1].strip().split(":")
                        roundtime = int(time[0])*60 + int(time[1])
                        new_match_line.round_diff = 0
                        new_match_line.defense_hold = 1
                        new_match_line.round_num = 2
                        new_match_line.round_time = roundtime
                        #break # do not
                    
                    #Always Round 1
                    #[skipnotify]>>> Clock set to: 10:00
                    #[skipnotify]>>> Clock set to: 6:56
                    if game_started and value.event == Const.EVENT_OSP_TIME_SET: #osp round 1 end.
                        game_started = False
                        game_paused = False
                        game_finished = True
                        collect_events = False
                        
                        if (new_match_line.defense_hold != 1): #do we know that it was fullhold from "Timelimit hit"?
                            new_match_line.defense_hold = 0
                        
                        #Get time from that line
                        time = x[1].strip().split(":")
                        new_match_line.round_time = int(time[0])*60 + int(time[1])
                        
                        new_match_line.round_num = 1
                        #TEMP_STORAGE
                        #tmp_r1_time = new_match_line.round_time
                        tmp_r1_fullhold = new_match_line.defense_hold
                        #break # do not
                    
                    if value.event == Const.CONSOLE_PASSWORD_RCON or (value.event == Const.CONSOLE_PASSWORD_REF and x[1].strip() != "comp") or value.event == Const.CONSOLE_PASSWORD_SERVER:
                        print("[!] Log contains sensitive information! Edit the log before sharing!")
                        print(line)
                        
                    
                    ######################################################################
                    #####################wrap up the round################################
                    ######################################################################
                    if game_finished and (value.event == Const.EVENT_OSP_REACHED or value.event == Const.EVENT_OSP_NOT_REACHED or value.event == Const.EVENT_OSP_TIME_SET):
                                                
                        #Determine the map                        
                        del map_counter["anymap"]
                        if(len(map_counter) > 1):
                            print("WARNING: Multiple objectives related to maps: " + str(map_counter))
                        
                        if(len(map_counter) == 0):
                            map_code = None
                            map_name = "unknown"
                            tmp_map = map_class.maps["anymap"]
                        else:
                            map_code = map_counter.most_common(1)[0][0]
                            tmp_map = map_class.maps[map_code]
                            map_name = tmp_map.name
                            
                        #round up all events and join them with OSP
                        tmp_logdf = pd.DataFrame([vars(e) for e in tmp_log_events])

                        tmp_stats_all = self.summarize_round(tmp_logdf, ospDF)
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
                            #TODO: determine teams based on kills just for this scenario
                            print("No teams found. OSP stats not joined for round " + str(tmp_stats_all["round_order"].min()))
                        else: 
                            new_match_line.players = get_player_list(tmp_stats_all)
                                            
                        #wrap up round one only
                        if value.event == Const.EVENT_OSP_TIME_SET:
                            #round 1. Time set is not indicative of win or loss. It could be set in result of a cap(5:33) or result of hold(10:00)
                            new_match_line.round_diff = tmp_map.timelimit*60 - new_match_line.round_time
                            tmp_stats_all.loc[tmp_stats_all[tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == tmp_map.offense].index,"round_win"] = abs(1 - new_match_line.defense_hold)
                            tmp_stats_all.loc[tmp_stats_all[tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == tmp_map.defense].index,"round_win"] = new_match_line.defense_hold
                            tmp_stats_all["game_result"] = "R1MSB"
                            if int(tmp_map.timelimit*60) == int(new_match_line.round_time):
                                new_match_line.winner = tmp_map.defense
                            else:
                                new_match_line.winner = tmp_map.offense
                        
                        #wrap up round two only 
                        if value.event == Const.EVENT_OSP_NOT_REACHED:
                            #round 2 DEFENSE HELD (WON OR DRAW)
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
                                print("bad round 2 winner status")

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
                        new_match_line.round_guid = round_guid
                        new_match_line.osp_guid = osp_guid
                        
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
                            
                        new_match_line.match_date = round_datetime
                        tmp_stats_all[Const.NEW_COL_MATCH_DATE] = round_datetime
                        
                        
                        matches.append(new_match_line)
                        print("Proccessed round " + str(new_match_line.round_order).ljust(2) + " winner " + new_match_line.winner.ljust(6) + " on " + new_match_line.map[0:10].ljust(11) + ". Events: " + str(len(tmp_logdf)).ljust(6) + ". Players: " + str(len(tmp_stats_all)) )
                        
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
                        

                        
                        
                        ######################################################################
                        ##############END of wrap up the round################################
                        ######################################################################
                        
                    
                    
                    #something was matched at this point
                    #IF the line relates to stats (kills, suicides, etc), write a stat_entry
                    #ELSE go through objective checks and write an objective entry
                    if collect_events and game_started and value.stats:
                        if len(x.groups()) > 0:
                            victim = x[1]
                        else: 
                            victim = ""
                        if len(x.groups()) > 1:
                            killer = x[2]
                        else: 
                            killer = ""
                        stat_entry = StatLine("temp",line_order, round_order,round_num,killer,value.event, value.mod, victim)
                    elif collect_events and game_started and value.event == Const.EVENT_OBJECTIVE:
                        #insert processing here for who and what
                        if(x[1] in announcements):                       
                            announcement_values = announcements[x[1]]
                            map_info= map_class.maps[announcement_values[1]]  
                            #print(x[1] + " interpreted as " + map_info.code)
                            obj_offender = map_info.offense
                            obj_defender = map_info.defense
                            obj_type = announcement_values[0]
                            if ("Allies transmitted the documents!" not in x[1]):
                                #Frostbite and beach share this objective"
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
                                print("---------------Unknown objective: ".ljust(20) + x[1])
                    else:
                        stat_entry = None
                    break
            
            
            #if did not match any regex    
            else:
                #did not match any lines
                line_event = "Nothing"
                #bad panzer special handling
                y = re.search("^\[skipnotify\](.*) was killed by (.*)",line)  
                if collect_events and y:
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
            debug_log.write(write_line)
        
        #close debig file        
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
            print("Nothing was processed")
            exit()
            return None
        else:
            matchesdf = pd.DataFrame([vars(e) for e in matches])
            logdf = self.handle_renames(renames, ["killer","victim"], logdf, False)
            stats_all = self.handle_renames(renames, ['player_strip','Killer','team_captain','OSP_Player'], stats_all, True)            
            logdf = logdf[['round_guid','line_order','round_order','round_num','event','killer','mod','victim']]
            
            if(len(renames) > 0):
                renameDF = pd.DataFrame.from_dict(renames, orient='index').reset_index()
                renameDF.columns = ["original","renamed_to"]
            else:
                renameDF = None
            
            time_end_process_log = _time.time()
            print ("Time to process " + self.read_file + " is " + str(round((time_end_process_log - time_start_process_log),2)) + " s")
            return {"logs":logdf, "stats":stats_all, "matches":matchesdf, "renames" : renameDF}
            
        
        
