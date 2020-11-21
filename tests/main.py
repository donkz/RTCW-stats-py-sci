import os, sys
import shutil
from datetime import datetime

from rtcwlog.clientlog import ClientLogProcessor
from rtcwlog.report.htmlreports import HTMLReport

#set relative path
RTCWPY_PATH = os.getcwd()
RTCWPY_PATH = RTCWPY_PATH.replace("\\tests","")
if not RTCWPY_PATH in sys.path:
    sys.path.append(RTCWPY_PATH)

#file to process
#rtcwlogfile = r"..\data\test_samples\rtcwconsole - r2.log"
#rtcwlogfile = r"..\data\test_samples\2020-08-09-07-02-37-rtcwconsole.log"
#rtcwlogfile = r"..\data\seasons_data\2020Oct\2020-10-23-04-02-26-rtcwconsole2222.log"
#rtcwlogfile = r"..\data\test_samples\rtcwconsole-2020-01-09.log" #map error
#rtcwlogfile = r"..\data\test_samples\rtcwconsole - r2.log"
#rtcwlogfile = r"..\data\test_samples\rtcwconsole-2019-12-15.log"
    
#fonzes duplication
rtcwlogfile = r"C:\Users\zveres\Downloads\2020-11-09-04-28-10-rtcwconsole.log"
#rtcwlogfile = r"C:\Users\zveres\Downloads\2020-11-09-04-27-57-donka.log"
    

#if it's a plain rtcwconsole.log file copy it into rtcwconsole-date.log for backup
if rtcwlogfile[-16:] == "\rtcwconsole.log":
    dt = datetime.now().strftime("%Y-%m-%d")
    dest = shutil.copyfile(rtcwlogfile, rtcwlogfile.replace(".log", "-" + dt + ".log")) 
    print("Copied file to: " + dest)

#process the file= 
processor = ClientLogProcessor(local_file = rtcwlogfile, debug = True)
result = processor.process_log()

#create HTML from the processed data
html_report = HTMLReport(result)
html_report.report_to_html()
#html_report.report_to_html(folder="C:/stats/")
#html_report.report_to_html(folder="C:/stats/", filenoext = "mystats" )