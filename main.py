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

debug_file = r"C:\Users\stavos\Desktop\python scripts\rtcwlogpy\testfile.txt"
read_file = r"C:\Users\stavos\Desktop\python scripts\rtcwconsole - r2.log"

processor = FileProcessor(read_file, debug_file)
results = processor.process_log()

logdf = results["logdf"]
ospdf = results["ospdf"]
matchesdf = results["matchesdf"]

kills = logdf[logdf["event"].isin([Const.EVENT_TEAMKILL,Const.EVENT_SUICIDE,Const.EVENT_KILL])].groupby(["killer","event"])["event"].count().unstack()
deaths = logdf[logdf["event"].isin([Const.EVENT_TEAMKILL,Const.EVENT_SUICIDE,Const.EVENT_KILL])].groupby(["victim","event"])["event"].count().unstack()

stats  = pd.DataFrame(kills[Const.EVENT_KILL])
stats["TK"]  = kills[Const.EVENT_TEAMKILL]
stats["Deaths"]= deaths[Const.EVENT_KILL]
stats["TKd"]= deaths[Const.EVENT_TEAMKILL]
stats["Suicide"]= deaths[Const.EVENT_SUICIDE]
stats["Deaths2"]= stats["Deaths"] + stats[Const.EVENT_SUICIDE]
stats = stats.drop(index='') #empty players
stats = stats.fillna(0)
pd.options.display.float_format = '{:0,.0f}'.format
ospdf.index = ospdf["player"]
stats_all = stats.join(ospdf) #Totals fall out naturally
stats_all = add_team_name(stats_all)

cols = ["player_strip", "team_name", "kill","Deaths2","Suicide","TK","TKd"] + Const.osp_columns[1:]
print(stats_all[cols].fillna("0"))







     
        



            
