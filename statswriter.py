import os, sys
import pandas as pd
from constants.logtext import Const

class StatsWriter:
    """Class docstrings go here."""

    def __init__(self, media, rootpath, subpath):
        """Class method docstrings go here."""
        self.filepath = None
        self.connection = None
        
        #weapon columns (mod = mean of death)
        self.weapon_cols = {}
        self.weapon_default_values = {}
        for mod_type in Const.mod_by_type.keys():
            for mod in Const.mod_by_type[mod_type]:
                self.weapon_cols[mod] = 'int'
                self.weapon_default_values[mod] = 0
        
        self.stats_column_types = {
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
                    'class' : 'str',
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
                    'team_name' : 'str',
                    "round_time" : 'int',
                    "round_diff" : 'int'
                   }
        
        self.stats_column_types.update(self.weapon_cols)
            
        self.stats_default_values = {
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
                    'team_name' : " ",
                    "round_time" : 600,
                    "round_diff" : 0
                    }
        self.stats_default_values.update(self.weapon_default_values)
            
        
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
    
    def correct_castings(self, df, df_name):
        if df_name == "stats":
            extra_cols_in_stats   = [value for value in df.columns if value not in self.stats_column_types.keys()]
            extra_cols_in_casting = [value for value in self.stats_column_types.keys() if value not in df.columns]
            
            if len(extra_cols_in_stats) > 0 :
                print("[!] Warning: there are more columns in new stat files than casting knows about. \n[!] Add new columns to casting variables in statswriter.py:correct_castings()")
                print(extra_cols_in_stats)
            
            if len(extra_cols_in_casting) > 0 :
                print("[!] Warning: there are extra columns in casting variable. Clean them up")
                print(extra_cols_in_casting)
            
            #do the casting and nan filling    
            df = df.fillna(value=self.stats_default_values)
            df = df.astype(self.stats_column_types)
        return df
    
    def write_results(self, array):
        """Class2 method docstrings go here."""
        
        if not os.path.exists(self.filepath):
            try:
                os.mkdir(self.filepath)
            except:
                print("Could not create a directory to write stats out: " + self.filepath)
                    
        for dataset in array:
            if dataset in ["logs", "stats", "matches"]:
                tmp = array[dataset]
                rounds = tmp['round_guid'].unique()
                
                if not os.path.exists(self.filepath + "\\" + dataset):
                    os.mkdir(self.filepath + "\\" + dataset)
                for r in rounds:
                    pd.options.mode.use_inf_as_na = True
                    df = tmp[tmp["round_guid"]==r]
                    try:
                        df = self.correct_castings(df, dataset)
                    except:
                        print("[!] Could hard cast the data for round " + r)
                        print(sys.exc_info()[1])
                    file_name = self.filepath + "\\" + dataset + "\\" + r + ".gz"
                    #print(f"Will write {num_lines} to file {file_name}")
                    df.to_parquet(file_name, compression='gzip', index=False)
    
    #not tested for order
    def make_aws_athena_table(self):
        schema = ""
        for col in self.stats_column_types.keys():
            row = "'" + col + "' " + self.stats_column_types[col] + "\n"
            schema += row
        print(schema)