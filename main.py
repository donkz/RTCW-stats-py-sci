#from functions.helpers.hello import hellosir

import pandas as pd
#import numpy as np

##project libraries

from processfile import FileProcessor
from constants.logtext import Const
#from textsci.aliases import decypher_name
#import tests.singlefunctions



pd.set_option("display.max_rows",40)
pd.set_option("display.max_columns",20)
pd.set_option("display.width",300)


#print("created: %s" % datetime.fromtimestamp(os.path.getmtime(filename)).strftime('%Y-%m-%d'))
#print("created: %s" % os.path.getsize(filename))

#debug_file = r"C:\Users\stavos\Desktop\python scripts\rtcwlogpy\testfile.txt"
debug_file = r".\test_samples\testfile.txt"
#read_file = r".\test_samples\rtcwconsole - r2.log"
read_file = r".\test_samples\rtcwconsole-8-30-2018.log"


processor = FileProcessor(read_file, debug_file)
results = processor.process_log()

logdf = results["logdf"]
statsdf= results["stats"]
matchesdf = results["matchesdf"]


#columns without guid
cols = ["round_num","player_strip", "team_name", "kill","Deaths2","Suicide","TK","TKd"] + Const.osp_columns[1:]
#print(statsdf[cols].fillna("0"))

#results_dir = ".\test_samples\\"
log_date = matchesdf["log_date"][0] 
if(log_date == ""):
    log_date = matchesdf["file_date"]
#logdf.to_csv(results_dir + log_date + ".csv")
logdf.to_csv(r"C:\Users\stavos\Desktop\test2.csv", index=False)
statsdf.to_csv(r"C:\Users\stavos\Desktop\stats2.csv", index=False)
matchesdf.to_csv(r"C:\Users\stavos\Desktop\matches2.csv", index=False)

matchesdf[["round_order","round_num","round_time","winner"]]







     
        



            
