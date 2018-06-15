import re
import os.path
from datetime import datetime
import pandas as pd
import numpy as np
import time


def openFile(filename):
    with open(filename,"r") as ins:
        lines = []
        for line in ins:
            lines.append(line)
        return lines

def setup_colors():
    '''Make an array for stripColors function'''
    colors_arr = []
    for x in range(33,126):
        colors_arr.append("^"+chr(x))
    return colors_arr

colors = setup_colors()
    
def stripColors(line):
    '''Strip character combinations like ^7don^eN^7ka to doNka'''
    ret = line
    for color in colors:
        ret = ret.replace(color,"")
    return ret;  

class LogLine:
    
    def matchid(self):
        return "MATCH_ID"
          
    def __init__(self, line_type, regex, event, mod, stats):
         self.line_type = line_type
         self.regex = regex
         self.event = event
         self.mod = mod
         self.stats = stats
         
class StatLine:
    
    def toString(self):
        vars =  [str(self.match_guid),str(self.line_order),str(self.round_order),str(self.round_num), str(self.killer),str(self.event),str(self.mod),str(self.victim)]
        return ",".join(vars)
    
    def __init__(self, match_guid, line_order, round_order,round_num, killer, event, mod, victim):
         self.match_guid=match_guid
         self.line_order=line_order
         self.round_order=round_order
         self.round_num=round_num
         self.killer=killer
         self.event=event
         self.mod=mod
         self.victim=victim

#Disassemble the following lines into a dataframe
#                                Kll Dth Sui TK Eff Gib DG    DR      TD  Score
#line = "Allies /mute doNka      19   3   0  0  86   5  2367  1435    0     48"
#line = "Allies /mute sem        19  10   2  2  65   4  3588  2085  226     46"
def process_OSP_line(line):
    tokens = re.split("\s+", line)    
    player = " ".join(tokens[1:len(tokens)-11])
    temp = pd.DataFrame([[player, tokens[0],tokens[-11],tokens[-10],tokens[-9],tokens[-8],tokens[-7],tokens[-6],tokens[-5],tokens[-4],tokens[-3],tokens[-2]]], columns=osp_columns)
    return temp

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
EVENT_DEF_WIN = "Defense win"

EVENT_OSP_STATS_ALLIES = "stats_al"
EVENT_OSP_STATS_AXIS = "stats_ax"

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

osp_columns=["player", "team","frags","deaths","suicides","teamkills","Eff", "gibs","dmg","dmr","teamdmg","score"]

line_types = [
        ["grenade", "^\[skipnotify\](.*) was exploded by (.*)\'s grenade",EVENT_KILL, WEAPON_GRENADE,True],
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
        ["chat","^\[skipnotify\](.*)\: (.*)", EVENT_CHAT,"", False],
        ["teamchat", "^\[skipnotify\]\((.*)\: (.*)", EVENT_CHAT,"", False],
        ["vote", "^\[skipnotify\](.*) called a vote", EVENT_CALLVOTE,"", False],
        ["kick", "^\[skipnotify\](.*) player kicked", EVENT_KICK,"", False],
        ["fightline", "^\[skipnotify\]FIGHT\!(.*)",EVENT_START,"",False],
        ["fullhold", "^\[skipnotify\](.*) Objective NOT reached in time",EVENT_DEF_WIN, "", False],
        ["timelimit", "^\[skipnotify\]Timelimit hit\.",EVENT_DEF_WIN, "", False],
        ["pause", "^\[skipnotify\](.*) PAUSED",EVENT_PAUSE, "", False ],
        ["clockset", "^\[skipnotify\]Server: timelimit changed",EVENT_PAUSE, "", False],
        ["ospaxis", "^Axis",EVENT_OSP_STATS_AXIS, "", False],
        ["ospallies", "^Allies",EVENT_OSP_STATS_ALLIES, "", False]
        ]

log_lines = {}  
for i in line_types:
    log_lines[i[0]] = LogLine(i[0], i[1],i[2], i[3],i[4])
    
G_AXIS = "Axis"
G_ALLIES = "Allies"
O_WIN = "Offense win"
D_WIN = "Defense win"
O_FLAG = "Offense flag"
D_FLAG = "Defense flag"
O_OBJ = "Mid objective"


map_announce = {
        "mp_ice" : [
                  [O_WIN,"Offense win", "Axis transmitted the documents!"],
                  [D_FLAG,"Defense flag", "Allies reclaim the Shipping Halls!"],
                  [O_FLAG,"Offense flag","Axis captures the Shipping Halls!"],
                  [O_OBJ,"Service Door breached!"],
                  [O_OBJ,"Fortress Wall breached!"]
                ]
        }
        
