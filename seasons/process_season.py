import os
import sys
import traceback
import pandas as pd

from rtcwlog.io.statswriter import StatsWriter
from rtcwlog.clientlog import ClientLogProcessor
from rtcwlog.report.htmlreports import HTMLReport
from rtcwlog.textsci.aliases import decypher_name
from seasons.renames_archive import renames
import csv

#set relative path
RTCWPY_PATH = os.getcwd()
RTCWPY_PATH = RTCWPY_PATH.replace("\\seasons","")
if not RTCWPY_PATH in sys.path:
    sys.path.append(RTCWPY_PATH)

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

def duplicate_round_guids(new_df_guids, existing_round_guids):
    duplicate_rounds = []
    for guid in new_df_guids: #for each guid in incoming df
        if guid in existing_round_guids:
            duplicate_rounds.append(guid)
            print(f"[!] Found {guid} as duplicate")
    return duplicate_rounds


#settings
season_dir = "..\\data\\seasons_data\\" #.. is back one folder. 
#tis_season = "eu\\gsix"
tis_season = "2020Nov"
keep_only_pattern = ""
all_seasons="all"
write_daily_stats = False
write_parquet = True


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
    processor = ClientLogProcessor(local_file = file, debug = True)
    result = processor.process_log()
    results.append(result)

#stich them up!
logs = stats = matches = players = None
for result in results:
    if result and len(result) > 0:
        if write_daily_stats:
            html_reportx = HTMLReport(result)
            html_reportx.report_to_html(season_dir + tis_season +"\\" + "reports" + "\\")
        
        if write_parquet:
            writer = StatsWriter(media="disk", rootpath=RTCWPY_PATH, subpath=r"\data\output")
            writer.write_results(result)
        
        if logs is not None and stats is not None and matches is not None:
            new_df_guids = list(result["matches"]["round_guid"].unique())
            existing_round_guids = list(matches["round_guid"].unique())
            duplicate_rounds = duplicate_round_guids(new_df_guids, existing_round_guids)
            
            logs = logs.append(result["logs"][~result["logs"]["round_guid"].isin(duplicate_rounds)],sort=True)
            stats = stats.append(result["stats"][~result["stats"]["round_guid"].isin(duplicate_rounds)],sort=True)
            matches = matches.append(result["matches"][~result["matches"]["round_guid"].isin(duplicate_rounds)],sort=True)
            players = players.append(result["players"][~result["players"]["osp_guid"].isin(duplicate_rounds)],sort=True)
    
        else:
            logs = result["logs"]
            stats = result["stats"]
            matches = result["matches"]
            players = result["players"]

if tis_season == "":
    print("Processing all seasons")
    tis_season = all_seasons

renames[all_seasons] = {}
for season in renames:
   renames[all_seasons].update(renames[season]) 

valid_names = list(set(renames["all"].values()))

saved_guids = pd.read_pickle(r'..\seasons\guids.pkl')

if tis_season not in renames or len(renames[tis_season]) == 0:
    print("\n\n\n[!] Need some renames for this season\n\n\n")
    print("Start a new dictionary element:\n")
    print("renames[\"" + tis_season + "\"] = {\n        \"donkz\" : \"donka\"\n        }")
    

else:
    #Round up missing aliases
    missing_aliases = {}
    for alias in stats.index.unique().values:
        if alias not in renames[tis_season]:
            print(f"[!] {alias} does not have a rename entry")
            try:
                pb_alias = pb_guid = None
                pb_guid = stats[stats.index.values == alias]["pb_guid"].value_counts().index[0]
                if len(pb_guid.strip()) > 0:
                    pb_aliases = saved_guids[saved_guids["pb_guid"]==pb_guid]
                    if len(pb_aliases) > 0:
                        pb_alias = pb_aliases["Killer"].values[0]
            except:
                exc_type, exc_value, exc_traceback = sys.exc_info()
                traceback.print_exception(exc_type, exc_value, exc_traceback,limit=5, file=sys.stdout)
            
            if pb_alias:
                if len(pb_alias)>0:
                    missing_aliases[alias]= pb_alias
                    print(f"[!] {alias} was found by pb_guid and renamed to {pb_alias}")
            else:
                missing_aliases[alias]= decypher_name(alias, valid_names)
    #print("\n".join(["        \"" + name + "\" : \"" +  + "\"," for name in sorted(missing_aliases)]))
    for alias, guessed_name in missing_aliases.items():
        print("        \"" + alias + "\" : \"" + guessed_name + "\",")
            
    #Handle renames
    renamed_logs = logs.replace(renames[tis_season], regex=False)
    renamed_stats = stats.replace(renames[tis_season], regex=False)
    renamed_players = players.replace(renames[tis_season], regex=False)
    renamed_stats.index = stats.reset_index().replace(renames[tis_season], regex=False)["index"].values

    #Write HTML!
    bigresult = {"logs":renamed_logs, "stats":renamed_stats, "matches":matches, "players" : renamed_players}
    #html_report1 = HTMLReport(bigresult, amendments={"Win%":3}) #qcon
    #html_report1 = HTMLReport(bigresult, amendments={'Panzer' : 0, 'Smoker' : 0, 'Sniper' : 0, 'Tapout' : 0})
    html_report1 = HTMLReport(bigresult, minimum_rounds=16)
    #debug ranks html_report1.award_stats["awards"].filter(regex='_rank')
    html_report1.report_to_html(season_dir + tis_season + "\\" + "season-")
    
