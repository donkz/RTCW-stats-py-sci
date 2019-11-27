import os

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
                    df = tmp[tmp["round_guid"]==r]
                    #num_lines = len(df)
                    file_name = self.filepath + "\\" + dataset + "\\" + r + ".gzip"
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