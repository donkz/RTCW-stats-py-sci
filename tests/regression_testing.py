import os
import sys, traceback
import pandas as pd

from rtcwlog.io.statswriter import StatsWriter
from rtcwlog.clientlog import ClientLogProcessor
from rtcwlog.report.htmlreports import HTMLReport

#set relative path
RTCWPY_PATH = os.getcwd()
RTCWPY_PATH = RTCWPY_PATH.replace("\\tests","")
if not RTCWPY_PATH in sys.path:
    sys.path.append(RTCWPY_PATH)

#expand viewing area for pandas datasets (visual inspection only)
pd.set_option('display.max_rows', 500)
pd.set_option("display.max_columns",30)
pd.set_option("display.max_colwidth",20)
pd.set_option("display.width",300)

#stat_files.append(r"..\tests\test_samples\rtcwconsole-09-12-2019.log") #3 #http://krisofwin.com/stats/stats/2019.Sep.13.%2015h54m23s.html

print("\nScanning for test files\n")
stat_files = [] 
for subdir, dirs, files in os.walk(r"..\tests\test_samples\\"):
        for file in files:
            #print os.path.join(subdir, file)
            filepath = subdir + os.sep + file
            if filepath.endswith(".log"):
                stat_files.append(filepath)


#just pick last one for debugging
#stat_files = stat_files[25:26]
#stat_files = stat_files[-2:] #last 2
#stat_files = stat_files[-1:] 
#n=0
#stat_files = stat_files[n:n+1] #[n-1 : n-th] --- to pull n-th file


results = []
for file in stat_files:
    try:
        processor = ClientLogProcessor(local_file = file, debug = True, debug_file = "testfile.txt")
        result = processor.process_log()
    except:
        print(f"Failed to process {file} with the following error:\n\n")
        exc_type, exc_value, exc_traceback = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_traceback,
                              limit=2, file=sys.stdout)
        
    
    writer = StatsWriter(media="disk", rootpath=RTCWPY_PATH, subpath=r"\data\output")
    writer.write_results(result)
      
    results.append(result)
    index = str(len(results) -1)
    print(f'Processed file: {file} into results[{index}]')

for result in results:
    html_report = HTMLReport(result)
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
            
    logs.to_csv(r"./data/test_samples/result_client_log.csv", index=False)
    stats.to_csv(r"./data/test_samples/result_client_log_sum_stats.csv", index=False)
    matches.to_csv(r"./data/test_samples/result_client_log_matches.csv", index=False)
    
    bigresult = {"logs":logs, "stats":stats, "matches":matches}
    html_report1 = HTMLReport(bigresult)
    html_report1.report_to_html()

if(2==1): #manual execution
    #file to process
    bucket_name="rtcw-stats-py-sci"
    file_key="input/rtcwconsoler2.log"
    
    processor = ClientLogProcessor(s3bucket=bucket_name, s3file = file_key, debug = True)
    result = processor.process_log()
    html_report = HTMLReport(result)
    html_report.report_to_html()
