import os, sys
import pandas as pd
from rtcwlog.constants.logtext import Const

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
                    'Accuracy'  : 'float', 
                    'Headshots' : 'int', 
                    'Revives' : 'int',
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
                    'round_time' : 'int',
                    'round_diff' : 'int',
                    'pb_guid' : 'str'
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
                    'OSP_Team' : '',
                    'OSP_Team_Damage' : 0,
                    'Suicides' : 0,
                    'Accuracy'  : 0.0, 
                    'Headshots' : 0, 
                    'Revives' : 0,
                    'TK' : 0,
                    'TKd' : 0,
                    'game_result' : '',
                    'map' : 'Unknown',
                    'match_date' : '',
                    'osp_guid' : ' ',
                    'player_strip' : ' ',
                    'round_guid' : ' ',
                    'round_num' : 0,
                    'round_order' : 0,
                    'round_win' : 0,
                    'side' : ' ',
                    'team_name' : ' ',
                    'round_time' : 600,
                    'round_diff' : 0,
                    'pb_guid' : ' '
                    }
        self.stats_default_values.update(self.weapon_default_values)
        
        self.matches_column_types = {
                'file_date': 'str',
                'match_date': 'str',
                'file_size': 'int',
                'round_guid': 'str',
                'osp_guid': 'str',
                'round_order': 'int',
                'round_num':'int',
                'players': 'str',
                'defense_hold':'int',
                'winner': 'str',
                'round_time':'int',
                'round_diff':'int',
                'map': 'str',
                'file_name' :'str'
                }
        self.matches_default_values = {
                'file_date': '1999-07-31',
                'match_date': '1999-07-31',
                'file_size': 1,
                'round_guid': 'defaulted',
                'osp_guid': 'defaulted',
                'round_order': 1,
                'round_num':1,
                'players': "[['defaultaxis', 'Axis', 'Offense'],['defaultallies', 'Allies', 'Defense']]",
                'defense_hold':0,
                'winner': 'Allies',
                'round_time':600,
                'round_diff':0,
                'map': 'Ice',
                'file_name' :'str'
                }
            
        
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
                print("[!] There are more columns in new stats dataframe than casting knows about. \n[!] Add new columns to casting variables in statswriter.py:correct_castings()")
                print(extra_cols_in_stats)
            
            if len(extra_cols_in_casting) > 0 :
                print("[!] There are extra columns in casting variable. Clean them up")
                print(extra_cols_in_casting)
            
            #do the casting and nan filling    
            df = df.fillna(value=self.stats_default_values)
            df = df.astype(self.stats_column_types)
        
        if df_name == "matches":
            extra_cols_in_macthes   = [value for value in df.columns if value not in self.matches_column_types.keys()]
            extra_cols_in_casting = [value for value in self.matches_column_types.keys() if value not in df.columns]
            
            if len(extra_cols_in_macthes) > 0 :
                print("[!] There are more columns in new matches than casting knows about. \n[!] Add new columns to casting variables in statswriter.py:correct_castings()")
                print(extra_cols_in_macthes)
            
            if len(extra_cols_in_casting) > 0 :
                print("[!] There are extra columns in casting variable. Clean them up")
                print(extra_cols_in_casting)
            
            #do the casting and nan filling    
            df = df.fillna(value=self.matches_default_values)
            df = df.astype(self.matches_column_types)
            
        return df
    
    def write_results(self, result):
        r"""
        Write a result to parquet split into rounds
        
        Parameters
        ----------
        result: dataframe containing logs, stats, and matches
        
        Returns Nothing
        """
        
        if not os.path.exists(self.filepath):
            try:
                os.mkdir(self.filepath)
            except:
                print("Could not create a directory to write stats out to : " + self.filepath)
                    
        if result is None:
            return
        for dataset in result:
            if dataset in ["logs", "stats", "matches"]:
                tmp = result[dataset]
                rounds = tmp['round_guid'].unique()
                
                if not os.path.exists(self.filepath + "\\" + dataset):
                    os.mkdir(self.filepath + "\\" + dataset)
                for r in rounds:
                    pd.options.mode.use_inf_as_na = True
                    df = tmp[tmp["round_guid"]==r]
                    try:
                        df = self.correct_castings(df, dataset)
                    except:
                        print("[!] Could not hard cast the data for round " + r)
                        print(sys.exc_info()[1])
                    file_name = self.filepath + "\\" + dataset + "\\" + r + ".gz"
                    #print(f"Will write {num_lines} to file {file_name}")
                    df.to_parquet(file_name, compression='gzip', index=False)
    
    
    def write_result_whole(self, result):
        r"""
        Write a huge result to parquet as a whole
        
        Parameters
        ----------
        result: dataframe containing logs, stats, and matches
        
        Returns Nothing
        """
        
        pd.options.mode.use_inf_as_na = True 
        if not os.path.exists(self.filepath):
            try:
                os.mkdir(self.filepath)
            except:
                print("Could not create a directory to write stats out to : " + self.filepath)
                    
        for dataset in result:
            if dataset in ["logs", "stats", "matches"]:
                df = result[dataset]
                
                try:
                    df = self.correct_castings(df, dataset)
                except:
                    print("[!] Could not hard cast the data.")
                    print(sys.exc_info()[1])
                file_name = self.filepath + "\\" + dataset + "_all" + ".gz"
                num_lines = len(df)
                print(f"Will write {num_lines} to file {file_name}")
                df.to_parquet(file_name, compression='gzip', index=False)
    
    #not tested for order
    def make_aws_athena_table(self):
        schema = ""
        for col in self.stats_column_types.keys():
            row = "'" + col + "' " + self.stats_column_types[col] + "\n"
            schema += row
        print(schema)
    
    def write_player(self, result, archive, castings, defaults):
        r"""
        Write player processing results
        
        Parameters
        ----------
        result: dataframe containing players, osp matches
        
        Returns Nothing
        """
        
        pd.options.mode.use_inf_as_na = True 
        if not os.path.exists(self.filepath):
            try:
                os.mkdir(self.filepath)
            except:
                print("Could not create a directory to write stats out to : " + self.filepath)
                    
        for dataset in result:
            if dataset in ["player","osponly"]:
                df = result[dataset]
                
                if dataset in castings and dataset in defaults:                
                    try:
                        df = df.fillna(value=defaults[dataset])
                        df = df.astype(castings[dataset])
                    except:
                        print("[!] Could not hard cast the data.")
                        print(sys.exc_info()[1])
                        
                file_name = self.filepath + "\\" + dataset + "\\" + archive + ".gz"
                num_lines = len(df)
                print(f"Will write {num_lines} to file {file_name}")
                df.to_parquet(file_name, compression='gzip', index=False)