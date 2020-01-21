from constants.logtext import Const 
from collections import Counter
import pandas as pd
import numpy as np


class Awards:
    
    def __init__(self, result):
        self.event_lines_dataframe = result["logs"]
        self.sum_lines_dataframe   = result["stats"]
        self.matches_dataframe     = result["matches"]
        
        temp = self.event_lines_dataframe[(self.event_lines_dataframe.event == "kill")]
        people = temp["killer"].append(temp["victim"]).unique()
        self.awardsdf = None
        self.all_people = pd.DataFrame(index=people)
    
    def collect_awards(self):
        event_lines_dataframe  = self.event_lines_dataframe
        sum_lines_dataframe    = self.sum_lines_dataframe
        #matches_dataframe     = self.sum_lines_dataframe
        awardsdf               = self.all_people
        columns = []
        
        x = self.award_kills_of_the_night(event_lines_dataframe)
        awardsdf = awardsdf.join(x)
        columns.append(x.columns[0])
        columns.append(x.columns[1])
    
        x = self.award_efficiency_of_the_night(event_lines_dataframe)
        awardsdf = awardsdf.join(x)
        columns.append(x.columns[0])
        columns.append(x.columns[1])
        
        x = self.award_kill_streak(event_lines_dataframe)
        awardsdf = awardsdf.join(x)
        columns.append(x.columns[0])
        columns.append(x.columns[1])
        
# =============================================================================
#         x = self.award_pack_of_five(event_lines_dataframe)
#         awardsdf = awardsdf.join(x)
#         columns.append(x.columns[0])
#         columns.append(x.columns[1])
# =============================================================================
        
        mk = self.award_megakill(event_lines_dataframe) #special for now
        x = mk[0]
        megakilldetail = mk[1]
        awardsdf = awardsdf.join(x)
        columns.append(x.columns[0])
        columns.append(x.columns[1])
        
        x = self.award_panzer(event_lines_dataframe)
        awardsdf = awardsdf.join(x)
        columns.append(x.columns[0])
        columns.append(x.columns[1])
        
        x = self.award_smoker(event_lines_dataframe)
        awardsdf = awardsdf.join(x)
        columns.append(x.columns[0])
        columns.append(x.columns[1])
        
        x = self.award_sniper(event_lines_dataframe)
        awardsdf = awardsdf.join(x)
        columns.append(x.columns[0])
        columns.append(x.columns[1])
        
        x = self.award_death_streak(event_lines_dataframe)
        awardsdf = awardsdf.join(x)
        columns.append(x.columns[0])
        columns.append(x.columns[1])
        
        x = self.award_most_blown_up(event_lines_dataframe)
        awardsdf = awardsdf.join(x)
        columns.append(x.columns[0])
        columns.append(x.columns[1])
        
        x = self.award_most_panzed(event_lines_dataframe)
        awardsdf = awardsdf.join(x)
        columns.append(x.columns[0])
        columns.append(x.columns[1])
        
        x = self.award_first_in_door(event_lines_dataframe)
        awardsdf = awardsdf.join(x)
        columns.append(x.columns[0])
        columns.append(x.columns[1])
        
        x = self.award_most_useful_points(sum_lines_dataframe)
        awardsdf = awardsdf.join(x)
        columns.append(x.columns[0])
        columns.append(x.columns[1])
        
