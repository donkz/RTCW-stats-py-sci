import os
import sys
import pandas as pd

from statswriter import StatsWriter
from processfile import FileProcessor
from utils.htmlreports import HTMLReport

#set relative path
RTCWPY_PATH = os.getcwd()
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

season_dir = r".\seasons\\"
tis_season = "2020Mar"
season_path = season_dir + tis_season
stat_files = list_files(season_path)

results = []
for file in stat_files:
    processor = FileProcessor(local_file = file, debug = False)
    result = processor.process_log()

    #writer = StatsWriter(media="disk", rootpath=RTCWPY_PATH, subpath=r"\output")
    #writer.write_results(result)
      
    results.append(result)
    #index = str(len(results) -1)
    #print(f'Processed file: {file} into results[{index}]')

try: 
    del logs
    del stats
    del matches
except:
    "Nothing"

for result in results:
    try:
        logs
        stats
        matches
    except NameError:
        logs = result["logs"]
        stats = result["stats"]
        matches = result["matches"]
    else:
        logs = logs.append(result["logs"],sort=True)
        stats = stats.append(result["stats"],sort=True)
        matches = matches.append(result["matches"],sort=True)
#    finally:
#        print(result["stats"]["class"].value_counts())
            
#logs.to_csv(r"./test_samples/result_client_log.csv", index=False)
#stats.to_csv(r"./test_samples/result_client_log_sum_stats.csv", index=False)
#matches.to_csv(r"./test_samples/result_client_log_matches.csv", index=False)

renames = {}
renames["2020Feb"] = {
        ".:.c@k-el" :  "cakel",
        ".:.CORPSE" :  "corpse",
        ".:.festus" :  "festus",
        ".:.spaztik" :  "spaztik",
        "[>>] Cliffdark" :  "cliffdark",
        "[tTt]c@k-el" :  "cakel",
        "Aimtastic Shootej" :  "aimtastic",
        "bru" :  "bru",
        "bwat" :  "bwat",
        "caffbe bryant" :  "caffeine",
        "CubanPete" :  "cubanpete",
        "Cypher" :  "cypher",
        "Deadeye" :  "deadeye",
        "DeadEye" :  "deadeye",
        "DHS Cypher" :  "cypher",
        "DHS DeadEye" :  "deadeye",
        "DHS Fistermiagi" :  "deadeye",
        "DHS jaytee" :  "jaytee",
        "DHS REKER" :  "reker",
        "DHS TOMMYTURBO" :  "tragic",
        "DHS tRAGIC" :  "tragic",
        "DillWeed" :  "dillweed",
        "donka" :  "donka",
        "eternal_" :  "eternal",
        "eXe|Anialatem" :  "anialatem",
        "eXe|Boo7y" :  "booty",
        "eXe|Flogzero" :  "flogzero",
        "FisterMiagi" :  "deadeye",
        "garT" :  "tragic",
        "huckleb rek" :  "reker",
        "HuckleBerryTommy" :  "tragic",
        "Joep" :  "joep",
        "John_Mullins" :  "john_mullins",
        "Kittens" :  "kittens",
        "MoistSurgeon" :  "moistsurgeon",
        "N/A BRND" :  "brandon",
        "N/A CKY" :  "cky",
        "n/a donkey" :  "donkey",
        "N/A DONKZ" :  "donka",
        "n/a eternal" :  "eternal",
        "N/A Ra!ser" :  "raiser",
        "n/a ra!ser" :  "raiser",
        "n00b" :  "n00b",
        "nigel" :  "nigel",
        "parcher" :  "parcher",
        "Ra!ser" :  "raiser",
        "rastareker" :  "reker",
        "rastatommy" :  "tragic",
        "Reflex cfg <3" :  "reflex",
        "RekeR :P" :  "reker",
        "scrill4" :  "scrilla",
        "SnowRunGut" :  "gut",
        "SOURCE" :  "source",
        "spaztik" :  "spaztik",
        "tragiC" :  "tragic",
        "Trinity*c@k-el" :  "cakel",
        "Trinity*festus" :  "festus",
        "Trinity*spaztik" :  "spaztik",
        "tTt->festus" :  "festus",
        "vodka!" :  "vodka"
        }

renames["2020Jan"] = {
        "Cliffdark" :  "cliffdark",
        "Cypher" :  "cypher",
        "DillWeed" :  "dillweed",
        "FisterMiagi" :  "deadeye",
        "Kittens" :  "kittens",
        "P.I.M.P. 180" :  "pimp",
        "Ra!ser" :  "raiser",
        "SOURCE" :  "source",
        "donka" :  "donka",
        "eXe|Boo7y" :  "booty",
        "elsa" :  "elsa",
        "murkey" :  "murkey",
        "reker" :  "reker",
        "spaztik" :  "spaztik",
        "illkilla" :  "illkilla",
        "nigel" :  "nigel",
        "eXe|Anialatem" :  "anialatem",
        "John_Mullins" :  "john_mullins",
        "[>>] Cliffdark" :  "cliffdark",
        "aaa" :  "parcher",
        "fromiam" :  "fro",
        "-[x]-nigel" :  "nigel",
        "-[x]-spaztik" :  "spaztik",
        "prowler*" :  "prowler",
        "eternal_" :  "eternal",
        "-[x]-DeadEye" :  "deadeye",
        "Festus_of_Pain" :  "festus",
        "MoistSurgeon" :  "moistsurgeon",
        "TK|POW" :  "tkpow",
        "BlewTHAT" :  "raiser",
        "The Ladies Man" :  "ladiesman",
        "Marcus Mariguta" :  "gut",
        "parcher" :  "parcher",
        "eX*Festus" :  "festus",
        "SKOL|Boo7y" :  "booty",
        "Wang of Pain" :  "wang",
        ".:.c@k-el" :  "cakel",
        ".:.prowler" :  "prowler",
        ".:.spaztik" :  "spaztik",
        "eXe|Flogzero" :  "flogzero",
        ".:.Festus" :  "festus",
        "tragiC" :  "tragic",
        "Fistermiagi" :  "deadeye",
        "Hucklebericus" :  "deadeye",
        "c@k-el" :  "cakel",
        "mach1ne" :  "machine",
        "o/ spaztik" :  "spaztik",
        "corpse" :  "corpse",
        "Tittens" :  "tragic",
        ".:.festus" :  "festus",
        "cKy" :  "cky"
        }

