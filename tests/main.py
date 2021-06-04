import os
import sys
import shutil
from datetime import datetime
from rtcwlog.clientlog import ClientLogProcessor
from rtcwlog.report.htmlreports import HTMLReport

# set relative path
RTCWPY_PATH = os.getcwd()
RTCWPY_PATH = RTCWPY_PATH.replace("\\tests", "")
if RTCWPY_PATH not in sys.path:
    sys.path.append(RTCWPY_PATH)

# file to process
rtcwlogfile = r"..\tests\test_samples\2021-02-17-05-17-39-industrial.log"

# if it's a plain rtcwconsole.log file copy it into rtcwconsole-date.log for backup
if rtcwlogfile[-16:] == "\rtcwconsole.log":
    dt = datetime.now().strftime("%Y-%m-%d")
    dest = shutil.copyfile(rtcwlogfile, rtcwlogfile.replace(".log", "-" + dt + ".log"))
    print("Copied file to: " + dest)

# process the file=
processor = ClientLogProcessor(local_file=rtcwlogfile, debug=True)
result = processor.process_log()

# create HTML from the processed data
html_report = HTMLReport(result)
html_report.report_to_html()
# html_report.report_to_html(folder="C:/stats/")
# html_report.report_to_html(folder="C:/stats/", filenoext = "mystats" )
