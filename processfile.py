import re
import pandas as pd
import os.path
from datetime import datetime

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
        
    def summarize_round(self, logdf, ospdf):
        kills = logdf[logdf["event"].isin([Const.EVENT_TEAMKILL,Const.EVENT_SUICIDE,Const.EVENT_KILL])].groupby(["killer","event"])["event"].count().unstack()
        deaths = logdf[logdf["event"].isin([Const.EVENT_TEAMKILL,Const.EVENT_SUICIDE,Const.EVENT_KILL])].groupby(["victim","event"])["event"].count().unstack()

        stats  = pd.DataFrame(kills[Const.EVENT_KILL])
        stats["TK"]  = kills[Const.EVENT_TEAMKILL]
        stats["Deaths"]= deaths[Const.EVENT_KILL]
        stats["TKd"]= deaths[Const.EVENT_TEAMKILL]
        stats["Suicide"]= deaths[Const.EVENT_SUICIDE]
        stats["Deaths2"]= stats["Deaths"] + stats[Const.EVENT_SUICIDE]
        stats = stats.drop(index='') #empty players
        stats = stats.fillna(0)
        pd.options.display.float_format = '{:0,.0f}'.format
        ospdf.index = ospdf["player"]
        stats_all = stats.join(ospdf) #Totals fall out naturally
        #print(stats_all)
        stats_all = add_team_name(stats_all)
        return stats_all

    def process_log(self):
        #Initialize local variables
        line_order = 0
        round_order = 0
        round_num = 1
        game_started = False
        game_paused = False
        reading_osp_stats = False
        line_num = 0
        matches = []
        osp_lines = []
        log_date = ""
        log_date = str(datetime.now())
        
        tmp_log_events = []
        
        #Load in Constants
        colors = setup_colors()
        log_lines = LogLine.LoadLogLines()
    
        #Prep debug log
        debug_log = open(self.debug_file,"w")
        debug_log.write("line".ljust(5) + "roundNum " + "##".ljust(2)  + "Event".ljust(20) + "Logged as".ljust(10) + "LineText".rstrip() + "\n")
        log_file_lines = self.openFile()
        fileLen = len(log_file_lines)-1
    
        file_date = self.get_file_date()
        file_size = self.get_file_size()
        
        map_class = ConstMap
        map_class.load_maps(map_class)
        announcements = map_class.transpose_by_obj(map_class)
        map_counter = Counter()
        
    
        #go through each line in the file
        for x in range(0,fileLen):
            line = stripColors(log_file_lines[x], colors)
            matched = None
            stat_entry = None
            ospline = None
            
            #for that line loop through all possible log line types and see which type of line it is
            for key, value in log_lines.items():
                x = re.search(value.regex, line)
                #if it looks like something we recognize (x is not None) then add this line appropriately
                if x:
                    line_order = line_order + 1
                    
                    if value.event == Const.EVENT_LOGFILE_TIMESTAMP: #beginning of every logfile
                        #Sun Apr 08 18:51:44 2018
                        log_date = str(datetime.strptime(x[1].strip(), "%a %b %d %H:%M:%S %Y" ))
                    
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
                                         
                    if value.event == Const.EVENT_PAUSE: #game paused. Unpause will result in FIGHT line again
                        game_paused = True

                    if value.event == Const.EVENT_OSP_STATS_ACCURACY: #happens aat the end of every round for a player that is ON A TEAM
                        #Accuracy info for: /mute doNka (2 Rounds)
                        #get round number
                        new_match_line.round_num = int(line.split("(")[-1].split(" ")[0])
                        
                    if value.event == Const.EVENT_OSP_STATS_START and reading_osp_stats == False:
                        reading_osp_stats = True
                        
                    if value.event == Const.EVENT_OSP_STATS_END:
                        reading_osp_stats = False
                        osp_guid = get_round_guid_osp(osp_lines)
                        print("Processing OSP stats id: " + osp_guid)
                        osp_lines = []
                    
                    if value.event == Const.EVENT_OSP_STATS_MID:
                        #do nothing for this line
                        break
                    
                    if value.event == Const.EVENT_OSP_STATS_ALLIES or value.event == Const.EVENT_OSP_STATS_AXIS: #OSP team stats per player
                        osp_line = self.process_OSP_line(line)
                        ospDF = ospDF.append(osp_line)
                        osp_lines.append(line)
                        
                        
                    if value.event == Const.EVENT_MAIN_TIMELIMIT: #happens before OSP stats if the time ran out
                        game_started = False
                        game_paused = False
                        new_match_line.defense_hold = 1
                        # implement timelimit hit. It appears before OSP stats only when clock ran out
                                           
                    if value.event == Const.EVENT_MAIN_SERVER_TIME: 
                        #happens after OSP stats, but not when map changes
                        #also happens anytime ref changes timelimit 
                        game_started = False
                        game_paused = False
                        #new_match_line.round_time = int(float(x[1])*60) # this comes after OSP stats and fucks everything up
                        
                    if value.event == Const.EVENT_OSP_REACHED: #osp round 2 defense lost
                        game_started = False
                        game_paused = False
                        new_match_line.defense_hold = 0
                        time1 = x[1].strip().split(":")
                        roundtime = int(time1[0])*60 + int(time1[1])
                        #print("round 2 time is " + str(roundtime))
                        new_match_line.round_time = roundtime 
                        time2 = x[2].strip().split(":")
                        new_match_line.round_diff = int(time2[0])*60 + int(time2[1]) - roundtime
                        #print("round times(t1,t2,diff) " + x[1].strip() + " " + x[2].strip() + " " + str(new_match_line.round_diff))
                        new_match_line.round_num = 2
                        
                    if value.event == Const.EVENT_OSP_NOT_REACHED: #osp round 2 defense lost
                        game_started = False
                        game_paused = False
                        time = x[1].strip().split(":")
                        roundtime = int(time[0])*60 + int(time[1])
                        new_match_line.round_diff = 0
                        new_match_line.defense_hold = 1
                        new_match_line.round_num = 2
                        new_match_line.round_time = roundtime
                        
                    
                    if value.event == Const.EVENT_OSP_TIME_SET: #osp round 1 end. Not indicative of win or loss
                        game_started = False
                        game_paused = False
                        if (new_match_line.defense_hold !=1): #do we know that it was fullhold from "Timelimit hit"?
                            new_match_line.defense_hold = 0
                        time = x[1].strip().split(":")
                        new_match_line.round_time = int(time[0])*60 + int(time[1])
                        new_match_line.round_num = 1
                        #TEMP_STORAGE
                        #tmp_r1_time = new_match_line.round_time
                        tmp_r1_fullhold = new_match_line.defense_hold
                        #EO TEMP STORAGE
                        if(new_match_line.defense_hold != 1): #TODO do this through maps info to get timelimit and round difference
                            new_match_line.defense_hold = 0
                    
                    ######################################################################
                    #####################wrap up the round################################
                    ######################################################################
                    if value.event == Const.EVENT_OSP_REACHED or value.event == Const.EVENT_OSP_NOT_REACHED or value.event == Const.EVENT_OSP_TIME_SET:
                        print("Objectives related to maps: " + str(map_counter))
                        #if either of the 3 above, dump stats
                        map_code = map_counter.most_common(1)[0][0]
                        map_counter = Counter() #reset it
                        tmp_logdf = pd.DataFrame([vars(e) for e in tmp_log_events])
                        tmp_stats_all = self.summarize_round(tmp_logdf, ospDF)
                        tmp_stats_all["round_order"] = round_order
                        tmp_stats_all = add_team_name(tmp_stats_all)
                        round_guid = get_round_guid_client_log(tmp_stats_all)
                        print("Processed log stats id: " + round_guid)
                        tmp_stats_all["round_guid"] = round_guid
                        tmp_stats_all["osp_guid"] = osp_guid
                        tmp_stats_all["round_num"] = new_match_line.round_num
                        
                        tmp_map = map_class.maps[map_code]
                        tmp_stats_all["map"] = tmp_map.name
                        new_match_line.map = tmp_map.name
                        new_match_line.players = get_player_list(tmp_stats_all)
                        
                        #print(tmp_stats_all.columns.values)
                        #print(tmp_stats_all["team"])
                        #print(tmp_map.defense)
                        #print(tmp_stats_all[tmp_stats_all["team"] == tmp_map.defense].index)
                        #print(tmp_stats_all.loc[tmp_stats_all[tmp_stats_all["team"] == tmp_map.defense].index])

                        tmp_stats_all.loc[tmp_stats_all[tmp_stats_all["team"] == tmp_map.defense].index,"side"] = "Defense"
                        tmp_stats_all.loc[tmp_stats_all[tmp_stats_all["team"] == tmp_map.offense].index,"side"] = "Offense"
                        #print(tmp_stats_all.columns.values)

                        if value.event == Const.EVENT_OSP_TIME_SET:
                            #round 1
                            new_match_line.round_diff = tmp_map.timelimit*60 - new_match_line.round_time
                            tmp_stats_all.loc[tmp_stats_all[tmp_stats_all["team"] == tmp_map.offense].index,"round_win"] = 1 
                            tmp_stats_all.loc[tmp_stats_all[tmp_stats_all["team"] == tmp_map.defense].index,"round_win"] = 0
                            tmp_stats_all["game_result"] = "R1MSB"
                            new_match_line.winner = tmp_map.offense
                        if value.event == Const.EVENT_OSP_NOT_REACHED:
                            #round 2 DEFENSE HELD (WON OR DRAW)
                            if tmp_r1_fullhold == 1:
                                tmp_stats_all.loc[tmp_stats_all[tmp_stats_all["team"] == tmp_map.offense].index,"round_win"] = 0 
                                tmp_stats_all.loc[tmp_stats_all[tmp_stats_all["team"] == tmp_map.defense].index,"round_win"] = 1 #they get a round win , but a game win is full hold
                                tmp_stats_all["game_result"] = "FULLHOLD"
                                new_match_line.winner = "Draw"
                            elif tmp_r1_fullhold == 0:
                                tmp_stats_all.loc[tmp_stats_all[tmp_stats_all["team"] == tmp_map.offense].index,"round_win"] = 0 
                                tmp_stats_all.loc[tmp_stats_all[tmp_stats_all["team"] == tmp_map.defense].index,"round_win"] = 1
                                tmp_stats_all.loc[tmp_stats_all[tmp_stats_all["team"] == tmp_map.defense].index,"game_result"] = "WON"
                                tmp_stats_all.loc[tmp_stats_all[tmp_stats_all["team"] == tmp_map.offense].index,"game_result"] = "LOST"
                                new_match_line.winner = tmp_map.defense
                            else:
                                print("bad round 2 winner status")
                            del tmp_r1_fullhold
                            #del tmp_r1_time 
                        if value.event == Const.EVENT_OSP_REACHED:
                            #round 2 DEFENSE LOST THE GAME
                            tmp_stats_all.loc[tmp_stats_all[tmp_stats_all["team"] == tmp_map.offense].index,"round_win"] = 1 
                            tmp_stats_all.loc[tmp_stats_all[tmp_stats_all["team"] == tmp_map.defense].index,"round_win"] = 0 
                            tmp_stats_all.loc[tmp_stats_all[tmp_stats_all["team"] == tmp_map.defense].index,"game_result"] = "LOST"
                            tmp_stats_all.loc[tmp_stats_all[tmp_stats_all["team"] == tmp_map.offense].index,"game_result"] = "WON"
                            new_match_line.winner = tmp_map.offense
                            del tmp_r1_fullhold
                            #del tmp_r1_time 
      
                        
                        tmp_logdf["round_guid"] = round_guid
                        tmp_logdf["round_num"] = new_match_line.round_num
                        new_match_line.round_guid = round_guid
                        new_match_line.osp_guid = osp_guid
                        #print(str(new_match_line.round_diff))
                        matches.append(new_match_line)
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
#                if killer.find("doNka") > 0: print(line)
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
                    if(value.stats and game_started):
                       stat_entry = StatLine("temp",line_order, round_order,round_num,killer,value.event, value.mod, victim)
                    elif value.event == Const.EVENT_OBJECTIVE:
                        #insert processing here for who and what
                        if(x[1] in announcements):                       
                            announcement_values = announcements[x[1]]
                            map_info= map_class.maps[announcement_values[1]]                      
                            obj_offender = map_info.offense
                            obj_defender = map_info.defense
                            obj_type = announcement_values[0]
                            map_counter[map_info.code] +=1
                            print("Known objective: ".ljust(20) + x[1] + " map: " + map_info.name)
                            stat_entry = StatLine("temp",line_order, round_order,round_num,obj_offender,"Objective", obj_type, obj_defender)
                        else:
                            print("Unknown objective: ".ljust(20) + x[1])
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
        matchesdf = pd.DataFrame([vars(e) for e in matches])
        #print(matchesdf["round_diff"])
        logdf = logdf[['round_guid','line_order','round_order','round_num','event','killer','mod','victim']]
        return {"logdf":logdf, "stats":stats_all, "matchesdf":matchesdf}
