from constants.logtext import Const # need to actually copy paste cont class to console until i figure out how to cross call the folders
from collections import Counter
import pandas as pd


class Awards:
    
    def collect_awards(self, data):
        event_lines_dataframe = data["logdf"]
        sum_lines_dataframe   = data["stats"]
        #matches_dataframe     = data["matchesdf"]
        
        temp = event_lines_dataframe[(event_lines_dataframe.event == "kill")]
        people = temp["killer"].append(temp["victim"]).unique()
        awardsdf = pd.DataFrame(index=people)
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
        
        x = self.award_pack_of_five(event_lines_dataframe)
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
        
        x = self.award_most_caps(sum_lines_dataframe)
        awardsdf = awardsdf.join(x)
        columns.append(x.columns[0])
        columns.append(x.columns[1])
        
        x = self.award_most_holds(sum_lines_dataframe)
        awardsdf = awardsdf.join(x)
        columns.append(x.columns[0])
        columns.append(x.columns[1])
        
        x = self.award_most_wins(sum_lines_dataframe)
        awardsdf = awardsdf.join(x)
        columns.append(x.columns[0])
        columns.append(x.columns[1])
        
        
        
        awardsdf['Pack5'] = awardsdf['Pack5'].fillna(0).astype(int)
        awardsdf['Blownup'] = awardsdf['Blownup'].fillna(0).astype(int)
        awardsdf['FirstInDoor'] = awardsdf['FirstInDoor'].fillna(0).astype(int)
        awardsdf['Holds'] = awardsdf['Holds'].fillna(0).astype(int)
        awardsdf['Caps'] = awardsdf['Caps'].fillna(0).astype(int)
        awardsdf['Wins'] = awardsdf['Wins'].fillna(0).astype(int)
        pd.options.display.float_format = '{:,.2f}'.format
        
        ranks = [name for name in awardsdf.columns if "_rank" in name]
        awardsdf["RankPts"] = awardsdf[ranks].sum(axis=1)
        awardsdf = awardsdf.sort_values("RankPts")
        awardsdf["RankPts_rank"] = awardsdf["RankPts"].rank(method="min", ascending=True, na_option='bottom')
        columns.append("RankPts")
        columns.append("RankPts_rank")
        
        #awardsdf = awardsdf.fillna(0)
        #Sanity check - all awards shoudld be matching
        #print([name.ljust(16) for name in awardsdf.columns if "rank" not in name])
        #print([name.ljust(16) for name in awardsdf.columns if "rank" in name])
        
        #print(awardsdf[[name for name in awardsdf.columns if "rank" not in name]].sort_values("Kills"))
        
        
        ranks = [name for name in awardsdf.columns if "rank" in name]
        rankmax = len(awardsdf)
        for rank in ranks:
            awardsdf[rank] = awardsdf[rank].fillna(rankmax).astype(int)
    
        #print(awardsdf[[name for name in awardsdf.columns if "_rank" in name]])
           
        return [awardsdf,columns]
    
    '''
    Kill matrix (who killed who how many times)
    '''
    def awards_kill_matrix(self, data):
        event_lines_dataframe = data["logdf"]
        kill_matrix = event_lines_dataframe[event_lines_dataframe.event.isin(["kill","Team kill"])].groupby(["killer","victim"]).count().reset_index().pivot(index = "killer", columns = "victim", values = "event").fillna(0)
        kill_matrix_rank = kill_matrix.rank(method="min", ascending=False, axis = 1)
        result = kill_matrix.join(kill_matrix_rank, rsuffix = "_rank")
        return [result, ""] #just to match others
    
    '''
    Traditional stats
    '''
    def all_stats_matrix(self, data):
        sum_lines_dataframe   = data["stats"]
        
        base_stats = sum_lines_dataframe[[Const.STAT_BASE_KILL, Const.STAT_BASE_DEATHS,Const.STAT_BASE_TK,Const.STAT_BASE_TKd, Const.STAT_BASE_SUI, Const.STAT_BASE_ALLDEATHS]]
        base_stats_sum = base_stats.groupby(base_stats.index).agg({Const.STAT_BASE_KILL : "sum", Const.STAT_BASE_DEATHS : "sum", Const.STAT_BASE_TK : "sum", Const.STAT_BASE_TKd : "sum", Const.STAT_BASE_SUI : "sum", Const.STAT_BASE_ALLDEATHS : "sum"})
        
        #use only round 2 stats
        osp_stats  = sum_lines_dataframe[sum_lines_dataframe["round_num"] == 2][[Const.STAT_OSP_SUM_GIBS, Const.STAT_OSP_SUM_DMG, Const.STAT_OSP_SUM_DMR, Const.STAT_OSP_SUM_TEAMDG]].fillna(0).astype(int)
        osp_stats_sum = osp_stats.groupby(osp_stats.index).agg({Const.STAT_OSP_SUM_GIBS : "sum", Const.STAT_OSP_SUM_DMG : "sum" , Const.STAT_OSP_SUM_DMR : "sum" , Const.STAT_OSP_SUM_TEAMDG : "sum"})

        stats_all_sum = base_stats_sum.join(osp_stats_sum)
        #columns = [Const.STAT_BASE_KILL, Const.STAT_BASE_DEATHS,Const.STAT_BASE_TK,Const.STAT_BASE_TKd, Const.STAT_BASE_SUI, Const.STAT_BASE_ALLDEATHS, Const.STAT_OSP_SUM_GIBS, Const.STAT_OSP_SUM_DMG, Const.STAT_OSP_SUM_DMR, Const.STAT_OSP_SUM_TEAMDG]
        #stats = sum_lines_dataframe[columns]
        stats_all_sum_rank = stats_all_sum.rank(method="min", ascending=False)
        stats_all_sum_rank[[Const.STAT_BASE_DEATHS,Const.STAT_BASE_TK,Const.STAT_BASE_TKd, Const.STAT_BASE_SUI, Const.STAT_BASE_ALLDEATHS,Const.STAT_OSP_SUM_DMR, Const.STAT_OSP_SUM_TEAMDG]] = 0
        stats = stats_all_sum.join(stats_all_sum_rank, rsuffix = "_rank")
        return [stats, ""] #just to match others
    
    '''
    Weapon count awards
    '''
    def award_weapon_counts(self,data):
        event_lines_dataframe = data["logdf"]
        #sum_lines_dataframe   = data["stats"]
        #matches_dataframe     = data["matchesdf"]
        temp = event_lines_dataframe[event_lines_dataframe["event"] == "kill"]
        temp2 = temp.groupby(["killer","mod"]).count().reset_index()
        pd.options.display.float_format = '{:,.0f}'.format
        result = temp2.pivot(index = "killer", columns = "mod", values = "event")
        existing_columns = result.columns
        new_columns = []
        for mod_type in Const.mod_by_type.keys():
            for mod in Const.mod_by_type[mod_type]:
                if mod in existing_columns: 
                    new_columns.append(mod)
                    result[mod + "_rank"] = result[mod].rank(method="min", ascending=False, na_option='keep') 
                    new_columns.append(mod + "_rank")
                else:
                    result[mod] = 0
                    result[mod + "_rank"] = 0
                    new_columns.append(mod)
        return [result.fillna(0), new_columns]
    
    
    
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
            
            #reset kills for players that died
            current_counter[row["victim"]] = 0
        
        resultdict = {}
        for key, value in top_counter.most_common():
            resultdict[key]=value
        resultdf = pd.DataFrame.from_dict(resultdict,orient='index')
        resultdf.columns=['KillStreak']
        resultdf["KillStreak_rank"] = resultdf["KillStreak"].rank(method="min", ascending=False, na_option='bottom')
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
        return resultdf
    
    '''
    Most kills of the night (Slaughterhouse Award from Kris)
    '''
    def award_kills_of_the_night(self,event_lines_dataframe):
        temp = event_lines_dataframe[(event_lines_dataframe.event == "kill")]
        result = temp["killer"].value_counts().to_frame().rename(columns={"killer" : "Kills"})
        result["Kills_rank"] = result["Kills"].rank(method="min", ascending=False, na_option='bottom')  
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
        return result

    '''
    Most times objective reached before timelimit (winning a round on offence)
    '''
    def award_most_caps(self,sum_lines_dataframe):
        temp = sum_lines_dataframe[(sum_lines_dataframe.side == "Offense") & (sum_lines_dataframe.round_win == 1)]
        result = temp.groupby(Const.STAT_BASE_KILLER)[["round_win"]].sum().rename(columns={"round_win" : "Caps"})
        result["Caps_rank"] = result["Caps"].rank(method="dense", ascending=False, na_option='bottom')    
        return result
    
    '''
    Most times defense held to timelimit (winning a round on defense)
    '''
    def award_most_holds(self,sum_lines_dataframe):
        temp = sum_lines_dataframe[(sum_lines_dataframe.side == "Defense") & (sum_lines_dataframe.round_win == 1)]
        result = temp.groupby(Const.STAT_BASE_KILLER)[["round_win"]].sum().rename(columns={"round_win" : "Holds"})
        result["Holds_rank"] = result["Holds"].rank(method="dense", ascending=False, na_option='bottom')    
        return result
    
    '''
    Most wins
    '''
    def award_most_wins(self,sum_lines_dataframe):
        temp = sum_lines_dataframe[sum_lines_dataframe.game_result == "WON"]
        result = temp.groupby(Const.STAT_BASE_KILLER)[["game_result"]].count().rename(columns={"game_result" : "Wins"})
        result["Wins_rank"] = result["Wins"].rank(method="dense", ascending=False, na_option='bottom')    
        return result
    
    '''
    Most useful points
    '''
    def award_most_useful_points(self,sum_lines_dataframe):
        result = sum_lines_dataframe.groupby([Const.STAT_BASE_KILLER])[[Const.STAT_POST_ADJSCORE]].sum()
        result[Const.STAT_POST_ADJSCORE + "_rank"] = result[Const.STAT_POST_ADJSCORE].rank(method="min", ascending=False, na_option='bottom')
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


