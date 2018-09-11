import pandas as pd
import numpy as np

#Given a team of player names create a matrix of character vs position and figure out prominent chars
#example: players(["+-ab", "+-cd" ) will return +- 
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
      
def get_team_name(players):
    team_name_default = "Unknown"
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
    if(bool(row["team_name"][0])):
        return row["team_name"].values
    else:
        return row.index.values[0]
          
def add_team_name(stats_all):
    if(stats_all["team"].unique().size == 2): #OSP stats were joined
        allies = stats_all[stats_all["team"]=="Allies"].index.values
        axis = stats_all[stats_all["team"]=="Axis"].index.values
        allies_team_name = get_team_name(allies)
        axis_team_name = get_team_name(axis)
        stats_all["player_strip"]=stats_all["player"].str.replace(allies_team_name, "").str.replace(axis_team_name, "").str.strip()
        if(allies_team_name != "Unknown"):
            stats_all.loc[stats_all[stats_all["team"]=="Allies"].index, "team_name"] = allies_team_name
        else:
            stats_all.loc[stats_all[stats_all["team"]=="Allies"].index, "team_name"] = get_captain(stats_all, "Allies")
        if(axis_team_name != "Unknown"):
            stats_all.loc[stats_all[stats_all["team"]=="Axis"].index, "team_name"] = axis_team_name
        else:
            stats_all.loc[stats_all[stats_all["team"]=="Axis"].index, "team_name"]  = get_captain(stats_all, "Axis")
    return stats_all