class RTCWMap:
      
    def __init__(self, code, name, announcements, defense, offense, timelimit):
         self.code = code
         self.name = name
         self.announcements = announcements
         self.defense = defense
         self.offense = offense
         self.timelimit = timelimit
         
maps = {}  
maps["mp_ice"] = RTCWMap("mp_ice", "Ice", map_announce["mp_ice"], G_ALLIES, G_AXIS, 10)
        

    


##############################################
#        FILE PROCESSING                     #
##############################################

filename = "C:\\Users\\stavos\\Desktop\\python scripts\\rtcwconsole - r2.log"

def get_file_guid(filename):
    return str(datetime.fromtimestamp(os.path.getmtime(filename)).strftime('%Y-%m-%d')) + "-" + str(os.path.getsize(filename))

file_guid = get_file_guid(filename)

#print("created: %s" % datetime.fromtimestamp(os.path.getmtime(filename)).strftime('%Y-%m-%d'))
#print("created: %s" % os.path.getsize(filename))


lines = openFile(filename)
fileLen = len(lines)-1


file = open("C:\\Users\\stavos\\Desktop\\python scripts\\testfile.txt","w") 
line_order = 0
round_order = 0
game_started = False
game_paused = False
log_events = []

for x in range(0,fileLen):
    line = stripColors(lines[x])
    matched = None
    stat_entry = None
    
    for key, value in log_lines.items():
        x = re.match(value.regex,line)
        if x:
            line_order = line_order + 1
            
            if value.event == EVENT_START and game_paused == False:
                game_started = True
                round_order = round_order + 1
                ospDF = pd.DataFrame(columns=osp_columns)
            
            if value.event == EVENT_OBJECTIVE:
                print(line)
            
            if value.event == EVENT_PAUSE:
                game_paused = True
                
            if value.event == EVENT_DEF_WIN:
                game_started = False
                game_paused = False
            
            if value.event == EVENT_OSP_STATS_ALLIES or value.event == EVENT_OSP_STATS_AXIS:
                ospDF = ospDF.append(process_OSP_line(line))
            
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
               #print(line.rstrip())
               stat_entry = StatLine(file_guid,line_order, round_order,1,killer,value.event, value.mod, victim)
               #print(stat_entry.toString())
            else:
                stat_entry = None
            matched = key
            break
    
    if matched == None:    
        y = re.match("^\[skipnotify\](.*) was killed by (.*)",line)  
        if y:
            stat_entry = StatLine(file_guid,line_order, round_order,1,y[2],EVENT_KILL, WEAPON_PANZER, y[1])
            print("Bad console line: " + line + "--- processed as " + stat_entry.toString())
    
    if stat_entry:
        processedLine = stat_entry.toString()
        log_events.append(stat_entry)
    else:
        processedLine = "Ignored"
    write_line = line.rstrip() + "\t" + processedLine +"\n"
    
    
    file.write(write_line)
        
file.close() 

logdf = pd.DataFrame([vars(e) for e in log_events])

testkiller = "/mute doNka'"
testvictim = "/mute doNka"

print("Kills: " + str(len(logdf["killer"][logdf.killer == testkiller])))
print("Deaths: " + str(len(logdf["victim"][(logdf.victim == testvictim) & (logdf.event != "Team kill")])))
print("Death2: " + str(len(logdf["event"][(logdf.victim == testvictim) & (logdf.event == "kill")])))
print("Suicides: " + str(len(logdf["event"][(logdf.victim == testvictim) & (logdf.event == "Suicide")])))

kills = logdf.groupby(["killer","event"])["event"].count().unstack()
deaths = logdf.groupby(["victim","event"])["event"].count().unstack()

stats  = pd.DataFrame(kills[EVENT_KILL])
stats["TK"]  = kills[EVENT_TEAMKILL]
stats["Deaths"]= deaths[EVENT_KILL]
stats["TKd"]= deaths[EVENT_TEAMKILL]
stats["Suicide"]= deaths[EVENT_SUICIDE]
stats["Deaths2"]= stats["Deaths"] + stats[EVENT_SUICIDE]
stats = stats.drop(index='') #empty players
stats = stats.fillna(0)
pd.options.display.float_format = '{:0,.0f}'.format
ospDF.index = ospDF["player"]
stats_all = stats.join(ospDF) #Totals fall out naturally
cols = ["kill","Deaths2","Suicide","TK","TKd"] + osp_columns[1:]
print(stats_all[cols].fillna("0"))




