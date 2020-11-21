import os, sys
from rtcwlog.clientlog import ClientLogProcessor
from rtcwlog.report.htmlreports import HTMLReport
import logging
import boto3

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    #set relative path
    RTCWPY_PATH = os.getcwd()
    if not RTCWPY_PATH in sys.path:
        sys.path.append(RTCWPY_PATH)

    #rtcwlogfile = r"/var/task/data/test_samples/rtcwconsole-2020-02-17.log"
    #processor = ClientLogProcessor(local_file = rtcwlogfile, debug = False)
    
    bucket_name = event['Records'][0]['s3']['bucket']['name']
    file_key = event['Records'][0]['s3']['object']['key']
    file_size = event["Records"][0]["s3"]["object"]["size"]
    logger.info('Reading {} from {}'.format(file_key, bucket_name))

    debug = True
    processor = ClientLogProcessor(s3bucket=bucket_name, s3file = file_key, s3file_size = file_size, debug = debug, debug_file = "/tmp/debug_file.txt")
    result = processor.process_log()
    
    html_report = HTMLReport(result)
    local_file, filename = html_report.report_to_html(folder="/tmp/", filenoext = os.path.basename(file_key).replace(".log",""))
    
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

