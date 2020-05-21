import os
import sys
import pandas as pd

from statswriter import StatsWriter
from processfile import FileProcessor
from utils.htmlreports import HTMLReport
from textsci.aliases import decypher_name
import csv

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

#settings
season_dir = ".\\seasons\\"
tis_season = "2020May"
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
        "eXe|Anialatem" :  "mean",
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
        "eXe|Anialatem" :  "mean",
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
        "Uber Brian" : "kotip",
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
        "eXe|Anialatem" : "mean",
        "eXe|Flogzero" : "flogzero",
        "eXe|MeaN" : "mean",
        "eXe|Meanguine" : "mean",
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
        "v57-sOn4R*" : "sonar",
        ">> Risk!" : "risk",
        "BRND" : "brandon",
        "BoN, Dtto" : "ditto",
        "FisterMiagi" : "deadeye",
        "Flogzero" : "flogzero",
        "Joep" : "joep",
        "LuNa" : "luna",
        "MEAN" : "mean",
        "Raiser clark" : "raiser",
        "TommyTomorrow" : "tragic",
        "boydarilla" : "boydarilla",
        "c@k kent" : "cakel",
        "caff stark" : "caffeine",
        "festus" : "festus",
        "vodka!" : "vodka",
        "tTt-spaztik" : "spaztik",
        "Boydarilla" : "boydarilla",
        "DHS LUNA" : "luna",
        "brujah" : "bru",
        "caff eating" : "caffeine",
        "flogzero" : "flogzero",
        "jaytee***" : "jaytee",
        "kick gut" : "gut",
        "nigel**" : "nigel",
        "raiser" : "raiser",
        "woodChop" : "woodchop"
        }

