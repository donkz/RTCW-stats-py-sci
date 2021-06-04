import pandas as pd
import numpy as np
import hashlib
import re
import time as _time

from rtcwlog.constants.logtext import Const

#Hash a string
#Example get_hash(round2_stats_string)
def get_hash(string):
    return hashlib.md5(string.encode()).hexdigest()

#Given a team of player names create a matrix of character vs position and figure out prominent chars
#example: players(["+-ab", "+-cd" ) will return +- 
#build a matrix of all characters vs positions
#figure out which letters in which positions repeat the most
#stich them together into a clan tag
def team_name_front(players):
    """Return a string element common to all players. Works when clan tags are in front"""
    charsdf = pd.DataFrame(np.arange(start=33, stop = 126+1), columns=["num"])
    charsdf = charsdf.set_index(charsdf["num"].apply(chr))
    charsdf = charsdf.drop(columns=['num'])
        
    for name in players:
        i = 0
        for c in list(name.lower()):
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
#break all player names into segments of 3,4,5 characters
#analyze which segment appears the most and its weight based on its length
def team_name_chars(players):
    """Return a string element common to all players. Works when clan tags are in front"""
    segments = []
    for segment_length in np.arange(3,6): 
        for player in players:
            player_segments = []
            for i in np.arange(len(player)-segment_length+1):
                segment = player.lower()[i:i+segment_length]
                if segment not in player_segments:
                    segments.append([segment_length,segment])
                    player_segments.append(segment)                
                
    segdf = pd.DataFrame(segments, columns = ["segment", "chars"])#, index = range(len(segments)))
    sums = pd.DataFrame(segdf.groupby(["segment","chars"])["chars"].count())
    sums.columns = ["count"]
    sums = sums.reset_index()
    team_low_threshold = round(len(players)*.75) # minimum occurenses is 75% players must have this tag
    team_high_threshold = round(len(players)) # number of occurences cannot be higher than number of players
    sums = sums[(sums["count"]< team_high_threshold) & (sums["count"] >= team_low_threshold)]
    if (len(sums) == 0): return ""
    sums["weight"] = sums["chars"].str.strip().str.len()*sums["count"]
    return sums.sort_values(by="weight",ascending=False).head(1)["chars"].values[0]
      
def get_team_name(players):
    team_name_default = "No tag"
    temp = team_name_front(players)
    if (len(temp) > 0):
        #print("Found tag " + temp + " using team_name_front function for:")
        #print(players)
        return temp
    else:
        temp = team_name_chars(players)
        if (len(temp) > 0):
            #print("Found tag " + temp + " using team_name_chars function for:")
            #print(players)
            return temp
    return team_name_default

def get_captain(stats_all, team):
    row = stats_all[stats_all[Const.STAT_OSP_SUM_TEAM] == team].sort_values([Const.STAT_BASE_KILL,Const.STAT_OSP_SUM_DMG]).tail(1)
    return row.index.values[0]

          
def add_team_name(stats_all):
    if(stats_all[Const.STAT_OSP_SUM_TEAM].dropna().unique().size == 2): #OSP stats were joined
        allies = stats_all[stats_all[Const.STAT_OSP_SUM_TEAM]=="Allies"].index.values
        axis = stats_all[stats_all[Const.STAT_OSP_SUM_TEAM]=="Axis"].index.values
        allies_team_name = get_team_name(allies)
        axis_team_name = get_team_name(axis)
        #print(stats_all[Const.STAT_OSP_SUM_PLAYER])
        #print("---------Team name " + allies_team_name)
        #print(stats_all[Const.STAT_OSP_SUM_PLAYER].str.replace(allies_team_name, ""))
        #print("try")
        stats_all["player_strip"]=stats_all[Const.STAT_OSP_SUM_PLAYER].str.replace(re.escape(allies_team_name),"").str.replace(re.escape(axis_team_name), "").str.strip()   
        #print("passed")
        #stats_all["player_strip"]=""
        stats_all.loc[stats_all[stats_all[Const.STAT_OSP_SUM_TEAM]=="Allies"].index, "team_name"] = allies_team_name
        stats_all.loc[stats_all[stats_all[Const.STAT_OSP_SUM_TEAM]=="Axis"].index, "team_name"] = axis_team_name
    return stats_all
    
