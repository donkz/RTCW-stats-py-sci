import os, sys
from processfile import FileProcessor
from utils.htmlreports import HTMLReport

#set relative path
RTCWPY_PATH = os.getcwd()
if not RTCWPY_PATH in sys.path:
    sys.path.append(RTCWPY_PATH)

#file to process
rtcwlogfile = r".\test_samples\rtcwconsole-2020-01-13.log"

processor = FileProcessor(rtcwlogfile, debug=False)
result = processor.process_log()
html_report = HTMLReport(result)
html_report.report_to_html()
