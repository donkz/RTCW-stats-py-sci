from constants.logtext import Const 
import pandas as pd


class MatchStats:
    #debug data = results
    
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
    
    def match_info_datetime(self,data):
        matches_dataframe     = data["matchesdf"]
        time_of_the_match = matches_dataframe[0:1][['log_date']].values[0][0]
        return time_of_the_match
    
    def table_match_results(self, data):
        matches_dataframe     = data["matchesdf"]
        temp = matches_dataframe[['round_order','map', 'round_num','round_diff', 'round_time', 'winner', 'players']]      
        return [temp,""]
    
    def table_map_list(self, data):
        sum_lines_dataframe   = data["stats"]
        result = sum_lines_dataframe[sum_lines_dataframe["round_num"] == 2].groupby(["round_order","map"]).count().reset_index().groupby(["map"]).agg({"round_order":["min","count"]}).sort_values([("round_order","min")])
        result.columns = ["order","games"]
        result.reset_index(inplace=True)
        return [result, ""]
    
    def table_player_joins(self, data):
        event_lines_dataframe = data["logdf"]
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
        event_lines_dataframe = data["logdf"]
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
        stats_all_sum["KDR"] = (stats_all_sum[Const.STAT_BASE_KILL]/stats_all_sum[Const.STAT_BASE_DEATHS]).round(1)
        stats_all_sum["KPR"] = (stats_all_sum[Const.STAT_BASE_KILL]/stats_all_sum["Rounds"]).round(1)
        stats_all_sum["DPR"] = (stats_all_sum[Const.STAT_OSP_SUM_DMG]/stats_all_sum["Rounds"]).astype(int)
        stats_all_sum["DPF"] = (stats_all_sum[Const.STAT_OSP_SUM_DMG]/stats_all_sum[Const.STAT_BASE_KILL]).astype(int)
        
        
        #columns = [Const.STAT_BASE_KILL, Const.STAT_BASE_DEATHS,Const.STAT_BASE_TK,Const.STAT_BASE_TKd, Const.STAT_BASE_SUI, Const.STAT_BASE_ALLDEATHS, Const.STAT_OSP_SUM_GIBS, Const.STAT_OSP_SUM_DMG, Const.STAT_OSP_SUM_DMR, Const.STAT_OSP_SUM_TEAMDG]
        #stats = sum_lines_dataframe[columns]
        stats_all_sum_rank = stats_all_sum.rank(method="min", ascending=False)
        stats_all_sum_rank[[Const.STAT_BASE_DEATHS,Const.STAT_BASE_TK,Const.STAT_BASE_TKd, Const.STAT_BASE_SUI, Const.STAT_BASE_ALLDEATHS,Const.STAT_OSP_SUM_DMR, Const.STAT_OSP_SUM_TEAMDG]] = 0
        stats = stats_all_sum.join(stats_all_sum_rank, rsuffix = "_rank")
        return [stats, ""] #just to match others
    
    '''
    Weapon count awards
    '''
    def table_weapon_counts(self,data):
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
    
    
    
    

