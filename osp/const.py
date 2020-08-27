'''
This class contains constants- strings, arrays, columns specific to RTCW and this application
Note: map constants are in maps.py
'''


class Const:
    
    EVENT_OSP_STATS_START = "OSP Stats begin"
    EVENT_OSP_STATS_MID = "Skip osp Axis totals"
    EVENT_OSP_STATS_END = "OSP Stats end"
    EVENT_OSP_STATS_ALLIES = "stats_al"
    EVENT_OSP_STATS_AXIS = "stats_ax"
    EVENT_OSP_STATS_ACCURACY = "accuracy_round"
    EVENT_PLAYER_ACC = "OSP Accuracy"
    EVENT_PLAYER_EXTRA = "OSP Extras"
    EVENT_PLAYER_TS  = "OSP File date"
    EVENT_PLAYER_DMG = "OSP_Damage_Given"
    EVENT_PLAYER_DMR = "OSP_Damage_Received"
    EVENT_PLAYER_MAP = "Map"
    EVENT_OSP_STATS_NO_INFO = "OSP Missing player info"
    
    
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
    WEAPON_MG42 = "CrewGun"
    
    bullet_dmg = {
            WEAPON_MP40 : [14,50], 
            WEAPON_THOMPSON : [18,50], 
            WEAPON_LUGER : [18,50], 
            WEAPON_COLT : [18,50], 
            WEAPON_SNIPER : [80,160], 
            WEAPON_STEN : [14,50]
            }
    

    
    WEAPON_SYRINGE = "Syringe"
    
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
    
    STAT_OSPFILE_DATE = "OSP File Date"
    STAT_OSPFILE_PLAYER_DMG = "OSP File DMG"
    STAT_OSPFILE_PU_REVIVE = "OSP File Revive"
    STAT_OSPFILE_DATE = "OSP File date"
    STAT_OSPFILE_PLAYER_DMR = "OSP File DMR"
    STAT_OSPFILE_PU_HEALTHPACK = "OSP File Health"
    STAT_OSPFILE_PU_AMMOPACK = "OSP File Ammo"
    STAT_OSPFILE_MAP = "OSP File Map"
    
    NO_HEADSHOT = [WEAPON_FLAME, WEAPON_VENOM, WEAPON_SYRINGE, WEAPON_ART, WEAPON_AS, WEAPON_DYN, WEAPON_GRENADE, WEAPON_KNIFE, WEAPON_PANZER, WEAPON_MG42]
    YES_HEADSHOT = [WEAPON_MP40, WEAPON_THOMPSON, WEAPON_LUGER, WEAPON_COLT, WEAPON_SNIPER, WEAPON_STEN]
    
    player_stat = {
     'rounds': '1',
     'Sniper_Accuracy': '0',
     'Sniper_Hits': '0',
     'Sniper_Attacks': '0',
     'Sniper_Kills': '0',
     'Sniper_Deaths': '0',
     'Sniper_HeadShots': '0',
     'CrewGun_Accuracy': '0',
     'CrewGun_Hits': '0',
     'CrewGun_Attacks': '0',
     'CrewGun_Kills': '0',
     'CrewGun_Deaths': '0',
     #'CrewGun_HeadShots': '0',
     'Panzerfaust_Accuracy': '0',
     'Panzerfaust_Hits': '0',
     'Panzerfaust_Attacks': '0',
     'Panzerfaust_Kills': '0',
     'Panzerfaust_Deaths': '0',
     #'Panzerfaust_HeadShots': '0',
     'match_date': '1999-12-26 22:44:14',
     'Knife_Accuracy': '0',
     'Knife_Hits': '0',
     'Knife_Attacks': '0',
     'Knife_Kills': '0',
     'Knife_Deaths': '0',
     #'Knife_HeadShots': '0',
     'Luger_Accuracy': '0',
     'Luger_Hits': '0',
     'Luger_Attacks': '0',
     'Luger_Kills': '0',
     'Luger_Deaths': '0',
     'Luger_HeadShots': '0',
     'MP40_Accuracy': '0',
     'MP40_Hits': '0',
     'MP40_Attacks': '0',
     'MP40_Kills': '0',
     'MP40_Deaths': '0',
     'MP40_HeadShots': '0',
     'Grenade_Accuracy': '0',
     'Grenade_Hits': '0',
     'Grenade_Attacks': '0',
     'Grenade_Kills': '0',
     'Grenade_Deaths': '0',
     #'Grenade_HeadShots': '0',
     'Dynamite_Accuracy': '0',
     'Dynamite_Hits': '0',
     'Dynamite_Attacks': '0',
     'Dynamite_Kills': '0',
     'Dynamite_Deaths': '0',
     #'Dynamite_HeadShots': '0',
     'Airstrike_Accuracy': '0',
     'Airstrike_Hits': '0',
     'Airstrike_Attacks': '0',
     'Airstrike_Kills': '0',
     'Airstrike_Deaths': '0',
     #'Airstrike_HeadShots': '0',
     'Artillery_Accuracy': '0',
     'Artillery_Hits': '0',
     'Artillery_Attacks': '0',
     'Artillery_Kills': '0',
     'Artillery_Deaths': '0',
     #'Artillery_HeadShots': '0',
     'AmmoGiven': '0',
     'AmmoDropped': '0',
     'Thompson_Accuracy': '0',
     'Thompson_Hits': '0',
     'Thompson_Attacks': '0',
     'Thompson_Kills': '0',
     'Thompson_Deaths': '0',
     'Thompson_HeadShots': '0',
     'HealthGiven': '0',
     'HealthDropped': '0',
     'Syringe_Accuracy': '0',
     'Syringe_Hits': '0',
     'Syringe_Attacks': '0',
     #'Syringe_Kills': '0',
     #'Syringe_Deaths': '0',
     #'Syringe_HeadShots': '0',
     'Revivals': '0',
     'Venom_Accuracy': '0',
     'Venom_Hits': '0',
     'Venom_Attacks': '0',
     'Venom_Kills': '0',
     'Venom_Deaths': '0',
     #'Venom_HeadShots': '0',
     'Sten_Accuracy': '0',
     'Sten_Hits': '0',
     'Sten_Attacks': '0',
     'Sten_Kills': '0',
     'Sten_Deaths': '0',
     'Sten_HeadShots': '0',
     'Colt_Accuracy': '0',
     'Colt_Hits': '0',
     'Colt_Attacks': '0',
     'Colt_Kills': '0',
     'Colt_Deaths': '0',
     'Colt_HeadShots': '0',
     'Flame_Accuracy': '0',
     'Flame_Hits': '0',
     'Flame_Attacks': '0',
     'Flame_Kills': '0',
     #'Flame_HeadShots': '0',
     'Flame_Deaths': '0'
     }
    
    mod_by_type = { 
                    "Guns" : [WEAPON_MP40,WEAPON_THOMPSON,WEAPON_STEN], 
                    "Pistols": [WEAPON_LUGER,WEAPON_COLT],
                    "Explosives" : [WEAPON_PANZER, WEAPON_GRENADE, WEAPON_AS, WEAPON_ART],
                    "Random" : [WEAPON_SNIPER, WEAPON_VENOM, WEAPON_FLAME, WEAPON_DYN, WEAPON_MG42, WEAPON_KNIFE]
                   }
    
   
    line_types = [
            
            ["map", "^>>> Map: (.*)",EVENT_PLAYER_MAP,STAT_OSPFILE_MAP, True],
            #stat types            
            ["grenade", "^Grenade  : (.*)",EVENT_PLAYER_ACC, WEAPON_GRENADE,True],
            ["Panzerfaust","^Panzer   : (.*)",EVENT_PLAYER_ACC, WEAPON_PANZER, True],
            ["thompson", "^Thompson : (.*)",EVENT_PLAYER_ACC, WEAPON_THOMPSON, True],
            ["mp40", "^MP-40    : (.*)",EVENT_PLAYER_ACC, WEAPON_MP40, True],
            ["sten", "^Sten     : (.*)",EVENT_PLAYER_ACC,WEAPON_STEN, True],
            ["luger", "^Luger    : (.*)",EVENT_PLAYER_ACC,WEAPON_LUGER, True],
            ["colt", "^Colt     : (.*)",EVENT_PLAYER_ACC,WEAPON_COLT, True],
            ["sniper", "^SniperRfl: (.*)",EVENT_PLAYER_ACC,WEAPON_SNIPER, True],
            ["venom", "^Venom    : (.*)",EVENT_PLAYER_ACC,WEAPON_VENOM, True],
            ["flamethrower", "^F.Thrower: (.*)",EVENT_PLAYER_ACC,WEAPON_FLAME, True],
            ["knife", "^Knife    : (.*)",EVENT_PLAYER_ACC,WEAPON_KNIFE, True],
            ["support", "^Airstrike: (.*)",EVENT_PLAYER_ACC,WEAPON_AS, True],
            ["artillery1", "^Artillery: (.*)",EVENT_PLAYER_ACC,WEAPON_ART, True],
            ["artillery2", "^Artillary: (.*)",EVENT_PLAYER_ACC,WEAPON_ART, True],
            ["dynamite", "^Dynamite : (.*)",EVENT_PLAYER_ACC,WEAPON_DYN, True],  
            ["syringe", "Syringe  : (.*)",EVENT_PLAYER_ACC,WEAPON_SYRINGE, True],
            ["mg42", "CrewGun  : (.*)",EVENT_PLAYER_ACC,WEAPON_MG42, True],
            
            #extra lines
            ["ammo1", "^Ammopacks: (.*)",EVENT_PLAYER_EXTRA,STAT_OSPFILE_PU_AMMOPACK, True],
            ["ammo2", "^Ammopacks  : (.*)",EVENT_PLAYER_EXTRA,STAT_OSPFILE_PU_AMMOPACK, True],
            ["hp", "^Healthpacks: (.*)",EVENT_PLAYER_EXTRA,STAT_OSPFILE_PU_HEALTHPACK, True],
            ["rev1", "^Revivals: (.*)",EVENT_PLAYER_EXTRA,STAT_OSPFILE_PU_REVIVE, True],
            ["rev2", "^Revivals   : (.*)",EVENT_PLAYER_EXTRA,STAT_OSPFILE_PU_REVIVE, True],
            ["rev3", "^Revivals : (.*)",EVENT_PLAYER_EXTRA,STAT_OSPFILE_PU_REVIVE, True],
            ["dmr", "^Damage Recvd: (.*)",EVENT_PLAYER_DMR,STAT_OSPFILE_PLAYER_DMR, True],
            ["dmg", "^Damage Given: (.*)",EVENT_PLAYER_DMG,STAT_OSPFILE_PLAYER_DMG, True],
            ["time", "^Stats recorded: (.*)",EVENT_PLAYER_TS,STAT_OSPFILE_DATE, True],

            ["ospbegin", "^TEAM   Player          Kll Dth Sui",EVENT_OSP_STATS_START, "", False],
            
            #these are executed in order, so it's important to keep it this way
            ["ospmid", "^Axis   Totals",EVENT_OSP_STATS_MID, "", False],
            ["ospend", "^Allies Totals",EVENT_OSP_STATS_END, "", False],
            ["ospaxis", "^Axis",EVENT_OSP_STATS_AXIS, "", False],
            ["ospallies", "^Allies",EVENT_OSP_STATS_ALLIES, "", False],
            #endof these
            
            ["roundind", "^Accuracy info for: (.*)", EVENT_OSP_STATS_ACCURACY, "", False], #could use "^Accuracy info for: (.*) \((.*) Round(.*)\):"
            ["separator", "^-------------------------------------", "", "", False],
            ["playerheader", "^Weapon     Acrcy Hits/Atts Kll Dth HS", "", "", False],
            ["noweapon", "^No weapon info available.", EVENT_OSP_STATS_NO_INFO, "", False]
            
            ]