#Given a team of player names create a matrix of character vs position and figure out prominent chars
#example: players(["+-ab", "+-cd" ) will return +- 
def team_name(players):
    """Return a string element common to all players. Works when clan tags are in front"""
    charsdf = pd.DataFrame(np.arange(start=33, stop = 126+1), columns=["num"])
    charsdf = charsdf.set_index(charsdf["num"].apply(chr))
    charsdf = charsdf.drop(columns=['num'])
        
    for name in players:
        i = 0
        for c in list(name):
            i = i+1
            if c not in charsdf.index.values: continue
            if i in charsdf.columns:
                charsdf.loc[c,i] = charsdf.loc[c,i]+1
            else:
                charsdf[i] = 0
                charsdf.loc[c,i]=1
                
    team_threshold = round(len(players)*.75)
    common_letters = charsdf[charsdf>team_threshold].idxmax()
    common_letters = common_letters[common_letters.notnull()]
    team_name = "".join(common_letters.values)
    return team_name

#Given a team of player names create a list of all sequential strings and find most common one
#example: players(["+-ab", "+-cd" ) will return +- 
#example: players(["+ab", "+cd" ) will return nothing because one char is too risky
def team_name_chars(players):
    """Return a string element common to all players. Works when clan tags are in front"""
    segments = []
    for segment_length in np.arange(5)+1: 
        for player in players:
            for i in np.arange(len(player)-segment_length+1):
                segments.append([segment_length,player[i:i+segment_length]])
                
    segdf = pd.DataFrame(segments, columns = ["segment", "chars"])#, index = range(len(segments)))
    sums = pd.DataFrame(segdf.groupby(["segment","chars"])["chars"].count())
    sums.columns = ["count"]
    sums = sums.reset_index()
    sums = sums[sums["count"]< len(players)+1]
    sums["weight"] = sums["chars"].str.strip().str.len()*sums["count"]
    return sums.sort_values(by="weight",ascending=False).head(1)["chars"].values[0]

def test_clan_tags():
    start_time = time.time()
    print(team_name_chars(["parcher-X-","cky-X-","ra!ser-X-","-a-brian-X-","-a-holliwood-X-","fx-gook-X-","fx-dook-X-"]))
    print(team_name_chars(["parcher","cky","ra!ser","-a-brian","-a-holliwood","fx-gook","fx-dook"]))
    print(team_name_chars(stats.index[0:6]))
    print(team_name_chars(stats.index[7:]))
    print("--- %s seconds ---" % (time.time() - start_time))
    
    start_time = time.time()
    print(team_name(["parcher-X-","cky-X-","ra!ser-X-","-a-brian-X-","-a-holliwood-X-","fx-gook-X-","fx-dook-X-"]))
    print(team_name(["parcher","cky","ra!ser","-a-brian","-a-holliwood","fx-gook","fx-dook"]))
    print(team_name(stats.index[0:6]))
    print(team_name(stats.index[7:]))
    print("--- %s seconds ---" % (time.time() - start_time))
    

pd.set_option("display.max_rows",40)
pd.set_option("display.max_columns",12)
pd.set_option("display.width",160)

#############################
### First in the door award #
#############################
temp = logdf[(logdf.event == "kill")][["round_order","killer", "victim"]].copy()
temp = temp.reset_index()
first_in_the_door = temp[temp["index"].isin(temp.groupby("round_order")["index"].min().values)][["killer", "victim"]]

#############################
### Decypher aliases#########
#############################

name = "n!kon"
valid_names = ["donka","caffeine","nikon","source", "lunatic","reker","corpse"]


def decypher_name(name, valid_names):
    '''Try to guess the original alias of the provided player string'''
    n=2
    name = name.lower()
    name_chain = [name[i:i+n] for i in range(0, len(name)-(n-1), 1)] #break the name into n-char chains
    #print(name_chain)
    for valid_name in valid_names:
        valid_name = valid_name.lower()
        valid_name_chain = [valid_name[i:i+n] for i in range(0, len(valid_name)-(n-1), 1)]  #break the name into n-char chains
        commonalities = set(name_chain).intersection(set(valid_name_chain)) #find common elements between name and valid_name
        #print("Name " + name +  " and template " + valid_name +" produced " + str(len(commonalities))+ " commonalities")
        #print(valid_name_chain)
        #print(commonalities)
        base_length = len(name)-(n-1) if len(name) < len(valid_name) else len(valid_name)-(n-1) #determine which name is longer to judge matching score
        if len(commonalities) >= base_length*.75:
            return valid_name
        
print(decypher_name("/mute donkz", valid_names))
print(decypher_name("donkanator", valid_names))
print(decypher_name("sourcerer", valid_names))    
print(decypher_name("rekenator", valid_names))    
print(decypher_name("caff", valid_names))  
print(decypher_name("<333 caffe1ne", valid_names))  
print(decypher_name("Lunatic ????", valid_names))  
print(decypher_name("----E corpserrr", valid_names))  


debug = True
x = print("kek") if debug else ""




            