renames["2020Mar"] = {
        "!tH!Gut" : "gut",
        "#REDUE John_Mullins" : "john_mullins",
        "-=prowler=-" : "prowler",
        "-Tv-Ra!ser" : "raiser",
        "-eh-brian" : "brian",
        "-n2p)(spaztik" : "spaztik",
        ".:.Flogzero" : "flogzero",
        ".:.c@k-el" : "cakel",
        ".:.crops" : "corpse",
        ".:.festus" : "festus",
        ".:.prowler" : "prowler",
        ".:.spaztik" : "spaztik",
        "BRND REDUE" : "brandon",
        "Cliff of Pain" : "cliffdark",
        "CoronaDill" : "dillweed",
        "Cypher" : "cypher",
        "DHS DEADEYE" : "deadeye",
        "DHS Fistermiagi" : "deadeye",
        "DHS NIGEL" : "nigel",
        "DHS jaytee" : "jaytee",
        "DHS tragiC" : "tragic",
        "DUBARD <o/" : "dubard",
        "Deadeye" : "deadeye",
        "DillWeed" : "dillweed",
        "Festus" : "festus",
        "Fister of Pain" : "deadeye",
        "HuckleBerryTragic" : "tragic",
        "Jimmy" : "jimmy",
        "John_Mullins" : "john_mullins",
        "John_Mullins_of_Pain" : "john_mullins",
        "Kittens" : "kittens",
        "MoistSurgeon" : "moistsurgeon",
        "N/A BRND" : "brandon",
        "N/A Ra!ser" : "raiser",
        "N/A donkz" : "donka",
        "Pasek" : "pasek",
        "Pasek*" : "pasek",
        "Pk of Pain" : "pasek",
        "RAISER" : "raiser",
        "Raiser" : "raiser",
        "SCRILL4" : "scrilla",
        "SOURCE" : "source",
        "Uber Brian" : "Uber Brian",
        "Wang of Pain" : "wang",
        "Yaourt ! ?" : "yaourt",
        "[>>] Cliffdark" : "cliffdark",
        "[>>] Helga von Bulow" : "cliffdark",
        "afk-ternal" : "eternal",
        "bru" : "bru",
        "c@k-el" : "cakel",
        "caffbe bryant" : "caffeine",
        "coronaBRND" : "brandon",
        "dillweed" : "dillweed",
        "donka" : "donka",
        "donkz" : "donka",
        "donkz of  Pain" : "donka",
        "donkztik" : "donka",
        "eXe|Anialatem" : "anialatem",
        "eXe|Flogzero" : "flogzero",
        "eXe|MeaN" : "anialatem",
        "eXe|Meanguine" : "anialatem",
        "eternal_" : "eternal",
        "fisterMiagi" : "deadeye",
        "fromiam" : "fro",
        "fucker" : "raiser",
        "miLes" : "miles",
        "miles" : "miles",
        "miles of Pain" : "miles",
        "mooshu" : "mooshu",
        "murkey" : "murkey",
        "n/a SOURCE" : "source",
        "n/a eternal" : "eternal",
        "n00b" : "brandon",
        "nig of Pain" : "nigel",
        "nigel" : "nigel",
        "parcher" : "parcher",
        "parhcer" : "vis",
        "prowler" : "prowler",
        "reker" : "reker",
        "rekernator" : "reker",
        "roz'murkey" : "murkey",
        "roz'parcher" : "parcher",
        "shootz" : "shootz",
        "source" : "source",
        "spaz of pain" : "spaztik",
        "spaztik" : "spaztik",
        "sscasper" : "casper",
        "tTt-c@k-el" : "cakel",
        "tTt-festus" : "festus",
        "tTt-prowler" : "prowler",
        "teker" : "tragic",
        "v57-sOn4R*" : "sonar"   
        }

if len(renames[tis_season]) == 0:
    print("\n".join(["        \"" + name + "\" : \"\"," for name in sorted(stats.index.unique().values)]))
    print("Need some renames for this season")
    exit()

#Round up missing aliases
missing_aliases = []
for alias in stats.index.unique().values:
    if alias not in renames[tis_season]:
        print(f"[!] {alias} does not have a rename entry")
        missing_aliases.append(alias)
print("\n".join(["        \"" + name + "\" : \"\"," for name in sorted(missing_aliases)]))
        
#Handle renames
renamed_logs = logs.replace(renames[tis_season], regex=False)
renamed_stats = stats.replace(renames[tis_season], regex=False)
renamed_stats.index = stats.reset_index().replace(renames[tis_season], regex=False)["index"].values

#Write HTML!
bigresult = {"logs":renamed_logs, "stats":renamed_stats, "matches":matches}
html_report1 = HTMLReport(bigresult)
html_report1.report_to_html()


