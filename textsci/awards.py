from constants.logtext import Const
from collections import Counter

'''
First in the door award
Determine who are the first people getting into fight (killing or dying)
'''
def award_first_in_door(event_lines_dataframe):
    #select only kill events and renumber all rows from 0-n sequentially
    temp = event_lines_dataframe[(event_lines_dataframe.event == "kill")][["round_order","line_order", "killer", "victim"]]
    
    #slice out first(minimum) kill line in each round 
    first_in_the_door_events = temp[temp["line_order"].isin(temp.groupby("round_order")["line_order"].min().values)][["round_order", "killer", "victim"]]
    
    #join together killers and victims as first people in the door
    people = first_in_the_door_events["killer"].append(first_in_the_door_events["victim"])
    
    #return first 3 as list
    result = people.value_counts(ascending=False)[0:3].reset_index().values.tolist()
    return result

'''
Most panzed award
Determine who are the people getting panzed the most
'''
def award_most_panzed(event_lines_dataframe):
    #select only kill events by panzer
    temp = event_lines_dataframe[(event_lines_dataframe["event"] == "kill") & (event_lines_dataframe["mod"] == Const.WEAPON_PANZER)]
    
    #return top 3 most panzed victims
    result = temp["victim"].value_counts(ascending=False)[0:3].reset_index().values.tolist()
    return result

'''
Most blown up award
Determine who are the people getting blown up the most
'''
def award_most_blown_up(event_lines_dataframe):
    #select only kill events by blowy things
    temp = event_lines_dataframe[(event_lines_dataframe["event"] == "kill") & (event_lines_dataframe["mod"].isin([Const.WEAPON_DYN,Const.WEAPON_ART,Const.WEAPON_AS,Const.WEAPON_GRENADE]))]
    
    #return top 3 most panzed victims
    result = temp["victim"].value_counts(ascending=False)[0:3].reset_index().values.tolist()
    return result

'''
(most) Kills in a row award
Determine who had most kills without dying
'''
def award_kill_streak(event_lines_dataframe):
    current_counter = Counter()    
    top_counter = Counter()
    
    #select only kill events
    temp = event_lines_dataframe[event_lines_dataframe["event"] == "kill"]
    
    #for every row    
    for index, row in temp.iterrows():
        #count a kill for a player
        current_counter[row["killer"]] += 1
        
        #if it is their record kill streak, save it
        if(current_counter[row["killer"]] > top_counter[row["killer"]]):
            top_counter[row["killer"]] = current_counter[row["killer"]]
        
        #reset kills for players that died
        current_counter[row["victim"]] = 0
    
    result = top_counter.most_common(3)
    return result

'''
(most) Deaths in a row award (Freefrag Award)
Determine who had most deaths without killing
'''
def award_death_streak(event_lines_dataframe):
    current_counter = Counter()    
    top_counter = Counter()
    
    #select only kill events
    temp = event_lines_dataframe[event_lines_dataframe["event"] == "kill"]
    
    #for every row    
    for index, row in temp.iterrows():
        
        #count a kill for a player
        current_counter[row["victim"]] += 1
        
        #if it is their record kill streak, save it
        if(current_counter[row["victim"]] > top_counter[row["victim"]]):
            top_counter[row["victim"]] = current_counter[row["victim"]]
        
        #reset kills for players that died
        current_counter[row["killer"]] = 0
        
        debug = False
        if debug:
            debug_player = "/mute eternal"
            if row["killer"] ==debug_player or row["victim"] ==debug_player:
                print(row)
                print(current_counter[debug_player])
    
    result = top_counter.most_common(3)
    return result

'''
Pack of 5 award (Brutal Rambo Award from Kris)
Determine how many times a player killed 5 enemies without dying
'''
def award_pack_of_five(event_lines_dataframe):
    current_counter = Counter()    
    pack_counter = Counter()
    
    #select only kill events
    temp = event_lines_dataframe[event_lines_dataframe["event"] == "kill"]
    
    #for every row    
    for index, row in temp.iterrows():
        #count a kill for a player
        current_counter[row["killer"]] += 1
        
        #if it is their record kill streak, save it
        if(current_counter[row["killer"]] == 5):
            pack_counter[row["killer"]] += 1
            current_counter[row["killer"]] = 0
        
        #reset kills for players that died
        current_counter[row["victim"]] = 0
    
    result = pack_counter.most_common(3)
    return result


#TODO: 
#     + needed
#     - not needed
#     ~ maybe
#     v complete
#KrisofWin Awards
# =============================================================================
#       Main Awards
# + Terminator Award: LoopsCat for killing efficiency of 2.85.
# + Slaughterhouse Award: flowerfro with total 94 kills.
# + Slaughterhouse Lama Award: flowerbully for getting slaughtered a total of 103 times.
# - Sly Fox Award: LoopsCat for getting killed only 20 times.
# - Harakiri Award: flowerfro for committing suicide 38 times
# ~ Internal Enemy Award: flowerfro for killing 10 teammates.
# ~ Needless Player Award: flowerCliffd for getting slaughtered a total of 9 times by teamkill.
# - Blabbermouth Award: roz'parcher for 23 lines of messagelog.
# - King Of Votes Award: flowerhomie for calling a total of 2 votes.
# v Rampage Award: LoopsCat for 17 frags without dying.
# v Brutal Rambo Award: flowerjam for 5 series frags (5 frags without dying).
# v Freefrag Award: flowerfaster for 14 deaths without fragging.
# - Desecrator Of Corpses Award: roz'murkey for 120 gibs.
# - Small Dick Award: roz'murkey for can't handling his big toy and blowing himself up a total of 9 times.
# - Careless Sheep Award: flowerfro for getting stabbed a total of 1 times.
#         Weapon Awards
# + The Master Of MP40 Award: flowerbully for 50 frags.
# + The King Of The Thompson Award: flowerCliffd, flowerjam for 37 frags.
# + The Panzer-Lama Award: flowerfro for 62 fuckin' frags.
# + The Sharp-Shooter Award: flowerfro, roz'raw for 7 sniper frags.
# + The Master Of Grenade Award: flowerfro for 16 frags.
# + The Best Indian Smoke-Messenger Award: roz'elsahosk for 11 support-fire frags.
# + The God Of War Award: roz'elsahosk for 3 artillery frags.
# + The Silent Killer Award: roz'raw for 1 knife frags.
# + The "John Wayne Is Lama" Award: flowerjam for 6 pistol frags.
# + Dynamite something award
# =============================================================================

#New awards
# v First in the door 
#   Most damage
# v Blown up  (dead by explosives)
# v Most panzed
#   Steals
#   Holds
#   Points
#   Kills per round
#   Damage per frag (lowest)
#   most kills in a single round