def get_player_list(stats_all):
        #debug stats_all = statsdf[statsdf["round_order"]==1]
        #print("got here")
        #print(stats_all[["side",Const.STAT_BASE_KILLER,Const.STAT_OSP_SUM_TEAM]])
        
        playerlisto = stats_all[stats_all["side"] == "Offense"].sort_values(Const.STAT_BASE_KILLER)[[Const.STAT_BASE_KILLER,Const.STAT_OSP_SUM_TEAM]]
        playerlisto_str = [Const.TEXT_PLAYER_SEPARATOR.join(playerlisto[Const.STAT_BASE_KILLER]), playerlisto.iloc[0,1], "Offense"]
        playerlistd = stats_all[stats_all["side"] == "Defense"].sort_values(Const.STAT_BASE_KILLER)[[Const.STAT_BASE_KILLER,Const.STAT_OSP_SUM_TEAM]]
        playerlistd_str = [Const.TEXT_PLAYER_SEPARATOR.join(playerlistd[Const.STAT_BASE_KILLER]), playerlistd.iloc[0,1], "Defense"]
#        print(playerlisto)
#        print(playerlistd)
#        print(playerlisto_str)
#        print(playerlistd_str)
        players = sorted([playerlisto_str , playerlistd_str], key=lambda x: x[0])
        return players 
    
def get_round_guid_client_log(stats_all):
        stats_all[Const.STAT_BASE_KILLER] = stats_all.index #could just reset_index
        match_id_table = stats_all.sort_values([Const.STAT_BASE_KILLER, Const.STAT_BASE_KILL,Const.STAT_BASE_DEATHS])[[Const.STAT_BASE_KILLER, Const.STAT_BASE_KILL,Const.STAT_BASE_DEATHS]]
        match_id_string = ''.join(match_id_table.to_string(index=False, header=False))
        #print(match_id_table.to_string(index=False, header=False))
        client_log_guid = get_hash(match_id_string)
        return client_log_guid
    
def get_round_desc_client_log(stats_all):
        allies_team = stats_all[stats_all[Const.STAT_OSP_SUM_TEAM] == "Allies"]["team_name"][0]
        axis_team = stats_all[stats_all[Const.STAT_OSP_SUM_TEAM] == "Axis"]["team_name"][0]
        
        if (allies_team == "No tag"): allies_team = stats_all[stats_all[Const.STAT_OSP_SUM_TEAM] == "Allies"]["team_captain"][0]
        if (axis_team == "No tag"): axis_team = stats_all[stats_all[Const.STAT_OSP_SUM_TEAM] == "Axis"]["team_captain"][0]
        teams = [allies_team,axis_team]
        teams.sort() #be consistent about identifying a match guid
        return "-vs-".join(map(str, teams))+ "-" + "-".join(stats_all.sort_values("kill")["kill"].astype(int).astype(str))


