import os
import pandas as pd

from processfile import FileProcessor
from utils.htmlreports import HTMLReport

#set relative path
RTCWPY_PATH = os.getcwd()
import sys
if not RTCWPY_PATH in sys.path:
    sys.path.append(RTCWPY_PATH)

#expan viewing area for pandas datasets (visual inspection only)
pd.set_option("display.max_rows",40)
pd.set_option("display.max_columns",20)
pd.set_option("display.width",300)

#file where processed lines will be written to for the last processed file
debug_file = r".\test_samples\testfile.txt"

#test files to process
stat_files = [
r".\test_samples\rtcwconsole - r2.log",
r".\test_samples\rtcwconsole-8-30-2018.log",
r".\test_samples\rtcwconsole-20190905.log",
r".\test_samples\rtcwconsole-09-12-2019.log", #http://krisofwin.com/stats/stats/2019.Sep.13.%2015h54m23s.html
r".\test_samples\rtcwconsole-2019-10-02.log",
r".\test_samples\rtcwconsole-09-19-2019.log",
r".\test_samples\rtcwconsole-2019-10-10.log",
r".\test_samples\rtcwconsole-2019-10-17.log",
r".\test_samples\rtcwconsole-2019-10-24.log",
r".\test_samples\rtcwconsoleOct28.log",
#r".\test_samples\rtcwconsole-MNF-2019-11-05.log",
r".\test_samples\rtcwconsole-2019-11-07.log"
]

#just pick one for debugging
stat_files = stat_files[-1:]

results = []
for read_file in stat_files:
    processor = FileProcessor(read_file, debug_file)
    result = processor.process_log()
    results.append(result)
    index = str(len(results) -1)
    print(f'Processed file: {read_file} into results[{index}]')

results = results[-1] #temporary
    
if (1==2) and results is not None:
    logdf = results["logdf"]
    statsdf= results["stats"]
    matchesdf = results["matchesdf"]
    renamedf = results["renamedf"]

if(1==2): #manual execution
    logdf.to_csv(r"./test_samples/result_client_log.csv", index=False)
    statsdf.to_csv(r"./test_samples/result_client_log_sum_stats.csv", index=False)
    matchesdf.to_csv(r"./test_samples/result_client_log_matches.csv", index=False)

#debug execution
html_report = HTMLReport(results)
html_report.report_to_html(r".\test_samples\html_report.html")


            
