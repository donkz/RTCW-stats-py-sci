import re
import pandas as pd
import os.path
from datetime import datetime

from utils.rtcwcolors import stripColors , setup_colors
from constants.logtext import Const, LogLine
from textsci.teams import add_team_name, get_captain

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
      
    def __init__(self, file_date, log_date, round_guid, round_order, round_num, players, final_round, winner):
         self.file_date = file_date
         self.log_date = log_date
         self.round_guid = round_guid
         self.round_order=round_order
         self.round_num=round_num
         self.players = players
         self.final_round = final_round
         self.winner = winner

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

    def get_match_guid(stats_all):
        return get_captain(stats_all, "Allies") + "-" + get_captain(stats_all, "Axis") + "-" + "-".join(stats_all.sort_values("kill")["kill"].astype(int).astype(str))

    def process_log(self):
        #init
        line_order = 0
        round_order = 0
        round_num = 1
        game_started = False
        game_paused = False
        line_num = 0
        log_events = []
        osp_stats = {}
        log_date = ""
        
        #const
        colors = setup_colors()
        log_lines = LogLine.LoadLogLines()
    
        #get to work    
        file = open(self.debug_file,"w") 
        lines = self.openFile()
        fileLen = len(lines)-1
    
        file_date = self.get_file_date()
        file_size = self.get_file_size()
    
        #go through each line in the file
        for x in range(0,fileLen):
            line = stripColors(lines[x], colors)
            matched = None
            stat_entry = None
            ospline = None
            
            #for each line in the file loop through all possible log line types and see which type of line it is
            for key, value in log_lines.items():
                x = re.search(value.regex, line)
                #if it looks like something we recognize (x is not None) then add this line appropriately
                if x:
                    line_order = line_order + 1
                    
                    if value.event == Const.EVENT_START and game_paused == False:
                        game_started = True
                        round_order = round_order + 1
                        ospDF = pd.DataFrame(columns=Const.osp_columns)
                        print("Round begin")
                    
                    if value.event == Const.EVENT_PAUSE:
                        game_paused = True
                        
                    if value.event == Const.EVENT_MAIN_TIMELIMIT or value.event == Const.EVENT_MAIN_SERVER_TIME: #need to add all ending scenarios here
                        game_started = False
                        game_paused = False
                        print("Round end")
                        
                    if value.event == Const.EVENT_OSP_REACHED:
                        game_started = False
                        game_paused = False
                        osp_stats[round_order] = ospDF
                        print("Round 2 end osp stats. time " + x[1] + " original " +x[2] )
                        
                    if value.event == Const.EVENT_OSP_NOT_REACHED:
                        game_started = False
                        game_paused = False
                        osp_stats[round_order] = ospDF
                        print("Round 2 end osp stats " + x[1])
                    
                    if value.event == Const.EVENT_OSP_TIME_SET:
                        game_started = False
                        game_paused = False
                        osp_stats[round_order] = ospDF
                        print("Round 1 end osp stats " + x[1])
                         
                    if value.event == Const.EVENT_OSP_STATS_ALLIES or value.event == Const.EVENT_OSP_STATS_AXIS:
                        ospline = self.process_OSP_line(line)
                        ospDF = ospDF.append(ospline)
                     
                    if value.event == Const.EVENT_OSP_STATS_ACCURACY: 
                        #not everything deserves it's own function
                        #Accuracy info for: /mute doNka (2 Rounds)
                        #get round number
                        round_num = int(line.split("(")[-1].split(" ")[0]) 
                    
                    if value.event == Const.EVENT_LOGFILE_TIMESTAMP:
                        #Sun Apr 08 18:51:44 2018
                        log_date = str(datetime.strptime(x[1].strip(), "%a %b %d %H:%M:%S %Y" ))
                    
                    if len(x.groups()) > 0: 
                        victim = x[1]
#                if killer.find("doNka") > 0: print(line)
                    else: 
                        victim = ""
                    if len(x.groups()) > 1:
                        killer = x[2]
                    else: 
                        killer = ""
                    
                    if(value.stats and game_started):
                       stat_entry = StatLine("temp",line_order, round_order,round_num,killer,value.event, value.mod, victim)
                    elif value.event == Const.EVENT_OBJECTIVE:
                        #insert processing here for who and what
                        testkiller = "Allies"
                        testvictim = "Axis"
                        testobj = "Flag"
                        stat_entry = StatLine("temp",line_order, round_order,round_num,testkiller,"Objective", testobj, testvictim)
                        #print(stat_entry.toString())
                    else:
                        stat_entry = None
                    matched = key
                    break
            
            #bad panzer handling
            if matched == None:    
                y = re.search("^\[skipnotify\](.*) was killed by (.*)",line)  
                if y:
                    stat_entry = StatLine("temp",line_order, round_order,1,y[2],Const.EVENT_KILL, Const.WEAPON_PANZER, y[1])
                    #print("Bad console line: " + line + "--- processed as " + stat_entry.toString())
            #end of bad panzer handling
            
            if stat_entry:
                processedLine = "Logged" #stat_entry.toString()
                log_events.append(stat_entry)
                line_num = line_num + 1
                #print("Added " + processedLine)
            elif ospline is not None:
                processedLine = "ospline"
            else:
                #
                processedLine = "Ignored"
            write_line = value.event + processedLine + "\t" + line.rstrip() + "\n"
            
            #write the line processing notes into debig file
            file.write(write_line)
        
        #close debig file        
        file.close() 
        
        logdf = pd.DataFrame([vars(e) for e in log_events])
        logdf = logdf[['round_guid','line_order','round_order','round_num','event','killer','mod','victim']]
        return {"logdf":logdf, "ospdf":ospDF, "matchesdf":None}