renames["2020Apr"] = {
        ".:.prowler" : "prowler",
        "Cliffdark" : "cliffdark",
        "DillWeed" : "dillweed",
        "Jimmy" : "pasek",
        "Kittens" : "kittens",
        "NABRND" : "brandon",
        "SOURCE" : "source",
        "bru" : "bru",
        "eXe|Boo7y" : "booty",
        "eXe|Flogzero" : "flogzero",
        "eXe|MeaN" : "mean",
        "eXe|eternal" : "eternal",
        "miles" : "miles",
        "murkey" : "murkey",
        "not13KDAMAGE" : "raiser",
        "parcher" : "parcher",
        "risk" : "risk",
        "spaztik" : "spaztik",
        "tragiC" : "tragic",
        "-playa-" : "playa",
        "Gutzwrzynski" : "gut",
        "Lunatic ????" : "luna",
        "Oops" : "oops",
        "Ra!sa" : "raiser",
        "caff ********" : "caffeine",
        "eXe|donka" : "donka",
        "eXe|prowler" : "prowler",
        "eternal" : "eternal",
        "kotip" : "kotip",
        "paper" : "paper",
        "rozmurk3y" : "murkey",
        "shrek" : "shrek",
        "#REDUE John_Mullins" : "john_mullins",
        "*** Cliffdark" : "cliffdark",
        "*** DozA" : "doza",
        "*** chinamann" : "chinamann",
        "*** sOnAR. <o/" : "sonar",
        "*** schwien" : "schwien",
        "-eh-brian" : "brian",
        ".:.spaztik" : "spaztik",
        "@blackmagik" : "blackmagik",
        "BRND" : "brandon",
        "Boydarilla" : "boydarilla",
        "Cock-El" : "parcher",
        "Cypher" : "cypher",
        "DHS Fistermiagi" : "deadeye",
        "DHS jaytee" : "jaytee",
        "FisterMiagi" : "deadeye",
        "Joep" : "joep",
        "Paint:>" : "paint",
        "RAZERRA!SER" : "raiser",
        "Ra!ser" : "raiser",
        "SCRILL4" : "scrilla",
        "SpuddyBuddy" : "spuddy",
        "TK|POW" : "tkpow",
        "Wang of Pain" : "wang",
        "[>>] Cliffdark" : "cliffdark",
        "aristotle" : "aristotle",
        "blackmagiknc." : "blackmagik",
        "c@k-3l" : "cakel",
        "c@k-el" : "cakel",
        "c@k-el*" : "cakel",
        "d13 caff" : "caffeine",
        "donka" : "donka",
        "donkz" : "donka",
        "eXe|Prowler" : "prowler",
        "festus" : "festus",
        "festusmoelesac" : "festus",
        "flogzero" : "flogzero",
        "gutzzzz" : "gut",
        "jaytee**************" : "jaytee",
        "mooshu" : "mooshu",
        "naper" : "naper",
        "nigel" : "nigel",
        "nigel ***" : "nigel",
        "nigel**" : "nigel",
        "playa" : "playa",
        "proWler" : "prowler",
        "prowler" : "prowler",
        "reker" : "reker",
        "spuddy" : "spuddy",
        "traggart" : "tragic",
        "trag|c" : "tragic",
        "notvis" : "vis",
        "vodka!" : "vodka",
        "-Tv-Ra!ser" : "raiser",
        "c@kztik" : "cakel",
        "-Tv-Conscious*" : "conscious",
        "corpse" : "corpse",
        "blackmagik" : "blackmagik",
        ".=[AoH]BlAZ" : "blaz",
        "jaytee*****" : "jaytee",
        "Ra!ser*" : "raiser",
        "c@k-el***" : "cakel",
        "Flogzero" : "flogzero",
        "OLIOKATH" : "oliokath",
        "RekeR" : "reker",
        "Festusmoesac" : "festus",
        "Cliffdark***" : "cliffdark",
        "mooshu*" : "mooshu",
        "nigel***" : "nigel",
        "trag|C" : "tragic",
        "MeaN" : "mean",
        "knifey" : "knifey",
        "[>>] jaytee" : "jaytee",
        "C0RPSE" : "corpse",
        "CAFF D13" : "caffeine",
        "not blackvis" : "vis",
        "oIiokath" : "oliokath",
        "rekernator" : "reker",
        "woodChop" : "woodchop",
        "Ra!ser ???" : "raiser",
        "brian" : "brian",
        "Ex-)Festus" : "festus",
        "VENOM" : "venom",
        "Euclid" : "euclid",
        "mooshu sux" : "mooshu",
        "eXe|Ra!se" : "raiser",
        "SPEC nigel" : "nigel",
        "fistermiagi" : "deadeye",
        "gut" : "gut",
        "raiser" : "raiser",
        "Tier B Ra!ser" : "raiser",
        "Tier C Jimmy" : "pasek",
        "Tier C c@k" : "cakel",
        "Tier C miles" : "miles",
        "valor-conscious*" : "conscious",
        "Tier C Fistermiagi" : "deadeye",
        "TIER F kotip" : "kotip",
        "Fistermiagi" : "deadeye",
        "bluemagik" : "blackmagik",
        "jaytee'" : "jaytee",
        "gutz0rz" : "gut",
        "Misha X" : "elsa",
        "Conscious*" : "conscious",
        "TIER C SPAZTIK" : "spaztik",
        "nigel." : "nigel",
        "f0nz3*" : "fonze",
        "HyperNegatiVemaN" : "HyperNegatiVemaN",
        "troll fans" : "reflex",
        "// Jimmy" : "pasek",
        "c@kzero" : "cakel",
        "fonze*" : "fonze",
        "c@k" : "cakel"
        }
