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
        vars =  [str(self.match_guid),str(self.line_order),str(self.round_order),str(self.round_num), str(self.killer),str(self.event),str(self.mod),str(self.victim)]
        return ",".join(vars)

class MatchLine:
      
    def __init__(self, file_date, log_date, file_size, round_guid, osp_guid, round_order, round_num, players, defense_hold, winner, round_time, round_diff, map_):
         self.file_date = file_date
         self.log_date = log_date
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
        stats_all = stats.join(ospdf) #Totals fall out naturally
        #print(stats_all)
        stats_all = add_team_name(stats_all)
        
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
        tmp_r1_fullhold = None
        log_date = str(datetime.now())
        
        tmp_log_events = []
        renames = {}
        
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
        debug_log.write("line".ljust(5) + "roundNum " + "##".ljust(2)  + "Event".ljust(20) + "Logged as".ljust(10) + "LineText".rstrip() + "\n")
        log_file_lines = self.openFile()
        fileLen = len(log_file_lines)-1
        
        #Derive log file properties
        file_date = self.get_file_date()
        file_size = self.get_file_size()
    
        #go through each line in the file
        for x in range(0,fileLen):
            #strip color coding
            line = stripColors(log_file_lines[x], colors)
            
            #init loop variables
            matched = None
            stat_entry = None
            ospline = None
            
            #for that line loop through all possible log line types and see which type of line it is
            for key, value in log_lines.items():
                
                x = re.search(value.regex, line)
                #if it looks like something we recognize (x is not None) then add this line appropriately
                if x:
                    line_order = line_order + 1
                    
                    if value.event == Const.EVENT_RENAME:
                        #print("x" + str(x) + " x0: " + x[0] + " x1: " + x[1] + " x2: " + x[2])
                        renames[x[1]] = x[2]
                    
                    if value.event == Const.EVENT_LOGFILE_TIMESTAMP: #beginning of every logfile
                        #Sun Apr 08 18:51:44 2018
                        log_date = str(datetime.strptime(x[1].strip(), "%a %b %d %H:%M:%S %Y" ))
                    
                    #^1FIGHT!
                    if value.event == Const.EVENT_START and game_paused == False:
                        if (game_started): #round aborted or otherwise interrupted
                            tmp_log_events = []                        
                        game_started = True
                        round_order = round_order + 1
                        ospDF = pd.DataFrame(columns=Const.osp_columns)
                        tmp_log_events = []
                        tmp_stats_all = []
                        
                        new_match_line = MatchLine(file_date,   # date of file creation
                                                   log_date,    # date from the text of the log itself
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
                                         
                    if game_started and value.event == Const.EVENT_PAUSE: #game paused. Unpause will result in FIGHT line again
                        game_paused = True
                    
                    #^7Accuracy info for: ^3KrAzYkAzE ^7(^22^7 Rounds)
                    if game_started and value.event == Const.EVENT_OSP_STATS_ACCURACY: #happens aat the end of every round for a player that is ON A TEAM
                        #Accuracy info for: /mute doNka (2 Rounds)
                        #get round number
                        new_match_line.round_num = int(line.split("(")[-1].split(" ")[0])
                    
                    #^7TEAM   Player          Kll Dth Sui TK Eff ^3Gib^7    ^2DG    ^1DR   ^6TD  ^3Score
                    if game_started and value.event == Const.EVENT_OSP_STATS_START and reading_osp_stats == False:
                        reading_osp_stats = True
                    
                    #^4Allies^7 ^5Totals           49  70  14  2^5  41^3  27^2 10969^1 12154^6  197^3     48
                    if game_started and value.event == Const.EVENT_OSP_STATS_END:
                        reading_osp_stats = False
                        osp_guid = get_round_guid_osp(osp_lines)
                        #print("Processing OSP stats id: " + osp_guid)
                        #print("Osp stats for guid calculation. Round: " + str(round_order))
                        #print(*osp_lines, sep = "\n")
                        osp_lines = []
                    
                    #^1Axis^7   ^5Totals           59  67  20  3^5  46^3  22^2 12154^1 10969^6  844^3     32
                    if game_started and value.event == Const.EVENT_OSP_STATS_MID:
                        #do nothing for this line
                        break
                    
                    #^1Axis^7   ^7Fister Miagi   ^3   7  12   1  1^7  36^3   1^2  1305^1  1917^6  123^3      6
                    #^4Allies^7 ^7bru            ^3   7  16   0  0^7  30^3   2^2  1442^1  2840^6    0^3     11
                    if value.event == Const.EVENT_OSP_STATS_ALLIES or value.event == Const.EVENT_OSP_STATS_AXIS: #OSP team stats per player
                        if (game_started == False):
                            print("Warning: processing OSP stats after OSP objective time string. This should never* happen")
                        osp_line = self.process_OSP_line(line)
                        ospDF = ospDF.append(osp_line)
                        osp_lines.append(line.strip())                      
                    
                    #^\[skipnotify\]Timelimit hit\.
                    if value.event == Const.EVENT_MAIN_TIMELIMIT: #happens before OSP stats if the time ran out
                        #game_started = False # we still have OSP stats to process
                        game_paused = False
                        game_finished = True
                        new_match_line.defense_hold = 1
                        # implement timelimit hit. It appears before OSP stats only when clock ran out
                                           
                    #if value.event == Const.EVENT_MAIN_SERVER_TIME:  #this can be invoked anytime by rcon or ref or map restart
                        #happens after OSP stats, but not when map changes
                        #also happens anytime ref changes timelimit 
                        #game_started = False
                        #game_paused = False
                        #game_finished = True
                        #new_match_line.round_time = int(float(x[1])*60) # this comes after OSP stats and fucks everything up
                    
                    if game_started and value.event == Const.EVENT_OSP_REACHED: #osp round 2 defense lost
                        game_started = False
                        game_paused = False
                        game_finished = True
                        new_match_line.defense_hold = 0
                        time1 = x[1].strip().split(":")
                        roundtime = int(time1[0])*60 + int(time1[1])
                        #print("round 2 time is " + str(roundtime))
                        new_match_line.round_time = roundtime 
                        time2 = x[2].strip().split(":")
                        new_match_line.round_diff = int(time2[0])*60 + int(time2[1]) - roundtime
                        #print("round times(t1,t2,diff) " + x[1].strip() + " " + x[2].strip() + " " + str(new_match_line.round_diff))
                        new_match_line.round_num = 2
                        
                    if game_started and value.event == Const.EVENT_OSP_NOT_REACHED: #osp round 2 defense lost
                        game_started = False
                        game_paused = False
                        game_finished = True
                        time = x[1].strip().split(":")
                        roundtime = int(time[0])*60 + int(time[1])
                        new_match_line.round_diff = 0
                        new_match_line.defense_hold = 1
                        new_match_line.round_num = 2
                        new_match_line.round_time = roundtime
                        
                    #[skipnotify]>>> Clock set to: 10:00
                    #[skipnotify]>>> Clock set to: 6:56
                    if game_started and value.event == Const.EVENT_OSP_TIME_SET: #osp round 1 end.
                        game_started = False
                        game_paused = False
                        game_finished = True
                        
                        if (new_match_line.defense_hold != 1): #do we know that it was fullhold from "Timelimit hit"?
                            new_match_line.defense_hold = 0
                        
                        #Get time from that line
                        time = x[1].strip().split(":")
                        new_match_line.round_time = int(time[0])*60 + int(time[1])
                        
                        new_match_line.round_num = 1
                        #TEMP_STORAGE
                        #tmp_r1_time = new_match_line.round_time
                        tmp_r1_fullhold = new_match_line.defense_hold
                    
                    ######################################################################
                    #####################wrap up the round################################
                    ######################################################################
                    if game_finished and (value.event == Const.EVENT_OSP_REACHED or value.event == Const.EVENT_OSP_NOT_REACHED or value.event == Const.EVENT_OSP_TIME_SET):
                        if(len(map_counter) > 1):
                            print("WARNING: Multiple objectives related to maps: " + str(map_counter))
                        
                        #if either of the 3 above, dump stats
                        if(len(map_counter) == 0):
                            map_code = None
                        else:
                            map_code = map_counter.most_common(1)[0][0]
                            
                        map_counter = Counter() #reset it
                        tmp_logdf = pd.DataFrame([vars(e) for e in tmp_log_events])
                        tmp_stats_all = self.summarize_round(tmp_logdf, ospDF)
                        tmp_stats_all["round_order"] = round_order
                        tmp_stats_all = add_team_name(tmp_stats_all)
                        round_guid = get_round_guid_client_log(tmp_stats_all)
                        #print("Processed log stats id: " + round_guid)
                        tmp_stats_all["round_guid"] = round_guid
                        tmp_stats_all["osp_guid"] = osp_guid
                        tmp_stats_all["round_num"] = new_match_line.round_num
                        
                        if(map_code == None):
                            print("WARNING: Map not found")
                        else:
                            tmp_map = map_class.maps[map_code]
                            tmp_stats_all["map"] = tmp_map.name
                            new_match_line.map = tmp_map.name
                        
                        #Recalculated scores (substract kills and suicides)
                        tmp_stats_all[Const.STAT_POST_ADJSCORE] = tmp_stats_all[Const.STAT_OSP_SUM_SCORE].fillna(0).astype(int) - tmp_stats_all[Const.STAT_BASE_KILL].fillna(0).astype(int) + tmp_stats_all[Const.STAT_BASE_SUI].fillna(0).astype(int)*3 + tmp_stats_all[Const.STAT_BASE_TK].fillna(0).astype(int)*3
                        #print(tmp_stats_all[["AdjScore","score","kill","Suicide","TK"]])                  
                        
                        #print(tmp_stats_all.columns.values)
                        #print(tmp_stats_all[Const.STAT_OSP_SUM_TEAM])
                        #print(tmp_map.defense)
                        #print(tmp_stats_all[tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == tmp_map.defense].index)
                        #print(tmp_stats_all.loc[tmp_stats_all[tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == tmp_map.defense].index])

                        tmp_stats_all.loc[tmp_stats_all[tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == tmp_map.defense].index,"side"] = "Defense"
                        tmp_stats_all.loc[tmp_stats_all[tmp_stats_all[Const.STAT_OSP_SUM_TEAM] == tmp_map.offense].index,"side"] = "Offense"
                        
                        print(tmp_stats_all)
                        if(tmp_stats_all["side"].isnull().sum() == len(tmp_stats_all)):
                            print("No teams found (osp stats not joined)")
                        else: 
                            new_match_line.players = get_player_list(tmp_stats_all)
                                            

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
                        
                        tmp_logdf["round_guid"] = round_guid
                        tmp_logdf["round_num"] = new_match_line.round_num
                        new_match_line.round_guid = round_guid
                        new_match_line.osp_guid = osp_guid
                        #print(str(new_match_line.round_diff))
                        matches.append(new_match_line)
                        print("Proccessed round " + str(new_match_line.round_order) + " winner " + new_match_line.winner + " on " + new_match_line.map)
                        #log_events = log_events + tmp_log_events
                        try:
                            logdf
                        except NameError:
                            logdf = tmp_logdf
                        else:
                            logdf = logdf.append(tmp_logdf)
                        try:
                            stats_all
                        except NameError:
                            stats_all = tmp_stats_all
                        else:
                            stats_all = stats_all.append(tmp_stats_all)
                                                          
                    if len(x.groups()) > 0: 
                        victim = x[1]
                    else: 
                        victim = ""
                    if len(x.groups()) > 1:
                        killer = x[2]
                    else: 
                        killer = ""
                    
                    
                    #print(value.event)
                    
                    #something was matched at this point
                    #IF the line relates to stats (kills, suicides, etc), write a stat_entry
                    #ELSE go through objective checks and write an objective entry
                    if game_started and value.stats:
                       stat_entry = StatLine("temp",line_order, round_order,round_num,killer,value.event, value.mod, victim)
                    elif game_started and value.event == Const.EVENT_OBJECTIVE:
                        #insert processing here for who and what
                        if(x[1] in announcements):                       
                            announcement_values = announcements[x[1]]
                            map_info= map_class.maps[announcement_values[1]]  
                            #print(x[1] + " interpreted as " + map_info.code)
                            obj_offender = map_info.offense
                            obj_defender = map_info.defense
                            obj_type = announcement_values[0]
                            map_counter[map_info.code] +=1
                            #print("Known objective: ".ljust(20) + x[1] + " map: " + map_info.name)
                            stat_entry = StatLine("temp",line_order, round_order,round_num,obj_offender,"Objective", obj_type, obj_defender)
                        else:
                            if ("the War Documents" in x[1]):
                                "This objective repeats in various maps so we are going to skip it"
                            else:
                                print("---------------Unknown objective: ".ljust(20) + x[1])
                    else:
                        stat_entry = None
                    matched = key
                    break
            
            #bad panzer special handling
            if matched == None:    
                y = re.search("^\[skipnotify\](.*) was killed by (.*)",line)  
                if y:
                    value.event = Const.EVENT_KILL
                    stat_entry = StatLine("temp",line_order, round_order,1,y[2],value.event, Const.WEAPON_PANZER, y[1])
                    #print("Bad console line: " + line + "--- processed as " + stat_entry.toString())
            #end of bad panzer handling
            
            if stat_entry:
                processedLine = "Logged" #stat_entry.toString()
                tmp_log_events.append(stat_entry)
                line_num = line_num + 1
                #print("Added " + processedLine)
            elif ospline is not None:
                processedLine = "OSPline"
            else:
                #
                processedLine = "Ignored"
            write_line = str(line_order).ljust(5) + "roundNum " + str(round_order).ljust(2)  + value.event.ljust(20) + processedLine.ljust(10) + line.rstrip() + "\n"
            
            #write the line processing notes into debig file
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
        except NameError:
            print("Nothing was processed")
            return None
        else:
            matchesdf = pd.DataFrame([vars(e) for e in matches])
            logdf = self.handle_renames(renames, ["killer","victim"], logdf, False)
            stats_all = self.handle_renames(renames, ['player_strip','Killer','team_captain','OSP_Player'], stats_all, True)            
            logdf = logdf[['round_guid','line_order','round_order','round_num','event','killer','mod','victim']]
            time_end_process_log = _time.time()
            print ("Time to process " + self.read_file + " is " + str(round((time_end_process_log - time_start_process_log),2)) + " s")
            return {"logdf":logdf, "stats":stats_all, "matchesdf":matchesdf}
            
        
        
