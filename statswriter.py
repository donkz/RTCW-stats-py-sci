import os
import pandas as pd

class StatsWriter:
    """Class docstrings go here."""

    def __init__(self, media, rootpath, subpath):
        """Class method docstrings go here."""
        self.filepath = None
        self.connection = None
        
        if media == "disk": 
            self.filepath = rootpath + subpath
            self.connection = "dud"
        elif media == "cloud": 
            print("[x] Method is not ready")
            exit()
        elif media == "nosql": 
            print("[x] Method is not ready")
            exit()
        else:
            print("[x] StatsWriter: Unknown media type.")
            exit()
    
    def correct_castings(df, df_name):
        if df_name == "stats":
            colum_types = {
                    'AdjScore' : 'int',
                    'All_Deaths' : 'int',
                    'Deaths' : 'int',
                    'Killer' : 'str',
                    'Kills' : 'int',
                    'OSP_Damage_Given' : 'int',
                    'OSP_Damage_Received' : 'int',
                    'OSP_Deaths' : 'int',
                    'OSP_Eff' : 'int',
                    'OSP_Gibs' : 'int',
                    'OSP_Kills' : 'int',
                    'OSP_Player' : 'str',
                    'OSP_Score' : 'int',
                    'OSP_Suicides' : 'int',
                    'OSP_TK' : 'int',
                    'OSP_Team' : 'str',
                    'OSP_Team_Damage' : 'int',
                    'Suicides' : 'int',
                    'TK' : 'int',
                    'TKd' : 'int',
                    'game_result' : 'str',
                    'map' : 'str',
                    'match_date' : 'str',
                    'osp_guid' : 'str',
                    'player_strip' : 'str',
                    'round_guid' : 'str',
                    'round_num' : 'int',
                    'round_order' : 'int',
                    'round_win' : 'int',
                    'side' : 'str',
                    'team_name' : 'str'
                   }
            default_values = {
                    'AdjScore' : 0,
                    'All_Deaths' : 0,
                    'Deaths' : 0,
                    'Kills' : 0,
                    'OSP_Damage_Given' : 0,
                    'OSP_Damage_Received' : 0,
                    'OSP_Deaths' : 0,
                    'OSP_Eff' : 0,
                    'OSP_Gibs' : 0,
                    'OSP_Kills' : 0,
                    'OSP_Score' : 0,
                    'OSP_Suicides' : 0,
                    'OSP_TK' : 0,
                    'OSP_Team' : "",
                    'OSP_Team_Damage' : 0,
                    'Suicides' : 0,
                    'TK' : 0,
                    'TKd' : 0,
                    'game_result' : "",
                    'map' : "Unknown",
                    'match_date' : "",
                    'osp_guid' : " ",
                    'player_strip' : " ",
                    'round_guid' : " ",
                    'round_num' : 0,
                    'round_order' : 0,
                    'round_win' : 0,
                    'side' : " ",
                    'team_name' : " "
                    }
            df.fillna(value=default_values, inplace=True)
            df.astype(colum_types, inplace = True)
        return df
    
    def write_results(self, array):
        """Class2 method docstrings go here."""
        
        if not os.path.exists(self.filepath):
                    os.mkdir(self.filepath)
                    
        for dataset in array:
            if dataset in ["logs", "stats", "matches"]:
                tmp = array[dataset]
                rounds = tmp['round_guid'].unique()
                
                if not os.path.exists(self.filepath + "\\" + dataset):
                    os.mkdir(self.filepath + "\\" + dataset)
                for r in rounds:
                    pd.options.mode.use_inf_as_na = True
                    df = tmp[tmp["round_guid"]==r]
                    df = self.correct_castings(df, dataset)
                    file_name = self.filepath + "\\" + dataset + "\\" + r + ".gz"
                    #print(f"Will write {num_lines} to file {file_name}")
                    df.to_parquet(file_name, compression='gzip')
    
                    
athena_stats_fields = """
'AdjScore' int
'All_Deaths' int
'Deaths' int
'Killer' string
'Kills' int
'OSP_Damage_Given' int
'OSP_Damage_Received' int
'OSP_Deaths' int
'OSP_Eff' int
'OSP_Gibs' int
'OSP_Kills' int
'OSP_Player' string
'OSP_Score' int
'OSP_Suicides' int
'OSP_TK' int
'OSP_Team' string
'OSP_Team_Damage' int
'Suicides' int
'TK' int
'TKd' int
'game_result' string
'map' string
'match_date' string
'osp_guid' string
'player_strip' string
'round_guid' string
'round_num' int
'round_order' int
'round_win' int
'side' string
'team_name' string
"""