'''
class Logline represents a single line of text processed and prepared for storage in standardized way
'''
class OSPFileLine:
             
    def __init__(self, line_type, regex, event, mod, stats):
         self.line_type = line_type # line ID. Not used for other than debugging
         self.regex = regex         # match on this expression
         self.event = event         # what recognized in a given line
         self.mod = mod             # method of death
         self.stats = stats         # True or False - if the line is recordable or just logical
    
    def LoadOSPLines():
        log_lines = {}  
        for i in Const.line_types:
            log_lines[i[0]] = OSPFileLine(i[0], i[1],i[2], i[3],i[4])
        return log_lines
# -*- coding: utf-8 -*-

import collections

def flatten(d, parent_key='', sep='_'):
    items = []
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def get_player_castings():
    castings = {}
    
    for key in Const.player_stat.keys():
        tokens = key.split("_")
        if len(tokens) == 2:
            if tokens[1] == "Accuracy" in key:
                castings[key] = "float"
            elif tokens[1] in ["HeadShots", "Attacks", "Hits", "Kills", "Deaths"]:
                castings[key] = "int"
            elif tokens[1] == "date":
                castings[key] = "str"
            else:
                print("[!] Unknown key before writing parquet")
        else:
            if key in ["rounds", "AmmoGiven", "AmmoDropped", "HealthGiven", "HealthDropped", "Revivals"]:
                castings[key] = "int"
            else:
                print("[!] Unknown key before writing parquet")
    return castings