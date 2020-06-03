import os
import sys
import pandas as pd

from statswriter import StatsWriter
from processfile import FileProcessor
from utils.htmlreports import HTMLReport
from textsci.aliases import decypher_name
from seasons_code.renames_archive import renames
import csv

#set relative path
RTCWPY_PATH = os.getcwd()
if not RTCWPY_PATH in sys.path:
    sys.path.append(RTCWPY_PATH.replace("\\seasons_code",""))

def list_files(path):
    print(f"\nScanning files in {path}\n")
    
    all_files = [] # will contain elements like [filepath,date]
    for subdir, dirs, files in os.walk(path):
            for file in files:
                #print os.path.join(subdir, file)
                filepath = subdir + os.sep + file
                if filepath.endswith(".log"):
                    #print (filepath)
                    all_files.append(filepath)
    print("\n".join(all_files))
    return all_files

#settings
season_dir = "..\\seasons_data\\" #.. is back one folder. 
tis_season = "2020MayDraft"
keep_only_pattern = ""
all_seasons="all"
write_daily_stats = False
write_parquet = False


#process files
season_path = season_dir + tis_season
stat_files = list_files(season_path)

if keep_only_pattern != "":
    print("[ ] Looking only for files like " + keep_only_pattern)
    stat_files = [filename for filename in stat_files if keep_only_pattern in filename]
    print("[ ] Filtered files to:\n")
    print(stat_files)

results = []
for file in stat_files:
    processor = FileProcessor(local_file = file, debug = False)
    result = processor.process_log()
    results.append(result)

#stich them up!
logs = stats = matches = None
for result in results:
    if write_daily_stats:
        html_reportx = HTMLReport(result)
        html_reportx.report_to_html(season_dir + tis_season +"\\" + "reports" + "\\")
    
    if write_parquet:
        writer = StatsWriter(media="disk", rootpath=RTCWPY_PATH, subpath=r"\output")
        writer.write_results(result)
    
    if logs is not None and stats is not None and matches is not None:
        logs = logs.append(result["logs"],sort=True)
        stats = stats.append(result["stats"],sort=True)
        matches = matches.append(result["matches"],sort=True)
    else:
        logs = result["logs"]
        stats = result["stats"]
        matches = result["matches"]



if tis_season == "":
    print("Processing all seasons")
    tis_season = all_seasons

 
renames[all_seasons] = {}
for season in renames:
   renames[all_seasons].update(renames[season]) 

valid_names = list(set(renames["all"].values()))

if tis_season not in renames or len(renames[tis_season]) == 0:
    print("\n\n\n[!] Need some renames for this season\n\n\n")
    print("Start a new dictionary element:\n")
    print("renames[\"" + tis_season + " \"] = {\n        \"donkz\" : \"donka\"\n        }")
    

else:
    #Round up missing aliases
    missing_aliases = {}
    for alias in stats.index.unique().values:
        if alias not in renames[tis_season]:
            print(f"[!] {alias} does not have a rename entry")
            missing_aliases[alias]= decypher_name(alias, valid_names)
    #print("\n".join(["        \"" + name + "\" : \"" +  + "\"," for name in sorted(missing_aliases)]))
    for alias, guessed_name in missing_aliases.items():
        print("        \"" + alias + "\" : \"" + guessed_name + "\",")
            
    #Handle renames
    renamed_logs = logs.replace(renames[tis_season], regex=False)
    renamed_stats = stats.replace(renames[tis_season], regex=False)
    renamed_stats.index = stats.reset_index().replace(renames[tis_season], regex=False)["index"].values

    #Write HTML!
    bigresult = {"logs":renamed_logs, "stats":renamed_stats, "matches":matches}
    html_report1 = HTMLReport(bigresult)
    html_report1.report_to_html(season_dir + tis_season + "\\" + "season-")
    
if (False):
    renames_export = {}
    for season in renames:
       renames_export.update(renames[season])
    
    renames_export_df = pd.DataFrame.from_dict(renames_export, orient='index').reset_index()
    renames_export_df["rounds_played"]=-1 # TODO
    renames_export_df.columns = ["killer","real_name","rounds_played"]
    renames_export_df.to_csv("Renames_2020-Jan-May.csv", index=False, quoting=csv.QUOTE_NONE, sep="\t")
    
#duplication check
matches = bigresult["matches"]
print("\n\n\n Duplicates check\n\n\n")
print(matches["round_guid"].value_counts().sort_values(ascending=False)[0:5])
dups = matches["round_guid"].value_counts().sort_values(ascending=False)
dups = dups[dups > 1]
if len(dups) > 1:
    print("[!] Found duplicates\n\n\n")
    pd.set_option("display.max_columns",20)
    pd.set_option("display.max_colwidth",30)
    pd.set_option("display.width",300)
    print(matches[matches["round_guid"].isin(dups.index)][['file_date', 'file_size', 'map', 'match_date', 'round_num', 'round_order', 'round_time']])
    print(matches[matches["round_guid"].isin(dups.index)]["file_date"].unique())

#attach elos
# 1. run season stats for all games
# 2. capture elos
if False:
    from tests.elo import process_games
    bigresult2020 = bigresult.copy()
    elos = process_games(bigresult2020["stats"])
    elos.index = elos["player"]
    elos.drop(["player"],inplace=True, axis=1)
    elos["elo"] = elos["elo"].astype(int)
    elos["elo_rank"] = elos["elo"].rank(method="min", ascending=False, na_option='bottom').fillna(999).astype(int)
        
    
    #Here you need to process current season and then run the rest of the lines
    
    html_report2 = HTMLReport(bigresult, elos)
    html_report2.report_to_html(season_dir + tis_season + "\\" + "season-")    
    
    writer = StatsWriter(media="disk", rootpath=RTCWPY_PATH, subpath=r"\output")
    writer.write_result_whole(bigresult2020)
