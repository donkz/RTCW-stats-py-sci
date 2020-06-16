from constants.logtext import Const 
import pandas as pd

class MatchStats:
    #debug data = results
    
    def match_metrics(self, data):
        matches_dataframe     = data["matches"]
        #event_lines_dataframe = data["logs"]
        sum_lines_dataframe   = data["stats"]
        
        metrics = {}
        metrics["players_count"] = len(sum_lines_dataframe.index.unique())
        metrics["match_time"] = matches_dataframe[Const.NEW_COL_MATCH_DATE].min()
        metrics["rounds_count"] = matches_dataframe["round_guid"].nunique()
        metrics["maps_count"] = len(matches_dataframe["map"].unique())
        metrics["kill_sum"] = int(sum_lines_dataframe["Kills"].sum())  
        
        return metrics
    
    def match_players(self, data):
        sum_lines_dataframe   = data["stats"]
        tmp = sum_lines_dataframe[["Killer","round_guid"]].groupby("Killer").count().reset_index()      
        tmp["alias"] = ""
        players = tmp[["Killer","alias", "round_guid"]]
        players.columns = ["killer","alias","rounds_played"]
        print(players.to_csv(index=False, sep="\t"))
    
    def match_info_datetime(self,data):
        matches_dataframe     = data["matches"]
        time_of_the_match = matches_dataframe[Const.NEW_COL_MATCH_DATE].min()
        return time_of_the_match
    
    def table_match_results(self, data):
        matches_dataframe     = data["matches"]
        temp = matches_dataframe[['round_order','map', 'round_num','round_diff', 'round_time', 'winner', 'players', 'match_date']]      
        return [temp,""]
    
    '''
    list which maps have been played that night
    map             order  games
    Escape              2     4
    Ice                10     3
    Frostbite          17     1
    Password           19     1
    Sub                21     1
    Chateau            23     1
    '''
    def table_map_list(self, data):
        sum_lines_dataframe   = data["stats"]
        result = sum_lines_dataframe[sum_lines_dataframe["round_num"] == 2].groupby(["round_order","map"]).count().reset_index().groupby(["map"]).agg({"round_order":["min","count"]}).sort_values([("round_order","min")])
        result.columns = ["order","games"]
        result.reset_index(inplace=True)
        return [result, ""]
    
    def table_renames(self,data):
        try:
            result = data["renames"]
        except: 
            result = None
            
        return [result, ""]
        
        
    def table_player_joins(self, data):
        event_lines_dataframe = data["logs"]
        temp = event_lines_dataframe[(event_lines_dataframe.event == "kill")][["line_order", "killer", "victim"]]
        temp2 = (temp[["killer", "line_order"]].rename(columns={"killer": "player"})).append(temp[["victim", "line_order"]].rename(columns={"victim": "player"}))
        playermax = temp2.groupby("player").max().sort_values("line_order")["line_order"]
        playermin = temp2.groupby("player").min().sort_values("line_order")["line_order"]
        col1 = playermin.append(playermax)
        col2 = pd.Series(["min"]).repeat(len(playermin)).append(pd.Series(["max"]).repeat(len(playermax)))
        result = col1.to_frame()
        result['kek'] = col2.values
        
        
    
    '''
    Kill matrix (who killed who how many times)
    '''
    def table_kill_matrix(self, data):
        event_lines_dataframe = data["logs"]
        kill_matrix = event_lines_dataframe[event_lines_dataframe.event.isin(["kill","Team kill"])].groupby(["killer","victim"]).count().reset_index().pivot(index = "killer", columns = "victim", values = "event").fillna(0)
        kill_matrix_rank = kill_matrix.rank(method="min", ascending=False, axis = 1)
        result = kill_matrix.join(kill_matrix_rank, rsuffix = "_rank")
        return [result, ""] #just to match others
    
    '''
    Traditional stats
    '''
    def table_base_stats(self, data):
        sum_lines_dataframe   = data["stats"]
        
        #stats using base data
        #base_stats = sum_lines_dataframe[[Const.STAT_BASE_KILL, Const.STAT_BASE_DEATHS,Const.STAT_BASE_TK,Const.STAT_BASE_TKd, Const.STAT_BASE_SUI, Const.STAT_BASE_ALLDEATHS]]
        base_stats_sum = sum_lines_dataframe.groupby(sum_lines_dataframe.index).agg({Const.STAT_BASE_KILL : "sum", Const.STAT_BASE_DEATHS : "sum", Const.STAT_BASE_TK : "sum", Const.STAT_BASE_TKd : "sum", Const.STAT_BASE_SUI : "sum", Const.STAT_BASE_ALLDEATHS : "sum", Const.STAT_BASE_KILLER : "count" })
        base_stats_sum.rename(columns={Const.STAT_BASE_KILLER : "Rounds"}, inplace=True)
        #stats using osp data
        #use only round 2 stats
        osp_stats  = sum_lines_dataframe[sum_lines_dataframe["round_num"] == 2][[Const.STAT_OSP_SUM_GIBS, Const.STAT_OSP_SUM_DMG, Const.STAT_OSP_SUM_DMR, Const.STAT_OSP_SUM_TEAMDG]].fillna(0).astype(int)
        osp_stats_sum = osp_stats.groupby(osp_stats.index).agg({Const.STAT_OSP_SUM_GIBS : "sum", Const.STAT_OSP_SUM_DMG : "sum" , Const.STAT_OSP_SUM_DMR : "sum" , Const.STAT_OSP_SUM_TEAMDG : "sum"})
        
        #Join base and OSP
        stats_all_sum = base_stats_sum.join(osp_stats_sum)
        
        #derived stats
        pd.options.mode.use_inf_as_na = True
        stats_all_sum["KDR"] = (stats_all_sum[Const.STAT_BASE_KILL]/stats_all_sum[Const.STAT_BASE_DEATHS]).fillna(0).round(1)
        stats_all_sum["KPR"] = (stats_all_sum[Const.STAT_BASE_KILL]/stats_all_sum["Rounds"]).fillna(0).round(1)
        stats_all_sum["DPR"] = (stats_all_sum[Const.STAT_OSP_SUM_DMG]/stats_all_sum["Rounds"]).fillna(0).astype(int)
        stats_all_sum["DPF"] = (stats_all_sum[Const.STAT_OSP_SUM_DMG]/stats_all_sum[Const.STAT_BASE_KILL]).fillna(0).astype(int)
        
        
        #columns = [Const.STAT_BASE_KILL, Const.STAT_BASE_DEATHS,Const.STAT_BASE_TK,Const.STAT_BASE_TKd, Const.STAT_BASE_SUI, Const.STAT_BASE_ALLDEATHS, Const.STAT_OSP_SUM_GIBS, Const.STAT_OSP_SUM_DMG, Const.STAT_OSP_SUM_DMR, Const.STAT_OSP_SUM_TEAMDG]
        #stats = sum_lines_dataframe[columns]
        stats_all_sum_rank = stats_all_sum.rank(method="min", ascending=False)
        stats_all_sum_rank[[Const.STAT_BASE_DEATHS,Const.STAT_BASE_TK,Const.STAT_BASE_TKd, Const.STAT_BASE_SUI, Const.STAT_BASE_ALLDEATHS,Const.STAT_OSP_SUM_DMR, Const.STAT_OSP_SUM_TEAMDG,"DPF"]] = 0
        stats = stats_all_sum.join(stats_all_sum_rank, rsuffix = "_rank")
        return [stats, ""] #just to match others
    
    '''
    Weapon count awards
    '''
    def table_weapon_counts(self,data):
        event_lines_dataframe = data["logs"]
        
        pivoted_weapons = self.weapon_pivot(event_lines_dataframe)
        
        #summarize some things
        pivoted_weapons["Smokes"] = pivoted_weapons["Airstrike"] + pivoted_weapons["Artillery"]
        pivoted_weapons["Pistols"] = pivoted_weapons["Luger"] + pivoted_weapons["Colt"]
        pivoted_weapons["SMGs"] = pivoted_weapons["MP40"] + pivoted_weapons["Thompson"] + pivoted_weapons["Sten"]
        pivoted_weapons.drop(["Airstrike","Artillery","Luger","Colt","MP40","Thompson","Sten"], axis=1, inplace = True)
        
        #re-order
        pivoted_weapons = pivoted_weapons[['SMGs','Pistols','Grenade','Smokes','Panzerfaust', 'Sniper','Venom', 'Flame', 'Dynamite', 'MG42', 'Knife']]
        pivoted_weapons = pivoted_weapons.loc[(pivoted_weapons.sum(axis=1) != 0), (pivoted_weapons.sum(axis=0) != 0)]
        
        
        #add total
        #pivoted_weapons = pivoted_weapons.reset_index()
        total = pivoted_weapons.sum(axis=0).to_frame().T
        total.index = ["Total"]
        pivoted_weapons = pivoted_weapons.append(total)
        kills = pivoted_weapons.sum(axis=1)
        
        #kills = kills[kills > 0]
        #pivoted_weapons = pivoted_weapons[pivoted_weapons["kills"] > 0]
        pivoted_weapons_perc = pivoted_weapons.div(kills, axis=0).mul(100).round(1).fillna(0)
        pivoted_weapons = pivoted_weapons.join(pivoted_weapons_perc, lsuffix="_kills")
        
        columns = list(pivoted_weapons_perc.columns)
        pivoted_weapons["Kills"] = kills
        columns = ["Kills"] + columns
        
        pivoted_weapons = pivoted_weapons[pivoted_weapons["Kills"]>0]
        for column in columns[1:]:
            pivoted_weapons[column] = pivoted_weapons[column].apply(lambda x: '{0:0>4}'.format(x)).astype(str)+"%"
        return [pivoted_weapons.replace("00.0%","0%"), columns]
    
    def weapon_pivot(self, event_lines_dataframe):
        temp = event_lines_dataframe[event_lines_dataframe["event"] == "kill"]
        temp2 = temp.groupby(["killer","mod"]).count().reset_index()
        result = temp2.pivot(index = "killer", columns = "mod", values = "event")
        
        existing_columns = result.columns
        
        for mod_type in Const.mod_by_type.keys():
            for mod in Const.mod_by_type[mod_type]:
                if mod not in existing_columns: 
                    result[mod] = 0        
        return result.fillna(0).astype(int) #https://stackoverflow.com/questions/46859400/pandas-pivot-changes-dtype
    
    '''
    Who killed who how many times (top10)
    Replaces Kill matrix
    '''
    def table_top_feuds(self,data):
        event_lines_dataframe = data["logs"]
        temp = event_lines_dataframe[event_lines_dataframe["event"] == "kill"]
        left = temp.groupby(["killer","victim"]).count().reset_index()[["killer","victim","event"]]
        left.index = left["killer"]+left["victim"]
        right = left.copy()
        right.index = left["victim"]+left["killer"]
        right = right[["event"]]
        
        left.columns = ['killer', 'victim', 'left']
        right.columns = ["right"]
        
        joined = left.join(right).dropna()
        joined["right"] = joined["right"].astype(int)
        joined["key"] = joined.index
        joined.index = ["".join(sorted(a)) for a in joined.index.values]
        unique = joined[["left","key"]].groupby(level=0).max()
        unique.index = unique["key"]
        joined.index = joined["key"]
        unique["keep"] = 1
        joined = joined.join(unique["keep"])
        joined = joined[joined["keep"]==1]
        result = joined[['killer','left','right','victim']].copy()
        result.columns = ['P1','left','right','P2']
        result["sum"]=result["right"]+result["left"]
        result = result.sort_values("sum").tail(20).reset_index(drop=True)
        return [result[['P1', 'left', 'right', 'P2']],['PlayerA', '', '', 'PlayerB']]
    
    def table_best_friends(self, data):
        sum_lines_dataframe   = data["stats"]
        sr2 = sum_lines_dataframe[sum_lines_dataframe["round_num"]==2][["game_result", "round_guid", Const.STAT_OSP_SUM_TEAM]]
        sr2 = sr2.reset_index()
        sr2 = sr2.dropna()
        sr2.columns = ['friend', 'game_result', 'round_guid', "team"]
        sr2b = sr2.copy()
        
        joined = sr2.merge(sr2b, left_on=['team', 'round_guid'], right_on = ['team', 'round_guid'], how='left', suffixes=('-a','-b'))
        joined = joined.drop(["game_result-b"],axis=1).rename(columns={"game_result-a" : "game_result"})
        joined = joined[joined["friend-a"] != joined["friend-b"]]
        joined["key"] = joined["friend-a"] + joined["friend-b"] + joined["round_guid"] + joined['team']
        joined["keysort"] = ["".join(sorted(a)) for a in joined["key"]]
        joined["num"] = 1
        
        no_dups = joined.sort_values(by=["friend-a","round_guid"]).drop_duplicates(subset = ["keysort"], keep = "first", inplace=False)
        
        pairgames = no_dups[["friend-a","friend-b","num"]].groupby(["friend-a","friend-b"]).sum().reset_index()
        wins = no_dups[no_dups["game_result"]=="WON"][["friend-a","friend-b","num"]].groupby(["friend-a","friend-b"]).sum().reset_index()
        losses = no_dups[no_dups["game_result"]=="LOST"][["friend-a","friend-b","num"]].groupby(["friend-a","friend-b"]).sum().reset_index()
        fh = no_dups[no_dups["game_result"]=="FULLHOLD"][["friend-a","friend-b","num"]].groupby(["friend-a","friend-b"]).sum().reset_index()
        
        
        pairgames.columns = ['friend-a', 'friend-b', 'games']
        wins.columns = ['friend-a', 'friend-b', 'won']
        losses.columns = ['friend-a', 'friend-b', 'lost']
        fh.columns = ['friend-a', 'friend-b', 'fullhold']
        
        final = pairgames.merge(wins, left_on=['friend-a', 'friend-b'], right_on = ['friend-a', 'friend-b'], how='left').merge(losses, left_on=['friend-a', 'friend-b'], right_on = ['friend-a', 'friend-b'], how='left').merge(fh, left_on=['friend-a', 'friend-b'], right_on = ['friend-a', 'friend-b'], how='left')
        final = final.fillna(0)
        final["win%"] = final["won"]/final["games"]*100
        final["loss%"] = final["lost"]/final["games"]*100
        final["fullhold%"] = final["fullhold"]/final["games"]*100
        
        desired_num_rows = 30 
        min_games_together = 20 
        min_win_ratio = 50
        
        #topx = final["games"].sort_values().tail(desired_num_rows).min()
        #topx = topx if topx > min_games_together else min_games_together
        final = final[(final["games"]>=min_games_together) & (final["win%"]>= min_win_ratio)]
        
        final = final.round(1)
        final["won"] = final["won"].astype(int)
        final["lost"] = final["lost"].astype(int)
        final["fullhold"] = final["fullhold"].astype(int)
        final = final.sort_values(by="win%", ascending=False).head(desired_num_rows).reset_index().drop(["index"],axis=1)
        return final[['friend-a', 'friend-b', 'games', 'win%', 'loss%', 'fullhold%']]
    
    
    

