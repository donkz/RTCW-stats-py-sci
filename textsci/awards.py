from constants.logtext import Const 
from collections import Counter
import pandas as pd
import numpy as np
import time as _time

class Awards:
    
    def __init__(self, result, amendments = None):
        self.debug_time = False
        self.event_lines_dataframe = result["logs"]
        self.sum_lines_dataframe   = result["stats"]
        self.matches_dataframe     = result["matches"]
        
        temp = self.event_lines_dataframe[(self.event_lines_dataframe.event == "kill")]
        
        self.rounds = self.sum_lines_dataframe["round_guid"].groupby(level=0).nunique().to_frame()
        minrounds = self.sum_lines_dataframe["round_guid"].nunique()/5 #play 20% of the games please!
        self.minrounds = min(40,int(minrounds)) #20% or 40 rounds, which ever is less
        self.rounds.columns = ["Rounds"]
        
        minutes = self.sum_lines_dataframe["round_time"].groupby(level=0).sum()/60
        self.minutes = minutes.fillna(0).astype(int).to_frame()
        self.minutes.columns = ["Minutes"]
        
        people = temp["killer"].append(temp["victim"]).unique()
        self.awardsdf = None
        self.all_people = pd.DataFrame(index=people) #self of all people
        self.amendments = amendments
    
    def collect_awards(self):
        event_lines_dataframe  = self.event_lines_dataframe
        sum_lines_dataframe    = self.sum_lines_dataframe
        #matches_dataframe     = self.sum_lines_dataframe
        awardsdf               = self.all_people
        columns = []
        
        t1 = _time.time()
        
        x = self.award_kills_of_the_night(event_lines_dataframe)
        awardsdf = awardsdf.join(x)
        t2 = _time.time()
        if self.debug_time: print ("Time to process kills is " + str(round((t2 - t1),2)) + " s")
        t1 = t2
            
        x = self.award_efficiency_of_the_night(event_lines_dataframe)
        awardsdf = awardsdf.join(x)
        t2 = _time.time()
        if self.debug_time: print ("Time to process kdr is " + str(round((t2 - t1),2)) + " s")
        t1 = t2
        
        x = self.award_kill_streak(event_lines_dataframe)
        awardsdf = awardsdf.join(x)
        t2 = _time.time()
        if self.debug_time: print ("Time to process killstreak is " + str(round((t2 - t1),2)) + " s")
        t1 = t2
        
        mk = self.award_megakill(event_lines_dataframe) #special for now
        x = mk[0]
        megakilldetail = mk[1]
        awardsdf = awardsdf.join(x)
        t2 = _time.time()
        if self.debug_time: print ("Time to process megakill is " + str(round((t2 - t1),2)) + " s")
        t1 = t2
        
        x = self.award_tapout(sum_lines_dataframe)
        awardsdf = awardsdf.join(x)
        t2 = _time.time()
        if self.debug_time: print ("Time to process tapout is " + str(round((t2 - t1),2)) + " s")
        t1 = t2
        
        x = self.award_negative_weapons("Panzer", [Const.WEAPON_PANZER], Const.PENALTY_PANZ_RANGES)
        awardsdf = awardsdf.join(x)
        t2 = _time.time()
        if self.debug_time: print ("Time to process panz is " + str(round((t2 - t1),2)) + " s")
        t1 = t2
        
        x = self.award_negative_weapons("Smoker", [Const.WEAPON_AS, Const.WEAPON_ART], Const.PENALTY_SMOKER_RANGES)
        awardsdf = awardsdf.join(x)
        t2 = _time.time()
        if self.debug_time: print ("Time to process smoker is " + str(round((t2 - t1),2)) + " s")
        t1 = t2
        
        x = self.award_negative_weapons("Sniper", [Const.WEAPON_SNIPER, Const.WEAPON_MAUSER], Const.PENALTY_SNIPER_RANGES)
        awardsdf = awardsdf.join(x)
        t2 = _time.time()
        if self.debug_time: print ("Time to process sniper is " + str(round((t2 - t1),2)) + " s")
        t1 = t2
        
        x = self.award_most_blown_up(event_lines_dataframe)
        awardsdf = awardsdf.join(x)
        columns.append(x.columns[0])
        columns.append(x.columns[1])
        t2 = _time.time()
        if self.debug_time: print ("Time to process blown up is " + str(round((t2 - t1),2)) + " s")
        t1 = t2
        
        x = self.award_most_panzed(event_lines_dataframe)
        awardsdf = awardsdf.join(x)
        columns.append(x.columns[0])
        columns.append(x.columns[1])
        t2 = _time.time()
        if self.debug_time: print ("Time to process panzed is " + str(round((t2 - t1),2)) + " s")
        t1 = t2
        
        x = self.award_first_in_door(event_lines_dataframe)
        awardsdf = awardsdf.join(x)
        columns.append(x.columns[0])
        columns.append(x.columns[1])
        t2 = _time.time()
        if self.debug_time: print ("Time to process first-in-door is " + str(round((t2 - t1),2)) + " s")
        t1 = t2
        
        x = self.award_most_useful_points(sum_lines_dataframe)
        awardsdf = awardsdf.join(x)
        columns.append(x.columns[0])
        columns.append(x.columns[1])
        t2 = _time.time()
        if self.debug_time: print ("Time to process points is " + str(round((t2 - t1),2)) + " s")
        t1 = t2
        
        x = self.award_most_wins(sum_lines_dataframe)
        awardsdf = awardsdf.join(x)
        t2 = _time.time()
        if self.debug_time: print ("Time to process wins is " + str(round((t2 - t1),2)) + " s")
        t1 = t2
        
        #plug the na wholes with appropriate values
        self.awardsdf = awardsdf
        awardsdf = self.fill_na_values()
        
        #sum all rank points into final RankPts
        ranks = [name for name in awardsdf.columns if "_rank" in name]
        if self.amendments is None or len(self.amendments) == 0:
            print("[ ] Summarizing without amendments")
            awardsdf["RankPts"] = awardsdf[ranks].sum(axis=1)
        else:
            print("[ ] Summarizing with amendments: " + str(self.amendments))
            amend_rank_cols = []
            for i in self.amendments.keys():
                amend_rank_cols.append(i+"_rank")
                
            regular_ranks_cols = [c for c in ranks if c not in amend_rank_cols]
            amended_ranks_cols = amend_rank_cols
            
            tmp_df = pd.DataFrame(index=awardsdf.index)
            for c in amended_ranks_cols:
                tmp_df[c] = awardsdf[c]*self.amendments[c.replace("_rank","")]
            amended_ranks = tmp_df.sum(axis=1).astype(int)
            regular_sum = awardsdf[regular_ranks_cols].sum(axis=1)
            awardsdf["RankPts"] = regular_sum + amended_ranks
        
        #Re-sort by total rank points and rank the ranks yo dawg
        awardsdf = awardsdf.sort_values(["RankPts", "Rounds"], ascending = (True, False))
        awardsdf["RankPts_rank"] = awardsdf["RankPts"].rank(method="min", ascending=True, na_option='bottom')
        columns.append("RankPts")
        columns.append("RankPts_rank")
               
        self.awardsdf = awardsdf
        
        t2 = _time.time()
        if self.debug_time: print ("Time to wrap up awards is " + str(round((t2 - t1),2)) + " s")
        return {"awards" : awardsdf, "megakills" :  megakilldetail}
       
    def fill_na_values(self):
        awardsdf = self.awardsdf
        
        rank_cols, ranked_cols, unranked_cols, inverse_ranked_cols = self.ranked_column_types()
        
        #plug rank wholes
        ranked_cols.remove("RankPts_rank") #at this point the col does not exist
        awardsdf[ranked_cols] = awardsdf[ranked_cols].fillna(Const.RANK_MAX).astype(int)
        awardsdf[unranked_cols] = awardsdf[unranked_cols].fillna(0).astype(int)
        awardsdf[inverse_ranked_cols] = awardsdf[inverse_ranked_cols].fillna(0).astype(int)
                
        #awardsdf['Pack5'] = awardsdf['Pack5'].fillna(0).astype(int)
        awardsdf['Blownup'] = awardsdf['Blownup'].fillna(0).astype(int)
        awardsdf['FirstInDoor'] = awardsdf['FirstInDoor'].astype(str)
        awardsdf['Deathroll'] = awardsdf['Deathroll'].fillna(0).astype(int)
        #awardsdf['Holds'] = awardsdf['Holds'].fillna(0).astype(int)
        #awardsdf['Caps'] = awardsdf['Caps'].fillna(0).astype(int)
        awardsdf['Wins'] = awardsdf['Wins'].fillna(0).astype(int)
        awardsdf['MegaKill'] = awardsdf['MegaKill'].fillna(0).astype(int)
        awardsdf['Panzed'] = awardsdf['Panzed'].fillna(0).astype(int)

        return awardsdf

    def ranked_column_types(self):
        rank_cols = [c for c in self.awardsdf.columns if c.endswith('_rank')]
        #ranked_cols = [c for c in self.awardsdf.columns[self.awardsdf.max() >0] if c.endswith('_rank')]
        ranked_cols = ['KPM_rank', 'KDR_rank', 'KillStreak_rank', 'MegaKill_rank', 'Panzer_rank', 'Smoker_rank', 'FirstInDoor_rank', 'AdjScore_rank', 'Win%_rank', 'RankPts_rank']
        #unranked_cols = [c for c in self.awardsdf.columns[self.awardsdf.max() == 0] if c.endswith('_rank')]
        unranked_cols = ['Kills_rank', 'Minutes_rank', 'Rounds_rank','Deathroll_rank', 'Blownup_rank', 'Panzed_rank', 'Wins_rank']
        inverse_ranked_cols = ['Panzer_rank', 'Smoker_rank', 'Sniper_rank', 'Tapout_rank']
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
        
        result = result.join(self.rounds, how='outer')
        result["FirstInDoor"] = result["FirstInDoor"]/result["Rounds"]
        result["FirstInDoor"] = result["FirstInDoor"].fillna(0)

        result.loc[result[result["Rounds"] < self.minrounds].index, "FirstInDoor"] = result.loc[result[result["Rounds"] < self.minrounds].index, "FirstInDoor"].multiply(-1)
        result["FirstInDoor_rank"] = result["FirstInDoor"].rank(method="min", ascending=False, na_option='bottom') 
        result.loc[result[result["FirstInDoor_rank"] > 4].index, "FirstInDoor_rank"] = 5

        result["FirstInDoor"] = result["FirstInDoor"].round(2).multiply(100).astype(int).apply(lambda x: '{0:0>2}'.format(x))+"%"        
        result["FirstInDoor"] = result["FirstInDoor"].replace("100%","X%").replace("00%","0%").replace("X%","100%")
        result.drop(["Rounds"], axis=1, inplace=True)
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
    
    def award_negative_weapons(self, weapon_name, weapon_list, penalty_list):
        #debug: event_lines_dataframe = result["logs"].copy()
        result_all = self.all_people
        weapon_kills_str = weapon_name + "kills"
        weapon_rank_str = weapon_name + "_rank"
        event_lines_dataframe = self.event_lines_dataframe
        
        temp = event_lines_dataframe[(event_lines_dataframe.event == "kill")]
        kills = temp["killer"].value_counts().to_frame().rename(columns={"killer" : "Kills"})
        result_all= result_all.join(kills)
        
        #select only kill events by LT
        temp2 = event_lines_dataframe[(event_lines_dataframe["event"] == "kill") & ((event_lines_dataframe["mod"].isin(weapon_list)))]
        weapon_kills = temp2["killer"].value_counts().to_frame()
        weapon_kills.columns = [weapon_kills_str]
        
        resultdf= result_all.join(weapon_kills).fillna(0)
        resultdf[weapon_name] = resultdf[weapon_kills_str]/resultdf["Kills"]
        
        '''
        old penalty ranking logic
        resultdf[weapon_rank_str] = resultdf[weapon_name].rank(method="dense", ascending=True, na_option='top') #na = top = 0
        scale_down_factor = penalty - resultdf[weapon_rank_str].max()
        resultdf[weapon_rank_str] = resultdf[weapon_rank_str] + scale_down_factor 
        resultdf.loc[resultdf[resultdf[weapon_rank_str] < 0].index, weapon_rank_str] = 0
        '''
        
        resultdf[weapon_rank_str] = 0
        for penalty, threshold in enumerate(penalty_list):
            resultdf.loc[resultdf[resultdf[weapon_name] > threshold].index, weapon_rank_str] = penalty
        
        resultdf.drop(['Kills',weapon_kills_str], axis=1, inplace=True)
        resultdf[weapon_name] = resultdf[weapon_name].fillna(0).round(2).multiply(100).astype(int).apply(lambda x: '{0:0>2}'.format(x))+"%"
        resultdf[weapon_name] = resultdf[weapon_name].replace("100%","X%").replace("00%","0%").replace("X%","100%")
        return resultdf
     
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
        t1 = _time.time()
        
        event_lines_dataframe = event_lines_dataframe.reset_index()
        del event_lines_dataframe["index"]
        temp = event_lines_dataframe[["event","killer","round_order"]]
        
        first = True
        megadict = {} # killer : [count, line_index, count_max, [line_index_max1....line_index_maxn]]
        for row in temp.itertuples():
            if first:
                curr_row = row
                first = False
                megadict[curr_row.killer] = [1, curr_row.Index, 0, [0]]
            else:
                prev_row = curr_row
                curr_row = row
                #if current event is a kill and next event is a kill and killer is the same, set next count to +1
                if curr_row.event == "kill":
                    if prev_row.event == "kill" and prev_row.killer == curr_row.killer and prev_row.round_order == curr_row.round_order:
                        stat = megadict[curr_row.killer]
                        current_kill_count = stat[0]+1
                        if current_kill_count == stat[2]:
                            megadict[curr_row.killer] = [current_kill_count, curr_row.Index, current_kill_count, stat[3] + [curr_row.Index]]
                        elif current_kill_count > stat[2]:
                            #print(megadict[curr_row.killer])
                            megadict[curr_row.killer] = [current_kill_count, curr_row.Index, current_kill_count, [curr_row.Index]]
                        else:    
                            megadict[curr_row.killer] = [current_kill_count, curr_row.Index, stat[2], stat[3]]
                    else:
                        if curr_row.killer in megadict:
                            stat = megadict[curr_row.killer]                        
                            megadict[curr_row.killer] = [1, curr_row.Index, stat[2], stat[3]]
                        else: 
                            megadict[curr_row.killer] = [1, curr_row.Index, 1, [curr_row.Index]]
            
        #select max kills for each player
        result = pd.DataFrame(megadict).transpose()
        result.columns  = ["count","idx","MegaKill","idxmax"]
        
        #result["MegaKill_rank"] = result["MegaKill"].rank(method="min", ascending=False, na_option='bottom')
        #result.loc[result[result["MegaKill_rank"] > 4].index, "MegaKill_rank"] = 5
        self.apply_rank_range(result, "MegaKill", Const.RANK_RANGE_MEGAKILL)
        
        t2 = _time.time()
        if self.debug_time: print ("Time to process megakills1 is " + str(round((t2 - t1),2)) + " s")
        t1 = t2
        
        #extract actual megakills (3 or more)
        #max_mk = result[result["MegaKill"] >= result["MegaKill"].quantile(.8)]["MegaKill"].min()
        max_mk = 3
        tmp_result = result[result["MegaKill"] >= max_mk][['MegaKill', 'idxmax']] #extract info or 3 or more kills in a row
        megakills = pd.DataFrame()
        for row in tmp_result.itertuples(index=False):
            indexmaxes = row.idxmax
            kill_count = row.MegaKill
            for i in indexmaxes:
                df = event_lines_dataframe.iloc[i-kill_count+1 : i+1].copy()
                df["count"] = kill_count
                megakills = megakills.append(df)
        
        megakills["count"] = megakills["count"].astype(int)
        
        time_and_map = self.matches_dataframe[["match_date","map","round_guid"]]
        megakills2 = megakills.merge(time_and_map, on='round_guid', how='inner', suffixes=('_events', '_matches'))
        
        result.drop(["count","idx","idxmax"], axis=1, inplace=True)
        
        t2 = _time.time()
        if self.debug_time: print ("Time to process megakills2 is " + str(round((t2 - t1),2)) + " s")
        return [result, megakills2[["match_date","map", "killer", "mod", "victim","count"]]]
    
    '''
    (most) Kills in a row award
    Determine who had most kills without dying
    '''
    def award_kill_streak(self,event_lines_dataframe):
        current_kill_counter = Counter()    
        top_kill_counter = Counter()
        current_deaths_counter = Counter()    
        top_deaths_counter = Counter()
        
        #select only kill events
        temp = event_lines_dataframe[event_lines_dataframe["event"] == "kill"][["killer","victim"]]
        
        #for every row    
        for line in temp.itertuples():
            #count a kill for a player
            current_kill_counter[line.killer] += 1
            current_deaths_counter[line.victim] += 1

            #if it is their record kill streak, save it
            if(current_kill_counter[line.killer] > top_kill_counter[line.killer]):
                top_kill_counter[line.killer] = current_kill_counter[line.killer]
            
            if(current_deaths_counter[line.victim] > top_deaths_counter[line.victim]):
                top_deaths_counter[line.victim] = current_deaths_counter[line.victim]
           
            #reset kills for players that died
            current_kill_counter[line.victim] = 0
            current_deaths_counter[line.killer] = 0
            
            debug = False
            if debug:
                debug_player = "/mute eternal"
                if line.killer ==debug_player or line.victim ==debug_player:
                    print(line)
                    print(current_kill_counter[debug_player], current_deaths_counter[debug_player])
        
        resultdict = {}
        for key, value in top_kill_counter.most_common():
            resultdict[key]=value
            
        resultkill = pd.DataFrame.from_dict(dict(top_kill_counter),orient='index')
        resultdeath = pd.DataFrame.from_dict(dict(top_deaths_counter),orient='index')
        resultkill.columns=['KillStreak']
        resultdeath.columns=['Deathroll']
        resultdf = resultkill.join(resultdeath)
        
        #resultdf["KillStreak_rank"] = resultdf["KillStreak"].rank(method="min", ascending=False, na_option='bottom')
        #resultdf.loc[resultdf[resultdf["KillStreak_rank"] > 4].index, "KillStreak_rank"] = 5
        self.apply_rank_range(resultdf, "KillStreak", Const.RANK_RANGE_KILLSTREAK)
        
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
        #result["Kills_rank"] = result["Kills"].rank(method="min", ascending=False, na_option='bottom')  
        #result.loc[result[result["Kills_rank"] > 4].index, "Kills_rank"] = 5
        
        
        result = result.join(self.minutes, how="outer")
        result = result.join(self.rounds, how="outer")
        result["Kills"] = result["Kills"].fillna(0)
        result["Kills_rank"] = 0
        
        result["KPM"] = result["Kills"]/result["Minutes"]
        result["KPM"] = result["KPM"].round(2)
        result.loc[result[result["Rounds"] < self.minrounds].index, "KPM"] = result.loc[result[result["Rounds"] < self.minrounds].index, "KPM"].multiply(-1)
        result["KPM_rank"] = result["KPM"].rank(method="min", ascending=False, na_option='bottom')
        result["KPM_rank"] = result["KPM_rank"]/2 #since there are 2 teams , split rankings on 2
        result["KPM_rank"] = result["KPM_rank"].apply(np.ceil).astype(int)
        result.loc[result[result["KPM_rank"] > 7].index, "KPM_rank"] = 8
        
        result["Minutes_rank"] = 0
        result["Rounds_rank"] = 0
        
        return result[['Minutes','Minutes_rank','Rounds','Rounds_rank', 'KPM', 'KPM_rank', 'Kills', 'Kills_rank']]
    
    '''
    Best efficiency of the night (Terminator Award from Kris)
    '''
    def award_efficiency_of_the_night(self,event_lines_dataframe):
        #pd.options.display.float_format = '{:,.2f}'.format
        temp = event_lines_dataframe[(event_lines_dataframe.event == "kill")]
        resultk = temp["killer"].value_counts()
        resultd = temp["victim"].value_counts()
        
        result = pd.DataFrame({"KDR" : resultk/resultd}).round(2)
        result = result.join(self.rounds, how="outer")
        result.loc[result[result["Rounds"] < self.minrounds].index, "KDR"] = result.loc[result[result["Rounds"] < self.minrounds].index, "KDR"].multiply(-1)
        result["KDR_rank"] = result["KDR"].rank(method="min", ascending=False, na_option='bottom')   
        
        #since there are 2 teams , split rankings on 2
        result["KDR_rank"] = result["KDR_rank"]/2
        result["KDR_rank"] = result["KDR_rank"].apply(np.ceil).astype(int)
        result.loc[result[result["KDR_rank"] > 7].index, "KDR_rank"] = 8
        result.drop(["Rounds"], axis=1, inplace=True)
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
        temp = sum_lines_dataframe[sum_lines_dataframe.game_result == "WON"][["Killer","game_result"]]
        result = temp.groupby(Const.STAT_BASE_KILLER)[["game_result"]].count().rename(columns={"game_result" : "Wins"})
        result["Wins_rank"] = 0
        
        result = result.join(self.rounds, how='outer')
        
        result["full_games"] = result["Rounds"].div(2).apply(np.ceil)
        result["Win%"] = result["Wins"]/result["full_games"]
        result["Win%"] = result["Win%"].fillna(0).round(2)
        result.loc[result[result["Rounds"] < self.minrounds].index, "Win%"] = result.loc[result[result["Rounds"] < self.minrounds].index, "Win%"].multiply(-1)
        
        
        #result["Win%_rank"] = result["Win%"].rank(method="dense", ascending=False, na_option='bottom') 
        #result.loc[result[result["Win%_rank"] > 5].index, "Win%_rank"] = 6
        self.apply_rank_range(result, "Win%", Const.RANK_RANGE_WINS)
        
        result["Win%"] = result["Win%"].round(2).multiply(100).astype(int).apply(lambda x: '{0:0>2}'.format(x))+"%"  
        result["Win%"] = result["Win%"].replace("100%","X%").replace("00%","0%").replace("X%","100%")
        result.drop(["Rounds", "full_games"], axis=1, inplace=True)
        
        return result
    
    '''
    Most useful points
    '''
    def award_most_useful_points(self,sum_lines_dataframe):
        result = sum_lines_dataframe.groupby([Const.STAT_BASE_KILLER])[[Const.STAT_POST_ADJSCORE]].sum()
        
        result = result.join(self.rounds)
        result[Const.STAT_POST_ADJSCORE] = result[Const.STAT_POST_ADJSCORE]/result["Rounds"]
        result[Const.STAT_POST_ADJSCORE] = result[Const.STAT_POST_ADJSCORE].round(1)
        result.loc[result[result["Rounds"] < self.minrounds].index, Const.STAT_POST_ADJSCORE] = result.loc[result[result["Rounds"] < self.minrounds].index, Const.STAT_POST_ADJSCORE].multiply(-1)
        result[Const.STAT_POST_ADJSCORE + "_rank"] = result[Const.STAT_POST_ADJSCORE].rank(method="min", ascending=False, na_option='bottom')
        result.loc[result[result[Const.STAT_POST_ADJSCORE + "_rank"] > 4].index, Const.STAT_POST_ADJSCORE + "_rank"] = 5
        result.drop(["Rounds"], axis=1, inplace=True)
        return result
    
    '''
    Suicide/Tapout (penalty)
    Determine who suiceides the most and penilize them
    '''
    def award_tapout(self,sum_lines_dataframe):
        #debug: sum_lines_dataframe = result["stats"].copy()

        base_stats_sum = sum_lines_dataframe.groupby(sum_lines_dataframe.index).agg({Const.STAT_BASE_KILL : "sum", Const.STAT_BASE_DEATHS : "sum", Const.STAT_BASE_SUI : "sum"})
        base_stats_sum["Tapout"] = base_stats_sum["Suicides"]/(base_stats_sum["Deaths"] + base_stats_sum["Suicides"])
        resultdf = self.all_people
        base_stats_sum.drop(['Kills', 'Deaths', 'Suicides'], axis=1, inplace=True)
        resultdf = resultdf.join(base_stats_sum)
       
        resultdf["Tapout_rank"] = 0
        resultdf.loc[resultdf[resultdf["Tapout"] > 0.25].index, "Tapout_rank"] = 1
        resultdf.loc[resultdf[resultdf["Tapout"] > 0.33].index, "Tapout_rank"] = 2
        resultdf.loc[resultdf[resultdf["Tapout"] > 0.40].index, "Tapout_rank"] = 3
     
        resultdf["Tapout"] = resultdf["Tapout"].round(2).multiply(100).astype(int).apply(lambda x: '{0:0>2}'.format(x))+"%"
        resultdf["Tapout"] = resultdf["Tapout"].replace("100%","X%").replace("00%","0%").replace("X%","100%")
        return resultdf
    
    def apply_rank_range(self, df, column, rank_range):
        r"""
        Attach a new column with rank values
        
        Parameters
        ----------
        df: dataframe 
        column: column with values that need ranked
        rank_range: what ranges to apply to values to rank them
        
        Returns
        ----------
        dataframe with a new column containing ranks
        """
        column_rank_name = column + "_rank"
        
        max_rank = len(rank_range) + 1 #supposedly 5
        df[column_rank_name] = max_rank
        for i, threshold in enumerate(rank_range[::-1],1):
            df.loc[df[df[column] >= threshold].index, column_rank_name] = max_rank - i
        
        
 
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


'''
panz 20 30 40 50 60 [0,0.10,0.30,0.40,0.50,0.60]# 0-5 penalty
lt 10 15 20 [0,0.1,0.15,0.2] # 0-3 penalty 
sniper 5 10 [0,0.05,0.1] # 0-2 penalty
tapout [0,0.25,0.33,0.4] # 0-3 penalty
'''