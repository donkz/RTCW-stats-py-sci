#from functions.helpers.hello import hellosir

import pandas as pd
#import numpy as np

##project libraries

from processfile import FileProcessor
from constants.logtext import Const
#from textsci.aliases import decypher_name
#import tests.singlefunctions
from textsci.teams import add_team_name

pd.set_option("display.max_rows",40)
pd.set_option("display.max_columns",20)
pd.set_option("display.width",300)


#print("created: %s" % datetime.fromtimestamp(os.path.getmtime(filename)).strftime('%Y-%m-%d'))
#print("created: %s" % os.path.getsize(filename))

#debug_file = r"C:\Users\stavos\Desktop\python scripts\rtcwlogpy\testfile.txt"
debug_file = r".\test_samples\testfile.txt"
#read_file = r"C:\Users\stavos\Desktop\python scripts\rtcwconsole - r2.log"
read_file = r".\test_samples\rtcwconsole - r2.log"

processor = FileProcessor(read_file, debug_file)
results = processor.process_log()

logdf = results["logdf"]
ospdf = results["ospdf"]
matchesdf = results["matchesdf"]



cols = ["player_strip", "team_name", "kill","Deaths2","Suicide","TK","TKd"] + Const.osp_columns[1:]
#print(stats_all[cols].fillna("0"))







     
        



            
