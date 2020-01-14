'''
This class contains constants- strings, arrays, columns specific to RTCW and this application
Note: map constants are in maps.py
'''


class Const:
    
    TEXT_PLAYER_SEPARATOR = "%"
    
    EVENT_LOGFILE_TIMESTAMP = "timestamp"
    
    EVENT_KILL = "kill"
    EVENT_SUICIDE = "Suicide"
    EVENT_MOD_WORLD = "World"
    EVENT_MOD_SLASHKILL = "/kill"
    EVENT_TEAMKILL = "Team kill"
    
    EVENT_RENAME="Renamed"
    
    EVENT_OBJ_AXIS_RETURN = "Axis Return Obj"
    EVENT_OBJ_ALLIES_RETURN = "Allies Return Obj"
    EVENT_OBJ_AXIS_STOLE = "Axis Stole Obj"
    EVENT_OBJ_ALLIES_STOLE = "Allies Stole Obj"
    
    EVENT_OBJECTIVE = "Objective"
    EVENT_CHAT = "Chat"
    EVENT_TEAM_CHAT = "Team Chat"
    EVENT_VSAY_CHAT = "Vsay chat"
    EVENT_CALLVOTE = "Callvote"
    EVENT_KICK = "Kick"
    EVENT_START = "Start"
    EVENT_PAUSE = "Pause"
    
    EVENT_MAIN_TIMELIMIT = "Timelimit hit"
    EVENT_MAIN_SERVER_TIME = "Server time set"
    
    EVENT_OSP_STATS_START = "OSP Stats begin"
    EVENT_OSP_STATS_MID = "Skip osp Axis totals"
    EVENT_OSP_STATS_END = "OSP Stats end"
    EVENT_OSP_STATS_ALLIES = "stats_al"
    EVENT_OSP_STATS_AXIS = "stats_ax"
    EVENT_OSP_STATS_ACCURACY = "accuracy_round"
    
    EVENT_OSP_TIME_SET = "osp_time_set"
    EVENT_OSP_NOT_REACHED = "osp_time_not_reached"
    EVENT_OSP_REACHED = "osp_time_reached"
    
    CONSOLE_PASSWORD_RCON = "Rcon password"
    CONSOLE_PASSWORD_REF =  "Ref password"
    CONSOLE_PASSWORD_SERVER = "Server password"
    
    EVENT_DATETIME_OSP_MAP_LOAD = "Datetime OSP"
    EVENT_DATETIME_SCREENSHOT = "Screenshot"
    EVENT_DATETIME_DEMO = "Record demo"
    EVENT_DATETIME_OSP_SAVE_STATS = "OSP file"
    
    WEAPON_GRENADE = "Grenade"
    WEAPON_PANZER = "Panzerfaust"
    WEAPON_THOMPSON = "Thompson"
    WEAPON_MP40 = "MP40"
    WEAPON_STEN = "Sten"
    WEAPON_LUGER = "Luger"
    WEAPON_COLT = "Colt"
    WEAPON_SNIPER = "Sniper"
    WEAPON_MAUSER = "Sniper"
    WEAPON_VENOM = "Venom"
    WEAPON_FLAME = "Flame"
    WEAPON_KNIFE = "Knife"
    WEAPON_AS = "Airstrike"
    WEAPON_ART = "Artillery"
    WEAPON_DYN = "Dynamite"
    WEAPON_MG42 = "MG42"
    
    CLASS_PANZER = "P"
    CLASS_LEUTENANT = "L"
    CLASS_SNIPER = "S"
    CLASS_VENOM = "V"
    CLASS_FLAMER = "F"
    
    STAT_BASE_KILLER = "Killer" #equivalent to player name
    STAT_BASE_KILL = "Kills"
    STAT_BASE_DEATHS = "Deaths"
    STAT_BASE_TK = "TK"
    STAT_BASE_TKd = "TKd"
    STAT_BASE_SUI = "Suicides"
    STAT_BASE_ALLDEATHS = "All_Deaths"
    
    NEW_COL_MATCH_DATE = "match_date"
    
    
    #                                Kll Dth Sui TK Eff Gib DG    DR      TD  Score
    #line = "Allies /mute doNka      19   3   0  0  86   5  2367  1435    0     48"
    #line = "Allies /mute sem        19  10   2  2  65   4  3588  2085  226     46"
    STAT_OSP_SUM_PLAYER = "OSP_Player"
    STAT_OSP_SUM_TEAM = "OSP_Team"
    STAT_OSP_SUM_FRAGS = "OSP_Kills"
    STAT_OSP_SUM_DEATHS = "OSP_Deaths"
    STAT_OSP_SUM_SUICIDES = "OSP_Suicides"
    STAT_OSP_SUM_TK = "OSP_TK"
    STAT_OSP_SUM_EFF = "OSP_Eff"
    STAT_OSP_SUM_GIBS = "OSP_Gibs"
    STAT_OSP_SUM_DMG = "OSP_Damage_Given"
    STAT_OSP_SUM_DMR = "OSP_Damage_Received"
    STAT_OSP_SUM_TEAMDG = "OSP_Team_Damage"
    STAT_OSP_SUM_SCORE = "OSP_Score"
    osp_columns=[STAT_OSP_SUM_PLAYER, STAT_OSP_SUM_TEAM, STAT_OSP_SUM_FRAGS, STAT_OSP_SUM_DEATHS, STAT_OSP_SUM_SUICIDES, STAT_OSP_SUM_TK, STAT_OSP_SUM_EFF, STAT_OSP_SUM_GIBS, STAT_OSP_SUM_DMG, STAT_OSP_SUM_DMR, STAT_OSP_SUM_TEAMDG, STAT_OSP_SUM_SCORE]
    #osp_columns=["player", "team","frags","deaths","suicides","teamkills","Eff", "gibs","dmg","dmr","teamdmg","score"]

    STAT_POST_ADJSCORE = "AdjScore"
    
    mod_by_type = { 
                    "Guns" : [WEAPON_MP40,WEAPON_THOMPSON,WEAPON_STEN], 
                    "Pistols": [WEAPON_LUGER,WEAPON_COLT],
                    "Explosives" : [WEAPON_PANZER, WEAPON_GRENADE, WEAPON_AS, WEAPON_ART],
                    "Random" : [WEAPON_SNIPER, WEAPON_VENOM, WEAPON_FLAME, WEAPON_DYN, WEAPON_MG42, WEAPON_KNIFE]
                   }
    
   
    line_types = [
            #kill types            
            ["grenade", "^\[skipnotify\](.*) was exploded by (.*)\'s grenade",EVENT_KILL, WEAPON_GRENADE,True],
            ["Panzerfaust","^\[skipnotify\](.*) was blasted by (.*)\'s Panzerfaust",EVENT_KILL, WEAPON_PANZER, True],
            ["thompson", "^\[skipnotify\](.*) was killed by (.*)\'s Thompson",EVENT_KILL, WEAPON_THOMPSON, True],
            ["mp40", "^\[skipnotify\](.*) was killed by (.*)\'s MP40",EVENT_KILL, WEAPON_MP40, True],
            ["sten", "^\[skipnotify\](.*) was killed by (.*)\'s Sten",EVENT_KILL,WEAPON_STEN, True],
            ["luger", "^\[skipnotify\](.*) was killed by (.*)\'s Luger 9mm",EVENT_KILL,WEAPON_LUGER, True],
            ["colt", "^\[skipnotify\](.*) was killed by (.*)\s's \.45ACP 1911",EVENT_KILL,WEAPON_COLT, True],
            ["sniper", "^\[skipnotify\](.*) was killed by (.*)\'s sniper rifle",EVENT_KILL,WEAPON_SNIPER, True],
            ["mauser", "^\[skipnotify\](.*) was killed by (.*)\'s Mauser",EVENT_KILL,WEAPON_MAUSER, True],
            ["venom", "^\[skipnotify\](.*) was ventilated by (.*)\'s Venom",EVENT_KILL,WEAPON_VENOM, True],
            ["flamethrower", "^\[skipnotify\](.*) was cooked by (.*)\'s flamethrower",EVENT_KILL,WEAPON_FLAME, True],
            ["knife", "^\[skipnotify\](.*) was stabbed by (.*)\'s knife",EVENT_KILL,WEAPON_KNIFE, True],
            ["support", "^\[skipnotify\](.*) was blasted by (.*)\'s support fire",EVENT_KILL,WEAPON_AS, True],
            ["artillery", "^\[skipnotify\](.*) was shelled by (.*)\'s artillery support",EVENT_KILL,WEAPON_ART, True],
            ["dynamite", "^\[skipnotify\](.*) was blasted by (.*)\'s dynamite",EVENT_KILL,WEAPON_DYN, True],
            ["mg42", "^\[skipnotify\](.*) was perforated by (.*)\'s crew-served MG42",EVENT_KILL,WEAPON_MG42, True],
            ["crush", "^\[skipnotify\](.*) was crushed\.",EVENT_SUICIDE, EVENT_MOD_WORLD, True],
            ["died", "^\[skipnotify\](.*) died\.",EVENT_SUICIDE, EVENT_MOD_WORLD, True],
            ["drown", "^\[skipnotify\](.*) drowned\.",EVENT_SUICIDE, EVENT_MOD_WORLD, True],
            ["fell", "^\[skipnotify\](.*) fell to his death\.",EVENT_SUICIDE, EVENT_MOD_WORLD, True],
            ["Vaporized", "^\[skipnotify\](.*) vaporized himself\.",EVENT_SUICIDE, WEAPON_PANZER, True],
            ["artyd", "^\[skipnotify\](.*) fired-for-effect on himself\.",EVENT_SUICIDE, WEAPON_ART, True],
            ["canned", "^\[skipnotify\](.*) obliterated himself\.",EVENT_SUICIDE, WEAPON_AS, True],
            ["dynamited", "^\[skipnotify\](.*) dynamited himself to pieces\.",EVENT_SUICIDE, WEAPON_DYN, True],
            ["Dove", "^\[skipnotify\](.*) dove on his own grenade\.",EVENT_SUICIDE, WEAPON_GRENADE, True],
            ["rename","^\[skipnotify\](.*) renamed to (.*)",EVENT_RENAME, "",False],
            ["teamkill", "^\[skipnotify\](.*) WAS KILLED BY TEAMMATE (.*)",EVENT_TEAMKILL, "None", True],
            ["suicide","^\[skipnotify\](.*) killed himself",EVENT_SUICIDE, EVENT_MOD_SLASHKILL, True],
            ["info","^\[skipnotify\]\*\*\* INFO: (.*)",EVENT_OBJECTIVE, "", False],
            ["vote", "^\[skipnotify\](.*) called a vote", EVENT_CALLVOTE,"", False],
            ["kick", "^\[skipnotify\](.*) player kicked", EVENT_KICK,"", False],
            ["fightline", "^\[skipnotify\]FIGHT\!(.*)",EVENT_START,"",False],
            ["pause", "^\[skipnotify\](.*) PAUSED",EVENT_PAUSE, "", False ],
            #match ending main 
            ["ospbegin", "^TEAM   Player          Kll Dth Sui",EVENT_OSP_STATS_START, "", False],
            ["ospmid", "^Axis   Totals",EVENT_OSP_STATS_MID, "", False],
            ["ospend", "^Allies Totals",EVENT_OSP_STATS_END, "", False],
            ["ospaxis", "^Axis",EVENT_OSP_STATS_AXIS, "", False],
            ["ospallies", "^Allies",EVENT_OSP_STATS_ALLIES, "", False],
            ["roundind", "^Accuracy info for:", EVENT_OSP_STATS_ACCURACY, "", False],
            ["timelimitmain", "^\[skipnotify\]Timelimit hit\.",EVENT_MAIN_TIMELIMIT, "", False],
            ["clocksetmain", "^\[skipnotify\]Server: timelimit changed to (.*)",EVENT_MAIN_SERVER_TIME, "", False],
            #match ending osp
            ["fullholdosp", "^\[skipnotify\]>>> Objective NOT reached in time \((.*)\)",EVENT_OSP_NOT_REACHED, "", False],
            ["clocksetosp", "^\[skipnotify\]>>> Clock set to: (.*)",EVENT_OSP_TIME_SET, "", False],
            ["clocklostosp", "^\[skipnotify\]>>> Objective reached at (.*) \(original: (.*)\)",EVENT_OSP_REACHED, "", False],
            #file info
            ["logdate","^logfile opened on(.*)", EVENT_LOGFILE_TIMESTAMP, "", False],
                        
            #timestamps
            ["osploadtime", "^\[skipnotify\]Current time: (.*)",EVENT_DATETIME_OSP_MAP_LOAD, "", False],
            ["ospdemotime", "^Match starting...recording to (.*)", EVENT_DATETIME_DEMO,"", False],
            ["ospstattime", "^>>> Stats recorded to: (.*)", EVENT_DATETIME_OSP_SAVE_STATS,"", False],
            ["ospjpegtime", "^Wrote screenshots\\/(.*)\\/(.*)", EVENT_DATETIME_SCREENSHOT,"", False],
            
            #chats must be below everything because they match just about anything
            ["teamchat","^\[skipnotify\]\((.*)\: (.*)", EVENT_TEAM_CHAT,"", False],
            ["vsay","^\[skipnotify\]\: \((.*)\)\: (.*)", EVENT_VSAY_CHAT,"", False],
            ["chat","^\[skipnotify\](.*)\: (.*)", EVENT_CHAT,"", False],
            
            #dont pass passwords further down stream
            ["passwordserv","^\]\/password (.*)", CONSOLE_PASSWORD_SERVER,"", False],
            ["passwordref","^\]\/ref (.*)", CONSOLE_PASSWORD_REF,"", False],
            ["passwordrcon","^\]\/rconpassword (.*)", CONSOLE_PASSWORD_RCON,"", False]
            #the following lines are in maps file
            #Axis engineer disarmed
            #Allied engineer disarmed
            #Allies have stolen
            #Allies have returned
            #Axis have stolen
            #Axis have returned
            ]

'''
class Logline represents a single line of text processed and prepared for storage in standardized way
'''
class LogLine:
             
    def __init__(self, line_type, regex, event, mod, stats):
         self.line_type = line_type # line ID. Not used for other than debugging
         self.regex = regex         # match on this expression
         self.event = event         # what recognized in a given line
         self.mod = mod             # method of death
         self.stats = stats         # True or False - if the line is recordable or just logical
    
    def LoadLogLines():
        log_lines = {}  
        for i in Const.line_types:
            log_lines[i[0]] = LogLine(i[0], i[1],i[2], i[3],i[4])
        return log_lines
