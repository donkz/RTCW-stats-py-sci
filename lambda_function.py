import os, sys
from processfile import FileProcessor
from utils.htmlreports import HTMLReport
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    #set relative path
    RTCWPY_PATH = os.getcwd()
    if not RTCWPY_PATH in sys.path:
        sys.path.append(RTCWPY_PATH)

    #rtcwlogfile = r"/var/task/test_samples/rtcwconsole-2020-02-17.log"
    #processor = FileProcessor(local_file = rtcwlogfile, debug = False)
    
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    logger.info('Reading {} from {}'.format(file_key, bucket_name))

    debug = True
    processor = FileProcessor(s3bucket=bucket_name, s3file = file_key, debug = debug, debug_file = "/tmp/debug_file.txt")
    result = processor.process_log()
    
    html_report = HTMLReport(result)
    local_file, filename = html_report.report_to_html("/tmp/")
    
    s3 = boto3.resource('s3')
    bucket = s3.Bucket('donkanator.com')
    
    if local_file:
        cloud_file = 'stats/' + filename
        bucket.upload_file(local_file, cloud_file, ExtraArgs={'ContentType': 'text/html'})
        
    if debug: 
        bucket.upload_file("/tmp/debug_file.txt", "debug/debug_file.txt", ExtraArgs={'ContentType': 'text/html'})
    
    message ="Nothing was processed"
    if result is not None and len(result) > 0:
        message = 'Stats lines: ' + str(len(result["stats"]))
        
    return { 
        'message' : message
    }  

