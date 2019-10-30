import os
import pandas as pd

from processfile import FileProcessor
from textsci.awards import Awards 
from textsci.matchstats import MatchStats


RTCWPY_PATH = os.getcwd()
import sys
if not RTCWPY_PATH in sys.path:
    sys.path.append(RTCWPY_PATH)

pd.set_option("display.max_rows",40)
pd.set_option("display.max_columns",20)
pd.set_option("display.width",300)

debug_file = r".\test_samples\testfile.txt"
#read_file = r".\test_samples\rtcwconsole - r2.log"
#read_file = r".\test_samples\rtcwconsole-8-30-2018.log"
#read_file = r".\test_samples\rtcwconsole-20190905.log"
#read_file = r".\test_samples\rtcwconsole-09-12-2019.log" #http://krisofwin.com/stats/stats/2019.Sep.13.%2015h54m23s.html
#read_file = r".\test_samples\rtcwconsole-2019-10-02.log"
#read_file = r".\test_samples\rtcwconsole-09-19-2019.log"
#read_file = r".\test_samples\rtcwconsole-2019-10-10.log"
#read_file = r".\test_samples\rtcwconsole-2019-10-17.log"
#read_file = r".\test_samples\rtcwconsole-2019-10-24.log"
read_file = r".\test_samples\rtcwconsoleOct28.log"

processor = FileProcessor(read_file, debug_file)
results = processor.process_log()

if results is not None:
    logdf = results["logdf"]
    statsdf= results["stats"]
    matchesdf = results["matchesdf"]


log_date = matchesdf["log_date"][0] 
if(log_date == ""):
    log_date = matchesdf["file_date"]

logdf.to_csv(r"./test_samples/result_client_log.csv", index=False)
statsdf.to_csv(r"./test_samples/result_client_log_sum_stats.csv", index=False)
matchesdf.to_csv(r"./test_samples/result_client_log_matches.csv", index=False)

awards = Awards()
matchstats = MatchStats()
award_stats = awards.collect_awards(results)
weapon_stats = matchstats.table_weapon_counts(results)
kill_matrix_stats = matchstats.table_kill_matrix(results)
basic_stats = matchstats.table_base_stats(results)
table_match_results = matchstats.table_match_results(results)
match_info_datetime = matchstats.match_info_datetime(results)
table_map_list = matchstats.table_map_list(results)



#Sanity check 1
statsdf.groupby(["round_num","round_win","game_result"])[["game_result"]].nunique()




            
