import pandas as pd

from processfile import FileProcessor
from textsci.awards import Awards 

RTCWPY_PATH = pwd
import sys
if not RTCWPY_PATH in sys.path:
    sys.path.append(RTCWPY_PATH)

pd.set_option("display.max_rows",40)
pd.set_option("display.max_columns",20)
pd.set_option("display.width",300)

debug_file = r".\test_samples\testfile.txt"
read_file = r".\test_samples\rtcwconsole - r2.log"
#read_file = r".\test_samples\rtcwconsole-8-30-2018.log"
#read_file = r".\test_samples\rtcwconsole-20190905.log"
#read_file = r".\test_samples\rtcwconsole-09-12-2019.log" #http://krisofwin.com/stats/stats/2019.Sep.13.%2015h54m23s.html


processor = FileProcessor(read_file, debug_file)
results = processor.process_log()

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
award_stats = awards.collect_awards(results)
weapon_stats = awards.award_weapon_counts(results)
kill_matrix_stats = awards.awards_kill_matrix(results)
basic_stats = awards.all_stats_matrix(results)



#matchesdf[["round_order","round_num","round_time","winner"]]

# =============================================================================
# event_lines_dataframe = logdf
# print(Awards.award_pack_of_five(event_lines_dataframe))
# print(Awards.award_death_streak(event_lines_dataframe))
# print(Awards.award_kill_streak(event_lines_dataframe))
# print(Awards.award_most_blown_up(event_lines_dataframe))
# print(Awards.award_most_panzed(event_lines_dataframe))
# print(Awards.award_first_in_door(event_lines_dataframe))
# print(Awards.award_efficiency_of_the_night(event_lines_dataframe))
# print(Awards.award_kills_of_the_night(event_lines_dataframe))
# 
# sum_lines_dataframe = statsdf
# print(Awards.award_most_useful_points(sum_lines_dataframe))
# print(Awards.award_most_holds(sum_lines_dataframe))
# print(Awards.award_most_caps(sum_lines_dataframe))
# =============================================================================

#Sanity check 1
statsdf.groupby(["round_num","round_win","game_result"])[["game_result"]].nunique()

     
        



            