# =============================================================================
#         x = self.award_most_caps(sum_lines_dataframe)
#         awardsdf = awardsdf.join(x)
#         columns.append(x.columns[0])
#         columns.append(x.columns[1])
#         
#         x = self.award_most_holds(sum_lines_dataframe)
#         awardsdf = awardsdf.join(x)
#         columns.append(x.columns[0])
#         columns.append(x.columns[1])
# =============================================================================
        
        x = self.award_most_wins(sum_lines_dataframe)
        awardsdf = awardsdf.join(x)
        columns.append(x.columns[0])
        columns.append(x.columns[1])   
        
        #plug the na wholes with appropriate values
        self.awardsdf = awardsdf
        awardsdf = self.fill_na_values()
        
        #sum all rank points into final RankPts
        ranks = [name for name in awardsdf.columns if "_rank" in name]
        awardsdf["RankPts"] = awardsdf[ranks].sum(axis=1)
        
        #Re-sort by total rank points and rank the ranks yo dawg
        awardsdf = awardsdf.sort_values("RankPts")
        awardsdf["RankPts_rank"] = awardsdf["RankPts"].rank(method="min", ascending=True, na_option='bottom')
        columns.append("RankPts")
        columns.append("RankPts_rank")
               
        self.awardsdf = awardsdf
        return [awardsdf,columns, megakilldetail]
       
    def fill_na_values(self):
        awardsdf = self.awardsdf
        
        rank_cols, ranked_cols, unranked_cols, inverse_ranked_cols = self.ranked_column_types()
        
        #plug rank wholes
        awardsdf[ranked_cols] = awardsdf[ranked_cols].fillna(Const.RANK_MAX).astype(int)
        awardsdf[unranked_cols] = awardsdf[unranked_cols].fillna(0).astype(int)
        awardsdf[inverse_ranked_cols] = awardsdf[inverse_ranked_cols].fillna(0).astype(int)
                
        #awardsdf['Pack5'] = awardsdf['Pack5'].fillna(0).astype(int)
        awardsdf['Blownup'] = awardsdf['Blownup'].fillna(0).astype(int)
        awardsdf['FirstInDoor'] = awardsdf['FirstInDoor'].fillna(0).astype(int)
        awardsdf['Deathroll'] = awardsdf['Deathroll'].fillna(0).astype(int)
        #awardsdf['Holds'] = awardsdf['Holds'].fillna(0).astype(int)
        #awardsdf['Caps'] = awardsdf['Caps'].fillna(0).astype(int)
        awardsdf['Wins'] = awardsdf['Wins'].fillna(0).astype(int)
        awardsdf['MegaKill'] = awardsdf['MegaKill'].fillna(0).astype(int)
        awardsdf['Panzer'] = awardsdf['Panzer'].fillna(0).astype(int)
        awardsdf['Panzed'] = awardsdf['Panzed'].fillna(0).astype(int)
        awardsdf['Smoker'] = awardsdf['Smoker'].fillna(0).astype(int)
        awardsdf['Sniper'] = awardsdf['Sniper'].fillna(0).astype(int)

        return awardsdf
    
    #TODO: re-write this statically maybe for easier understanding
    def ranked_column_types(self):
        rank_cols = [c for c in self.awardsdf.columns if c.endswith('_rank')]
        #ranked_cols = [c for c in self.awardsdf.columns[self.awardsdf.max() >0] if c.endswith('_rank')]
        ranked_cols = ['Kills_rank', 'KDR_rank', 'KillStreak_rank', 'MegaKill_rank', 'Panzer_rank', 'Smoker_rank', 'FirstInDoor_rank', 'AdjScore_rank', 'Wins_rank']
        #unranked_cols = [c for c in self.awardsdf.columns[self.awardsdf.max() == 0] if c.endswith('_rank')]
        unranked_cols = ['Deathroll_rank', 'Blownup_rank', 'Panzed_rank']
        inverse_ranked_cols = ['Panzer_rank', 'Smoker_rank', 'Sniper_rank']
        return rank_cols, ranked_cols, unranked_cols, inverse_ranked_cols
        
    '''
    First in the door award
    Determine who are the first people getting into fight (killing or dying)
    '''
    def award_first_in_door(self,event_lines_dataframe):
        #select only kill events and renumber all rows from 0-n sequentially
        temp = event_lines_dataframe[(event_lines_dataframe.event == "kill")][["round_order","line_order", "killer", "victim"]]
        
        #slice out first(minimum) kill line in each round 
        first_in_the_door_events = temp[temp["line_order"].isin(temp.groupby("round_order")["line_order"].min().values)][["round_order", "killer", "victim"]]
        
        #join together killers and victims as first people in the door
        people = first_in_the_door_events["killer"].append(first_in_the_door_events["victim"])
        
        #Count values
        result = people.value_counts().to_frame()
        result.columns = ["FirstInDoor"]
        result["FirstInDoor_rank"] = result["FirstInDoor"].rank(method="min", ascending=False, na_option='bottom') 
        result.loc[result[result["FirstInDoor_rank"] > 4].index, "FirstInDoor_rank"] = 5
        return result
    
    '''
    Most panzed award
    Determine who are the people getting panzed the most
    '''
    def award_most_panzed(self,event_lines_dataframe):
        #select only kill events by panzer
        temp = event_lines_dataframe[(event_lines_dataframe["event"] == "kill") & (event_lines_dataframe["mod"] == Const.WEAPON_PANZER)]
        
        result = temp["victim"].value_counts().to_frame()
        result.columns = ["Panzed"]
        result["Panzed_rank"] = 0  
        return result
    
    '''
    Panzer award (penalty)
    Determine who are the people that got most panz kills
    '''
    def award_panzer(self,event_lines_dataframe):
        #debug: event_lines_dataframe = results[0]["logs"].copy()
        
        #get all people
        temp = event_lines_dataframe[(event_lines_dataframe.event == "kill")]
        people = temp["killer"].append(temp["victim"]).unique()
        result_all = pd.DataFrame(index=people) #, columns=["Panzer","Panzer_rank"]).fillna(0)
        
        #select only kill events by panzer
        temp2 = event_lines_dataframe[(event_lines_dataframe["event"] == "kill") & (event_lines_dataframe["mod"] == Const.WEAPON_PANZER)]
        result = temp2["killer"].value_counts().to_frame()
        result.columns = ["Panzer"]
        result["Panzer_rank"] = result["Panzer"].rank(method="dense", ascending=True, na_option='bottom')
        scale_down_factor = 5 - result["Panzer_rank"].max()
        result["Panzer_rank"] = result["Panzer_rank"] + scale_down_factor 
        result.loc[result[result["Panzer_rank"] < 0].index, "Panzer_rank"] = 0
        result = result_all.join(result).fillna(0)
        return result
    
    '''
    Leautenant award (penalty)
    Determine who are the people that got most artllery and airstrike kills
    '''
    def award_smoker(self,event_lines_dataframe):
        #debug: event_lines_dataframe = results[0]["logs"].copy()
        
        #get all people
        temp = event_lines_dataframe[(event_lines_dataframe.event == "kill")]
        people = temp["killer"].append(temp["victim"]).unique()
        result_all = pd.DataFrame(index=people) 
        
        #select only kill events by LT
        temp2 = event_lines_dataframe[(event_lines_dataframe["event"] == "kill") & ((event_lines_dataframe["mod"] == Const.WEAPON_AS) | (event_lines_dataframe["mod"] == Const.WEAPON_ART))]
        result = temp2["killer"].value_counts().to_frame()
        result.columns = ["Smoker"]
        result["Smoker_rank"] = result["Smoker"].rank(method="dense", ascending=True, na_option='bottom')
        scale_down_factor = 3 - result["Smoker_rank"].max()
        result["Smoker_rank"] = result["Smoker_rank"] + scale_down_factor 
        result.loc[result[result["Smoker_rank"] < 0].index, "Smoker_rank"] = 0
        result = result_all.join(result).fillna(0)
        return result
    
    '''
    Sniper award (penalty)
    Determine who are the people that got most sniper kills
    '''
    def award_sniper(self,event_lines_dataframe):
        #debug: event_lines_dataframe = results[0]["logs"].copy()
        
        #get all people
        temp = event_lines_dataframe[(event_lines_dataframe.event == "kill")]
        people = temp["killer"].append(temp["victim"]).unique()
        result_all = pd.DataFrame(index=people) 
        
        #select only kill events by LT
        temp2 = event_lines_dataframe[(event_lines_dataframe["event"] == "kill") & ((event_lines_dataframe["mod"] == Const.WEAPON_SNIPER) | (event_lines_dataframe["mod"] == Const.WEAPON_MAUSER))]
        result = temp2["killer"].value_counts().to_frame()
        result.columns = ["Sniper"]
        result["Sniper_rank"] = result["Sniper"].rank(method="dense", ascending=True, na_option='bottom')
        scale_down_factor = 2 - result["Sniper_rank"].max()
        result["Sniper_rank"] = result["Sniper_rank"] + scale_down_factor 
        result.loc[result[result["Sniper_rank"] < 0].index, "Sniper_rank"] = 0
        result = result_all.join(result).fillna(0)
        return result
    
    
    
    '''
    Most blown up award
    Determine who are the people getting blown up the most
    '''
    def award_most_blown_up(self,event_lines_dataframe):
        #select only kill events by blowy things
        temp = event_lines_dataframe[(event_lines_dataframe["event"] == "kill") & (event_lines_dataframe["mod"].isin([Const.WEAPON_DYN,Const.WEAPON_ART,Const.WEAPON_AS,Const.WEAPON_GRENADE]))]
        
        result = temp["victim"].value_counts().to_frame()
        result.columns = ["Blownup"]
        result["Blownup_rank"] = 0  
        return result
    
    '''
    Megakill award
    Determine the killing spree that happened in an instance
    '''
    def award_megakill(self,event_lines_dataframe):
        #debug: event_lines_dataframe = results[0]["logs"].copy()
        #count killers repeating in succession
        
        #this almost worked....as a one liner
        #event_lines_dataframe["count"] = event_lines_dataframe.groupby((event_lines_dataframe['killer'] != event_lines_dataframe['killer'].shift(1)).cumsum()).cumcount()+1
        
        event_lines_dataframe = event_lines_dataframe.reset_index()
        del event_lines_dataframe["index"]
        event_lines_dataframe["count"] = 0
        for index in event_lines_dataframe.index[0:len(event_lines_dataframe)-1]:
            #if current event is a kill and next event is a kill and killer is the same, set next count to +1
            if event_lines_dataframe.loc[index, "event"] == "kill" and event_lines_dataframe.loc[index+1, "event"] == "kill" and event_lines_dataframe.loc[index, "killer"] == event_lines_dataframe.loc[index+1, "killer"]:
                event_lines_dataframe.loc[index + 1, "count"] = event_lines_dataframe.loc[index, "count"] + 1
            else:
                event_lines_dataframe.loc[index + 1, "count"] = 1
            
        #select max kills for each player
        result = event_lines_dataframe[event_lines_dataframe["event"] == "kill"].groupby("killer")["count"].max().to_frame()
        result.columns = ["MegaKill"]
        result["MegaKill_rank"] = result["MegaKill"].rank(method="min", ascending=False, na_option='bottom')
        result.loc[result[result["MegaKill_rank"] > 4].index, "MegaKill_rank"] = 5
        
        #extract actual megakills (3 or more)
        tmp_result = result[result["MegaKill"] > 2]
        megakills = pd.DataFrame()
        for player, row in tmp_result.iterrows():
            idx = event_lines_dataframe[(event_lines_dataframe["killer"] == player) & (event_lines_dataframe["count"] == row["MegaKill"])].index.values
            for i in range(len(idx)):
                df = event_lines_dataframe.iloc[idx[i]+1-int(row["MegaKill"]) : idx[i]+1]
                megakills = megakills.append(df)
        
        megakills["count"] = megakills["count"].astype(int)
        return [result, megakills[["round_order", "killer", "mod", "victim","count"]]]
    
    '''
    (most) Kills in a row award
    Determine who had most kills without dying
    '''
    def award_kill_streak(self,event_lines_dataframe):
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
                if row["killer"] == "KrAzYkAzEX":
                   print(str(current_counter[row["killer"]]) + " killstreak  in round: " + str(row["round_order"])) 
            
            #reset kills for players that died
            current_counter[row["victim"]] = 0
            
            if row["killer"] == "KrAzYkAzEX" or row["victim"] == "KrAzYkAzEX":
                print(row.values[2:])
                print(" Current counter is " + str(current_counter["KrAzYkAzE"]))
                #print(" Top counter is " + str(top_counter["KrAzYkAzE"]))
        
        resultdict = {}
        for key, value in top_counter.most_common():
            resultdict[key]=value
        resultdf = pd.DataFrame.from_dict(resultdict,orient='index')
        resultdf.columns=['KillStreak']
        resultdf["KillStreak_rank"] = resultdf["KillStreak"].rank(method="min", ascending=False, na_option='bottom')
        resultdf.loc[resultdf[resultdf["KillStreak_rank"] > 4].index, "KillStreak_rank"] = 5
        return resultdf
    
    '''
    (most) Deaths in a row award (Freefrag Award)
    Determine who had most deaths without killing
    ranked in reverse order
    '''
    def award_death_streak(self,event_lines_dataframe):
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
        
        resultdict = {}
        for key, value in top_counter.most_common():
            resultdict[key]=value
        resultdf = pd.DataFrame.from_dict(resultdict,orient='index')
        resultdf.columns=['Deathroll']
        resultdf["Deathroll_rank"] = 0
        return resultdf

    
    '''
    Pack of 5 award (Brutal Rambo Award from Kris)
    Determine how many times a player killed 5 enemies without dying
    '''
    def award_pack_of_five(self, event_lines_dataframe):
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
        
        resultdict = {}
        for key, value in pack_counter.most_common():
            resultdict[key]=value
        resultdf = pd.DataFrame.from_dict(resultdict,orient='index')
        resultdf.columns=['Pack5']
        resultdf["Pack5_rank"] = resultdf["Pack5"].rank(method="min", ascending=False, na_option='bottom')
        resultdf.loc[resultdf[resultdf["Pack5_rank"] > 4].index, "Pack5_rank"] = 5
        return resultdf
    
    '''
    Most kills of the night (Slaughterhouse Award from Kris)
    '''
    def award_kills_of_the_night(self,event_lines_dataframe):
        temp = event_lines_dataframe[(event_lines_dataframe.event == "kill")]
        result = temp["killer"].value_counts().to_frame().rename(columns={"killer" : "Kills"})
        result["Kills_rank"] = result["Kills"].rank(method="min", ascending=False, na_option='bottom')  
        result.loc[result[result["Kills_rank"] > 4].index, "Kills_rank"] = 5
        return result
    
    '''
    Best efficiency of the night (Terminator Award from Kris)
    '''
    def award_efficiency_of_the_night(self,event_lines_dataframe):
        #pd.options.display.float_format = '{:,.2f}'.format
        temp = event_lines_dataframe[(event_lines_dataframe.event == "kill")]
        resultk = temp["killer"].value_counts()
        resultd = temp["victim"].value_counts()
        
        result = pd.DataFrame({"KDR" : resultk/resultd}).round(2)
        result["KDR_rank"] = result["KDR"].rank(method="min", ascending=False, na_option='bottom')   
        
        #since there are 2 teams , split rankings on 2
        result["KDR_rank"] = result["KDR_rank"]/2
        result["KDR_rank"] = result["KDR_rank"].apply(np.ceil).astype(int)
        #result.loc[result[result["KDR_rank"] > 4].index, "KDR_rank"] = 5
        return result

    '''
    Most times objective reached before timelimit (winning a round on offence)
    '''
    def award_most_caps(self,sum_lines_dataframe):
        temp = sum_lines_dataframe[(sum_lines_dataframe.side == "Offense") & (sum_lines_dataframe.round_win == 1)]
        result = temp.groupby(Const.STAT_BASE_KILLER)[["round_win"]].sum().rename(columns={"round_win" : "Caps"})
        result["Caps_rank"] = result["Caps"].rank(method="dense", ascending=False, na_option='bottom')  
        result.loc[result[result["Caps_rank"] > 4].index, "Caps_rank"] = 5
        return result
    
    '''
    Most times defense held to timelimit (winning a round on defense)
    '''
    def award_most_holds(self,sum_lines_dataframe):
        temp = sum_lines_dataframe[(sum_lines_dataframe.side == "Defense") & (sum_lines_dataframe.round_win == 1)]
        result = temp.groupby(Const.STAT_BASE_KILLER)[["round_win"]].sum().rename(columns={"round_win" : "Holds"})
        result["Holds_rank"] = result["Holds"].rank(method="dense", ascending=False, na_option='bottom') 
        result.loc[result[result["Holds_rank"] > 4].index, "Holds_rank"] = 5
        return result
    
    '''
    Most wins
    '''
    def award_most_wins(self,sum_lines_dataframe):
        temp = sum_lines_dataframe[sum_lines_dataframe.game_result == "WON"]
        result = temp.groupby(Const.STAT_BASE_KILLER)[["game_result"]].count().rename(columns={"game_result" : "Wins"})
        result["Wins_rank"] = result["Wins"].rank(method="dense", ascending=False, na_option='bottom') 
        #result["Wins_rank"][result["Wins_rank"] > 4] = 5
        result.loc[result[result["Wins_rank"] > 4].index, "Wins_rank"] = 5
        return result
    
    '''
    Most useful points
    '''
    def award_most_useful_points(self,sum_lines_dataframe):
        result = sum_lines_dataframe.groupby([Const.STAT_BASE_KILLER])[[Const.STAT_POST_ADJSCORE]].sum()
        result[Const.STAT_POST_ADJSCORE + "_rank"] = result[Const.STAT_POST_ADJSCORE].rank(method="min", ascending=False, na_option='bottom')
        result.loc[result[result[Const.STAT_POST_ADJSCORE + "_rank"] > 4].index, Const.STAT_POST_ADJSCORE + "_rank"] = 5
        return result

 