renames["2020May"] = {
        "@corpse," : "corpse",
        "@jaytee" : "jaytee",
        "Jimmy" : "pasek",
        "MeaN" : "mean",
        "Ra!ser..." : "raiser",
        "beast" : "beast",
        "bru" : "bru",
        "eXe|Flogzero" : "flogzero",
        "fromiam" : "fro",
        "murkey" : "murkey",
        "nigel" : "nigel",
        "prowler" : "prowler",
        "Conscious*" : "conscious",
        "fonze" : "fonze",
        "FisterMiagi" : "deadeye",
        "Kittens" : "kittens",
        "blackmagik" : "blackmagik",
        "c@k-el" : "cakel",
        "donka" : "donka",
        "miles" : "miles",
        "oIiokath" : "oliokath",
        "Dr3sserWo0d!" : "dresserwood",
        "#REDUE John_Mullins" : "john_mullins",
        "DozA" : "doza",
        "festus" : "festus",
        "kindergarden c@k" : "cakel",
        "spaztik" : "spaztik",
        "vodka!" : "vodka",
        "*** Cliffdark" : "cliffdark",
        "Dress3rWo0d!" : "dresserwood",
        "fonze*" : "fonze",
        "blackmagiknc." : "blackmagik",
        "*Conscious'gA" : "conscious",
        "paper" : "paper",
        "eXe|MeaN" : "mean",
        "*Conscious'" : "conscious",
        "Jimmy Bones" : "pasek",
        "corpse" : "corpse",
        "valor-conscious*" : "conscious",
        "pixi" : "pixi",
        "Ra!ser" : "raiser",
        "-n2p)(spaztik-" : "spaztik",
        "$upac@k" : "cakel",
        "c@ktens" : "cakel",
        "asianjaytee" : "jaytee",
        "Jimbo" : "pasek",
        "siTtIns" : "corpse",
        "conscious*" : "conscious",
        "Ra!ser -_-" : "raiser",
        "Anialatem" : "mean",
        "Flogzero" : "flogzero",
        "Pixi" : "pixi",
        "Ra!ser-D" : "raiser",
        "blackmagik)" : "blackmagik",
        "dresserwood!" : "dresserwood",
        "mooshu" : "mooshu",
        "eternal)" : "eternal",
        "spaztik*" : "spaztik",
        "trag|c*" : "tragic",
        "sscasper" : "casper",
        "eXe|Anialatem" : "mean",
        "@festus" : "festus",
        "(503th.esla)" : "elsa",
        "parcher" : "parcher",
        "prwlr-$mG" : "prowler",
        "virus047" : "virus",
        "Cypher" : "cypher",
        "eXe|Folgzero" : "flogzero",
        "eelsa" : "elsa",
        "milse" : "miles",
        "rampage !!!!" : "rampage",
        "caff 23" : "caffeine",
        "playa" : "playa",
        "eternal" : "eternal",
        "Oops" : "oops",
        "reker" : "reker",
        "DillWeed" : "dillweed",
        "MoistSurgeon" : "moistsurgeon",
        "Tittens" : "tragic",
        "Becky G" : "elsa",
        "Cliffdark" : "cliffdark",
        "MILES" : "miles",
        "paper*" : "naper",
        "tragiC" : "tragic",
        "Luna" : "luna",
        "mooshu@" : "mooshu",
        "@eternal)" : "eternal",
        "CORPSE" : "corpse",
        "jaytee" : "jaytee",
        "BRU" : "bru",
        "kotip" : "kotip",
        "prowl3r" : "prowler",
        "dresserwood" : "dresserwood",
        "blackmagik(d)" : "blackmagik",
        "purples.Jimbo" : "pasek",
        "cK aimO" : "aimology",
        "(Daria.Skyhigh)" : "elsa",
        "-d-blackmagik" : "blackmagik",
        "TE)(spaztik" : "spaztik",
        "-a-Ra!ser-)" : "raiser",
        "m|Volks" : "volks",
        "[>>] Daria Cross" : "cliffdark",
        "-a-Ra!ser" : "raiser"
        }

renames["2020MayDraft"] = {
        "8===DBRU" : "bru",
        "8===DFONZ" : "fonze",
        "8===DKittens" : "kittens",
        "8===DMLS" : "miles",
        "8==DFistermiagi" : "deadeye",
        "@blackmagik" : "blackmagik",
        "@c@k-el" : "cakel",
        "@corpse" : "corpse",
        "@eternal)" : "eternal",
        "@festus" : "festus",
        "@nigel" : "nigel",
        "8===DOIiO" : "oliokath",
        "REDUE-Cypher" : "cypher",
        "REDUE-Jimmy" : "pasek",
        "REDUE-Spaztik" : "spaztik",
        "Ra!ser" : "raiser",
        "Redue-Conscious*" : "conscious",
        "Redue-Flogzero" : "flogzero",
        "donka" : "donka",
        "murkey" : "murkey",
        "pixi" : "pixi",
        "rekernator" : "reker",
        "traggart" : "tragic",
        ":+:VirUs047`" : "virus",
        "meaN" : "mean",
        "REDUE-Prowler" : "prowler",
        "Redue-Ra!ser-D^" : "raiser",
        "8===DillWeed" : "dillweed",
        "8===Dknifey" : "knifey",
        "8===DoIiokath" : "oliokath",
        "Dimension" : "dimension",
        "MeaN" : "mean",
        "gart" : "tragic",
        "reker" : "reker",
        "virus" : "virus",
        "8==DFisterMiagi" : "deadeye",
        "beast" : "beast",
        "Redue-Cypher" : "cypher",
        "Redue-Elsa" : "elsa",
        "Redue-Jimmy" : "pasek",
        "Redue-Ra!ser" : "raiser",
        "Redue-Spaztik" : "spaztik",
        "@corpse'" : "corpse",
        "@fromiam" : "fro",
        "@jaytee" : "jaytee",
        "vodka!" : "vodka"
        }

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
        
    
    #process current season alone
    html_report2 = HTMLReport(bigresult, elos)
    html_report2.report_to_html(season_dir + tis_season + "\\" + "season-")
    
