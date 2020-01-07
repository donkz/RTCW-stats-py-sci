import os
import datetime
import pandas as pd

from statswriter import StatsWriter
from processfile import FileProcessor
from utils.htmlreports import HTMLReport

#set relative path
RTCWPY_PATH = os.getcwd()
import sys
if not RTCWPY_PATH in sys.path:
    sys.path.append(RTCWPY_PATH)

#expand viewing area for pandas datasets (visual inspection only)
pd.set_option("display.max_rows",2080)
pd.set_option("display.max_columns",20)
pd.set_option("display.width",300)

#file where processed lines will be written to for the last processed file
debug_file = r".\test_samples\testfile.txt"

#test files to process
stat_files = []
stat_files.append(r".\test_samples\rtcwconsole - r2.log") #1
stat_files.append(r".\test_samples\rtcwconsole-8-30-2018.log") #2
stat_files.append(r".\test_samples\rtcwconsole-20190905.log") #3
stat_files.append(r".\test_samples\rtcwconsole-09-12-2019.log") #4 #http://krisofwin.com/stats/stats/2019.Sep.13.%2015h54m23s.html
stat_files.append(r".\test_samples\rtcwconsole-2019-10-02.log") #5
stat_files.append(r".\test_samples\rtcwconsole-09-19-2019.log") #6
stat_files.append(r".\test_samples\rtcwconsole-2019-10-10.log") #7
stat_files.append(r".\test_samples\rtcwconsole-2019-10-17.log") #8
stat_files.append(r".\test_samples\rtcwconsole-2019-10-24.log") #9
stat_files.append(r".\test_samples\rtcwconsoleOct28.log") #10
stat_files.append(r".\test_samples\rtcwconsole-MNF-2019-11-05 - clean.log") #11
stat_files.append(r".\test_samples\rtcwconsole-2019-11-07.log") #12
stat_files.append(r".\test_samples\rtcwconsole-2019-11-14.log") #13
stat_files.append(r".\test_samples\rtcwconsoleNov19.log") #14
stat_files.append(r".\test_samples\rtcwconsoleNov25.log") #15
stat_files.append(r".\test_samples\rtcwconsole-2019-12-10.log") #16
stat_files.append(r".\test_samples\rtcwconsole-2019-12-05.log") #17
stat_files.append(r".\test_samples\rtcwconsole-2019-12-12.log") #18
stat_files.append(r".\test_samples\rtcwconsole-2019-12-15.log") #19
stat_files.append(r".\test_samples\rtcwconsole-2019-12-21.log") #20
stat_files.append(r".\test_samples\rtcwconsole-2019-12-19.log") #21
stat_files.append(r".\test_samples\rtcwconsole-2019-12-26.log") #22
stat_files.append(r".\test_samples\rtcwconsole-2019-01-02.log") #23
stat_files.append(r".\test_samples\rtcwconsole-2019-01-03.log") #24
stat_files.append(r".\test_samples\rtcwconsole-2019-01-05.log") #25
stat_files.append(r".\test_samples\rtcwconsole-2019-01-06MNF.log") #26

#just pick last one for debugging
stat_files = stat_files[-1:] #last
#stat_files = stat_files[22:23] #[n-1 : n-th] --- to pull n-th file


results = []
for read_file in stat_files:
    processor = FileProcessor(read_file, debug_file)
    result = processor.process_log()
    
    #writer = StatsWriter(media="disk", rootpath=RTCWPY_PATH, subpath=r"\output")
    #writer.write_results(result)
      
    results.append(result)
    index = str(len(results) -1)
    #print(result["stats"][['OSP_Player', 'player_strip', 'team_name','Killer']].drop_duplicates())
    print(f'Processed file: {read_file} into results[{index}]')

for result in results:
    html_report = HTMLReport(result)
    try:
        date = result["matches"]["match_date"].min().split(" ")[0]
    except: 
        date = datetime.datetime.today().strftime('%Y-%m-%d')
    #html_report.report_to_html(r".\test_samples\stats-" + date + ".html")
    html_report.report_to_html()



if(2==1): #manual execution
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
            logs = logs.append(result["logs"])
            stats = stats.append(result["stats"])
            matches = matches.append(result["matches"])
        finally:
            print(result["stats"]["class"].value_counts())
            
    logs.to_csv(r"./test_samples/result_client_log.csv", index=False)
    stats.to_csv(r"./test_samples/result_client_log_sum_stats.csv", index=False)
    matches.to_csv(r"./test_samples/result_client_log_matches.csv", index=False)
    
    bigresult = {"logs":logs, "stats":stats, "matches":matches}
    html_report1 = HTMLReport(bigresult)
    html_report1.report_to_html()




'''
r".\test_samples\rtcwconsole-2019-11-07.log"

Proccessed round 1  winner Allies on Ice        . Events: 284   . Players: 16
Proccessed round 2  winner Axis   on Ice        . Events: 206   . Players: 16
Proccessed round 3  winner Allies on Base       . Events: 83    . Players: 16
Proccessed round 4  winner Axis   on Base       . Events: 82    . Players: 16
WARNING: Multiple objectives related to maps: Counter({'te_frostbite': 8, 'mp_beach': 1})
Proccessed round 5  winner Allies on Frostbite  . Events: 54    . Players: 16
WARNING: Multiple objectives related to maps: Counter({'te_frostbite': 2, 'mp_beach': 1})
Proccessed round 6  winner Allies on Frostbite  . Events: 38    . Players: 16
Proccessed round 7  winner Allies on Village    . Events: 143   . Players: 16
Proccessed round 8  winner Axis   on Village    . Events: 145   . Players: 16
Proccessed round 9  winner Axis   on Beach      . Events: 185   . Players: 16
Proccessed round 10 winner Allies on Beach      . Events: 120   . Players: 16
Proccessed round 11 winner Allies on Chateau    . Events: 95    . Players: 14
Proccessed round 12 winner Axis   on Chateau    . Events: 96    . Players: 14
Proccessed round 13 winner Axis   on Ice        . Events: 130   . Players: 11
Proccessed round 14 winner Axis   on Ice        . Events: 86    . Players: 11
Proccessed round 15 winner Allies on Ice        . Events: 162   . Players: 10
Proccessed round 16 winner Axis   on Ice        . Events: 54    . Players: 10
'''

      
#logdf["count"] = logdf.groupby((logdf['killer'] != logdf['killer'].shift(1)).cumsum()).cumcount()+1
#logdf[(logdf["event"] == "kill") & (logdf["count"] > 4)]