import os, sys
import shutil
from datetime import datetime

#set relative path
RTCWPY_PATH = os.getcwd()
RTCWPY_PATH = RTCWPY_PATH.replace("\\tests","")
if not RTCWPY_PATH in sys.path:
    sys.path.append(RTCWPY_PATH)

from rtcwlog.clientlog import ClientLogProcessor
from rtcwlog.report.htmlreports import HTMLReport



#file to process
#rtcwlogfile = r"..\data\test_samples\rtcwconsole - r2.log"
#rtcwlogfile = r"..\data\test_samples\2020-08-09-07-02-37-rtcwconsole.log"
#rtcwlogfile = r"..\data\seasons_data\2020Oct\2020-10-23-04-02-26-rtcwconsole2222.log"
#rtcwlogfile = r"..\data\test_samples\rtcwconsole-2020-01-09.log" #map error
#rtcwlogfile = r"..\data\test_samples\rtcwconsole - r2.log"
#rtcwlogfile = r"..\data\test_samples\rtcwconsole-2019-12-15.log"
    
rtcwlogfile = r"D:\Games\Return to Castle Wolfenstein\rtcwpro\rtcwconsole11-22-2020-b.log"


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

#RTCWPro TODO 
#Allies have lost the Unholy Grail!
#[skipnotify] before clocks
#[skipnotify]^z before /statsall

#osp
#^1Axis^7   ^7Fister Miagi   ^3   7  12   1  1^7  36^3   1^2  1305^1  1917^6  123^3      6
#^4Allies^7 ^7bru            ^3   7  16   0  0^7  30^3   2^2  1442^1  2840^6    0^3     11

#rtcwpro
#^1Axis ^7Team
#^7john_mullins   ^e  14^7   6   2  0^7^c  70^7  0  38.33  10^2 1880^1 1126^4    0^5    2^7    9
#^4Allied ^7Team
#^3recount-donka  ^e   4^7   6   0  0^3^c  40^7  0  34.32   1^2  920^1 1211^4   36^5    6^7    8

#osp
#Accuracy info for:
#rtcwpro
#Overall stats for:

#rtcwpro - ingame
#^7Overall stats for:
#rtcwpro - statsall
#[skipnotify]^7Overall stats for:

