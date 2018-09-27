import pandas as pd
import numpy as np

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
#break all player names into segments of 2,3,4,5 characters
#analyze which segment appears the most and its weight based on its length
def team_name_chars(players):
    """Return a string element common to all players. Works when clan tags are in front"""
    segments = []
    for segment_length in np.arange(2,6): 
        for player in players:
            for i in np.arange(len(player)-segment_length+1):
                segments.append([segment_length,player[i:i+segment_length]])
                
    segdf = pd.DataFrame(segments, columns = ["segment", "chars"])#, index = range(len(segments)))
    sums = pd.DataFrame(segdf.groupby(["segment","chars"])["chars"].count())
    sums.columns = ["count"]
    sums = sums.reset_index()
    team_low_threshold = round(len(players)*.75) # minimum occurenses is 75% players must have this tag
    team_high_threshold = round(len(players)+1) # number of occurences cannot be higher than number of players
    sums = sums[(sums["count"]< team_high_threshold) & (sums["count"] >= team_low_threshold)]
    if (len(sums) == 0): return ""
    sums["weight"] = sums["chars"].str.strip().str.len()*sums["count"]
    return sums.sort_values(by="weight",ascending=False).head(1)["chars"].values[0]
      
def get_team_name(players):
    team_name_default = "No tag"
    temp = team_name_front(players)
    if (len(temp) > 0):
        return temp
    else:
        temp = team_name_chars(players)
        if (len(temp) > 0):
            return temp
    return team_name_default

def get_captain(stats_all, team):
    row = stats_all[stats_all["team"] == team].sort_values(["kill","dmg"]).tail(1)
    return row.index.values[0]

          
def add_team_name(stats_all):
    if(stats_all["team"].dropna().unique().size == 2): #OSP stats were joined
        allies = stats_all[stats_all["team"]=="Allies"].index.values
        axis = stats_all[stats_all["team"]=="Axis"].index.values
        allies_team_name = get_team_name(allies)
        axis_team_name = get_team_name(axis)
        stats_all["player_strip"]=stats_all["player"].str.replace(allies_team_name, "").str.replace(axis_team_name, "").str.strip()
        
        stats_all.loc[stats_all[stats_all["team"]=="Allies"].index, "team_name"] = allies_team_name
        stats_all.loc[stats_all[stats_all["team"]=="Allies"].index, "team_captain"] = get_captain(stats_all, "Allies")
        stats_all.loc[stats_all[stats_all["team"]=="Axis"].index, "team_name"] = axis_team_name
        stats_all.loc[stats_all[stats_all["team"]=="Axis"].index, "team_captain"]  = get_captain(stats_all, "Axis")
    return stats_all

def get_round_guid(stats_all):
        allies_team = stats_all[stats_all["team"] == "Allies"]["team_name"][0]
        axis_team = stats_all[stats_all["team"] == "Axis"]["team_name"][0]
        
        if (allies_team == "No tag"): allies_team = stats_all[stats_all["team"] == "Allies"]["team_captain"][0]
        if (axis_team == "No tag"): axis_team = stats_all[stats_all["team"] == "Axis"]["team_captain"][0]
        teams = [allies_team,axis_team]
        teams.sort() #be consistent about identifying a match guid
        return "-vs-".join(map(str, teams))+ "-" + "-".join(stats_all.sort_values("kill")["kill"].astype(int).astype(str))
    