# =============================================================================
# a = pd.DataFrame(index = statsdf["player"].unique())    
# b = temp.sort_values("AdjScore",ascending=False)
# c = a.join(b)
# =============================================================================

#TODO: 
#     + needed
#     - not needed
#     ~ maybe
#     v complete
#base = requires only console log events
#osp  = requires osp stats
#KrisofWin Awards
# =============================================================================
#       Main Awards
# v base - Terminator Award: LoopsCat for killing efficiency of 2.85.
# v base - Slaughterhouse Award: flowerfro with total 94 kills.
# ~ base - Slaughterhouse Lama Award: flowerbully for getting slaughtered a total of 103 times.
# - Sly Fox Award: LoopsCat for getting killed only 20 times.
# - Harakiri Award: flowerfro for committing suicide 38 times
# ~ base - Internal Enemy Award: flowerfro for killing 10 teammates.
# ~ Needless Player Award: flowerCliffd for getting slaughtered a total of 9 times by teamkill.
# - Blabbermouth Award: roz'parcher for 23 lines of messagelog.
# - King Of Votes Award: flowerhomie for calling a total of 2 votes.
# v base - Rampage Award: LoopsCat for 17 frags without dying.
# v base - Brutal Rambo Award: flowerjam for 5 series frags (5 frags without dying).
# v base - Freefrag Award: flowerfaster for 14 deaths without fragging.
# - Desecrator Of Corpses Award: roz'murkey for 120 gibs.
# - Small Dick Award: roz'murkey for can't handling his big toy and blowing himself up a total of 9 times.
# - Careless Sheep Award: flowerfro for getting stabbed a total of 1 times.
#         Weapon Awards
# + base - The Master Of MP40 Award: flowerbully for 50 frags.
# + base - The King Of The Thompson Award: flowerCliffd, flowerjam for 37 frags.
# + base - The Panzer-Lama Award: flowerfro for 62 fuckin' frags.
# + base - The Sharp-Shooter Award: flowerfro, roz'raw for 7 sniper frags.
# + base - The Master Of Grenade Award: flowerfro for 16 frags.
# + base - The Best Indian Smoke-Messenger Award: roz'elsahosk for 11 support-fire frags.
# + base - The God Of War Award: roz'elsahosk for 3 artillery frags.
# + base - The Silent Killer Award: roz'raw for 1 knife frags.
# + base - The "John Wayne Is Lama" Award: flowerjam for 6 pistol frags.
# + base - Dynamite something award
# =============================================================================

#New awards
# v base - First in the door 
# v base - Blown up  (dead by explosives)
# v base - Most panzed
# v base - Caps (if won on offence)
# v base - Holds
#   base - Kills per round
#   base - most kills in a single round
#   osp  - Damage per frag (lowest)
#   osp  - Most damage
# v osp  - most points 


