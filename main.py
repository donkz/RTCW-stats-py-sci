import os, sys
from processfile import FileProcessor
from utils.htmlreports import HTMLReport
import shutil
from datetime import datetime

#set relative path
RTCWPY_PATH = os.getcwd()
if not RTCWPY_PATH in sys.path:
    sys.path.append(RTCWPY_PATH)

#file to process
rtcwlogfile = r".\test_samples\rtcwconsole-2020-01-13.log"
#rtcwlogfile = r"C:\Games\rtcw\osp\rtcwconsole.log"

if "rtcwconsole.log" in rtcwlogfile:
    dt = datetime.now().strftime("%Y-%m-%d")
    dest = shutil.copyfile(rtcwlogfile, rtcwlogfile.replace(".log", "-" + dt + ".log")) 
    print("Copied file to: " + dest)

processor = FileProcessor(local_file = rtcwlogfile, debug = True)
result = processor.process_log()

html_report = HTMLReport(result)
html_report.report_to_html()