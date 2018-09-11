class Const:
    
    EVENT_LOGFILE_TIMESTAMP = "timestamp"
    
    EVENT_KILL = "kill"
    EVENT_SUICIDE = "Suicide"
    EVENT_MOD_WORLD = "World"
    EVENT_MOD_SLASHKILL = "/kill"
    EVENT_TEAMKILL = "Team kill"
    
    EVENT_RENAME="Renamed"
    EVENT_OBJECTIVE = "Objective"
    EVENT_CHAT = "Chat"
    EVENT_CALLVOTE = "Callvote"
    EVENT_KICK = "Kick"
    EVENT_START = "Start"
    EVENT_PAUSE = "Pause"
    
    EVENT_MAIN_TIMELIMIT = "Timelimit hit"
    EVENT_MAIN_SERVER_TIME = "Server time set"
    
    EVENT_OSP_STATS_ALLIES = "stats_al"
    EVENT_OSP_STATS_AXIS = "stats_ax"
    EVENT_OSP_STATS_ACCURACY = "accuracy_round"
    
    EVENT_OSP_TIME_SET = "osp_time_set"
    EVENT_OSP_NOT_REACHED = "osp_time_not_reached"
    EVENT_OSP_REACHED = "osp_time_reached"
    
    
    
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
    
   
    line_types = [
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
            ["info","^\[skipnotify\]\*\*\* INFO:(.*)",EVENT_OBJECTIVE, "", False],
            ["teamchat", "^\[skipnotify\]\((.*)\: (.*)", EVENT_CHAT,"", False],
            ["vote", "^\[skipnotify\](.*) called a vote", EVENT_CALLVOTE,"", False],
            ["kick", "^\[skipnotify\](.*) player kicked", EVENT_KICK,"", False],
            ["fightline", "^\[skipnotify\]FIGHT\!(.*)",EVENT_START,"",False],
            ["pause", "^\[skipnotify\](.*) PAUSED",EVENT_PAUSE, "", False ],
            ["ospaxis", "^Axis",EVENT_OSP_STATS_AXIS, "", False],
            ["ospallies", "^Allies",EVENT_OSP_STATS_ALLIES, "", False],
            #time indicators
            ["roundind", "^Accuracy info for:", EVENT_OSP_STATS_ACCURACY, "", False],
            #main 
            ["timelimitmain", "^\[skipnotify\]Timelimit hit\.",EVENT_MAIN_TIMELIMIT, "", False],
            ["clocksetmain", "^\[skipnotify\]Server: timelimit changed to (.*)",EVENT_MAIN_SERVER_TIME, "", False],
            #osp
            ["fullholdosp", "^\[skipnotify\]>>> Objective NOT reached in time \((.*)\)",EVENT_OSP_NOT_REACHED, "", False],
            ["clocksetosp", "^\[skipnotify\]>>> Clock set to: (.*)",EVENT_OSP_TIME_SET, "", False],
            ["clocklostosp", "^\[skipnotify\]>>> Objective reached at (.*) \(original: (.*)\)",EVENT_OSP_REACHED, "", False],
            #file info
            ["logdate","^logfile opened on(.*)", EVENT_LOGFILE_TIMESTAMP, "", False],
            ["teamchat","^\[skipnotify\]\((.*)\: (.*)", EVENT_CHAT,"", False],
            ["chat","^\[skipnotify\](.*)\: (.*)", EVENT_CHAT,"", False]
            ]
    
    osp_columns=["player", "team","frags","deaths","suicides","teamkills","Eff", "gibs","dmg","dmr","teamdmg","score"]



class LogLine:
    
    def matchid(self):
        return "MATCH_ID"
          
    def __init__(self, line_type, regex, event, mod, stats):
         self.line_type = line_type
         self.regex = regex
         self.event = event
         self.mod = mod
         self.stats = stats
    
    def LoadLogLines():
        log_lines = {}  
        for i in Const.line_types:
            log_lines[i[0]] = LogLine(i[0], i[1],i[2], i[3],i[4])
        return log_lines