def guess_team(logdf, passes=4, side=False, debug_time=False):
    """Guess which team players belong to based on their kills and teamkills."""
    # test
    # logdf = result["logs"]  # for end-game team determination
    # logdf = logdf[logdf["round_order"]==35] # for imputing team determination
    # test

    t1 = _time.time()

    kills = logdf[logdf["event"].isin(["kill", "Team kill"])][['event', 'killer', 'mod', 'victim']]
    kills["count"] = 1
    kills["WeaponSide"] = kills["mod"].replace("MP40", "-1").replace("Luger", "-100").replace("Thompson", "4").replace("Colt", "100")
    kills["WeaponSide"] = pd.to_numeric(kills["WeaponSide"], errors='coerce').fillna(0).astype(int)
    kills.drop(["mod"], axis=1, inplace=True)
    kills = kills.groupby(['event', 'killer', 'victim']).sum().reset_index().sort_values("count", ascending=False)

    player0 = kills[["killer", "count"]].groupby("killer").sum().sort_values("count", ascending=False).index.values[0]

    kills.loc[kills[(kills["killer"] == player0) & (kills["event"] == "kill")].index, "VicTeam"] = "B"
    kills.loc[kills[(kills["killer"] == player0) & (kills["event"] == "Team kill")].index, "VicTeam"] = "A"
    kills.loc[kills[(kills["killer"] == player0) & (kills["event"] == "kill")].index, "KilTeam"] = "A"
    kills.loc[kills[(kills["killer"] == player0) & (kills["event"] == "Team kill")].index, "KilTeam"] = "B"

    for x in range(passes):  # 2 works. 4 is safer
        teamB = kills[kills["VicTeam"] == "B"]["victim"].unique()
        for p in teamB:
            kills.loc[kills[(kills["killer"] == p) & (kills["event"] == "kill")].index, "VicTeam"] = "A"
            kills.loc[kills[(kills["killer"] == p) & (kills["event"] == "kill")].index, "KilTeam"] = "B"

            kills.loc[kills[(kills["killer"] == p) & (kills["event"] == "Team kill")].index, "KilTeam"] = "B"
            kills.loc[kills[(kills["killer"] == p) & (kills["event"] == "Team kill")].index, "VicTeam"] = "B"

            kills.loc[kills[(kills["victim"] == p) & (kills["event"] == "kill")].index, "KilTeam"] = "A"
            kills.loc[kills[(kills["victim"] == p) & (kills["event"] == "kill")].index, "VicTeam"] = "B"

        teamA = kills[kills["KilTeam"] == "A"]["killer"].unique()
        for p in teamA:
            kills.loc[kills[(kills["killer"] == p) & (kills["event"] == "kill")].index, "VicTeam"] = "B"
            kills.loc[kills[(kills["killer"] == p) & (kills["event"] == "kill")].index, "KilTeam"] = "A"

            kills.loc[kills[(kills["killer"] == p) & (kills["event"] == "Team kill")].index, "KilTeam"] = "A"
            kills.loc[kills[(kills["killer"] == p) & (kills["event"] == "Team kill")].index, "VicTeam"] = "A"

            kills.loc[kills[(kills["victim"] == p) & (kills["event"] == "kill")].index, "KilTeam"] = "B"
            kills.loc[kills[(kills["victim"] == p) & (kills["event"] == "kill")].index, "VicTeam"] = "A"

    # plug holes
    kills.loc[kills[(kills["KilTeam"] == "A") & (kills["event"] == "kill")].index, "VicTeam"] = "B"
    kills.loc[kills[(kills["KilTeam"] == "A") & (kills["event"] == "Team kill")].index, "VicTeam"] = "A"
    kills.loc[kills[(kills["KilTeam"] == "B") & (kills["event"] == "kill")].index, "VicTeam"] = "A"
    kills.loc[kills[(kills["KilTeam"] == "B") & (kills["event"] == "Team kill")].index, "VicTeam"] = "B"

    playersraw = kills[["killer", "KilTeam"]].rename(columns={"killer": "player", "KilTeam": "Team"}).append(kills[["victim", "VicTeam"]].rename(columns={"victim": "player", "VicTeam": "Team"}))
    players = playersraw.groupby(["player", "Team"]).size().reset_index()
    players.drop(players.columns[-1], axis=1, inplace=True)
    players.index = players["Team"]
    teams = kills[['WeaponSide', 'KilTeam']].groupby("KilTeam").sum()
    res = players.join(teams)
    res.loc[res[res["WeaponSide"] == res["WeaponSide"].min()].index, "TeamName"] = "Axis"
    res.loc[res[res["WeaponSide"] == res["WeaponSide"].max()].index, "TeamName"] = "Allies"
    res.index = res["player"]
    # print(res)

    if res["TeamName"].nunique() < 2:
        print("[!] Could not guess teams while imputing variables. Skipping this round")
        return None

    t2 = _time.time()
    if debug_time:
        print("[t] Time to guess team while imputing " + str(round((t2 - t1), 3)) + " s")

    if side:
        return res["TeamName"].to_dict()
    else:
        return res["Team"].to_dict()