if (False):
    renames_export = {}
    for season in renames:
       renames_export.update(renames[season])
    
    renames_export_df = pd.DataFrame.from_dict(renames_export, orient='index').reset_index()
    renames_export_df["rounds_played"]=-1 # TODO
    renames_export_df.columns = ["killer","real_name","rounds_played"]
    renames_export_df.to_csv("..\\data\\output\\aliases\\Renames_2020-Jan-Oct.csv", index=False, quoting=csv.QUOTE_NONE, sep="\t")
    
#duplication check
matches = bigresult["matches"]
print("\n Duplicates check\n")
print(matches["round_guid"].value_counts().sort_values(ascending=False)[0:10])
dups = matches["round_guid"].value_counts().sort_values(ascending=False)
dups = dups[dups > 1]
if len(dups) > 1:
    print("\n\n[!] Found duplicates\n")
    pd.set_option("display.max_columns",20)
    pd.set_option("display.max_colwidth",30)
    pd.set_option("display.width",300)
    print(matches[matches["round_guid"].isin(dups.index)][['file_date', 'file_size', 'map', 'match_date', 'round_num', 'round_order', 'round_time']])
    print(matches[matches["round_guid"].isin(dups.index)]["file_date"].unique())
    
    print("\n\n[!] Deduplicating\n")
    #bigresult["matches"].drop_duplicates(["round_guid"], keep="first", inplace=True)
    #bigresult["logs"].drop_duplicates(["round_guid", "line_order"], keep="first", inplace=True)
    #bigresult["stats"].drop_duplicates(["round_guid", "Killer"], keep="first", inplace=True)

#attach elos
# 1. run season stats for all games
# 2. capture elos
if False:
    from seasons.elo import process_games
    bigresult2020 = {}
    try:
        bigresult2020["stats"] = pd.read_parquet("..\\data\\output\\stats_all.gz")
        bigresult2020["logs"] = pd.read_parquet("..\\data\\output\\logs_all.gz")
        bigresult2020["matches"] = pd.read_parquet("..\\data\\output\\matches_all.gz") 
    except:
        print("Did not load bigresult2020 from archive")
        bigresult2020 = bigresult.copy()

    bigresult2020["stats"].index = bigresult2020["stats"]["Killer"]
    bigresult2020["stats"].index.name = "index"
    
    bigresult2020["stats"] = bigresult2020["stats"].append(bigresult["stats"])
    bigresult2020["logs"] = bigresult2020["logs"].append(bigresult["logs"])
    bigresult2020["matches"] = bigresult2020["matches"].append(bigresult["matches"])
    bigresult2020["players"] = bigresult["players"] # TODO !!!!

    
    bigresult2020["logs"].reset_index(inplace=True, drop=True)
    bigresult2020["matches"].reset_index(inplace=True, drop=True)
    bigresult2020["players"] = bigresult["players"].astype(str)
    
    elos = process_games(bigresult2020["stats"])
    elos.index = elos["player"]
    elos.drop(["player"],inplace=True, axis=1)
    elos["elo"] = elos["elo"].astype(int).fillna(100)
    elos["elo_rank"] = elos["elo"].rank(method="min", ascending=False, na_option='bottom').fillna(999).astype(int)
        
    
    #Here you need to process current season and then run the rest of the lines
    
    html_report2 = HTMLReport(bigresult, elos.fillna(0))
    html_report2.report_to_html(season_dir + tis_season + "\\" + "season-")    

if False:
    writer = StatsWriter(media="disk", rootpath=RTCWPY_PATH, subpath=r"\data\output")
    writer.write_result_whole(bigresult2020)
    
if False:
    html_report3 = HTMLReport(bigresult2020, elos)
    html_report3.report_to_html(season_dir + tis_season + "\\" + "season-")  
