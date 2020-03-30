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
rtcwlogfile = r"C:\Users\zveres\Downloads\rtcwconsole.log"
#rtcwlogfile = r"C:\Users\zveres\Downloads\rtcwconsole-2020-03-16.log"

dt = datetime.now().strftime("%Y-%m-%d")
dest = shutil.copyfile(rtcwlogfile, rtcwlogfile.replace(".log", dt+".log")) 
print("Copied file to: " + dest)

processor = FileProcessor(local_file = rtcwlogfile, debug = False)
result = processor.process_log()
html_report = HTMLReport(result)
html_report.report_to_html()