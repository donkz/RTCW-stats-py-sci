#RTCW Log File Processor - RTCW-stats-py-sci

> What is this?

This is a python program that processes rtcwconsole.log files and spits out a match report in HTML format

> What is rtcwconsole.log?

rtcwmp.exe creates the file if you have setting /logfile 2. It creates the file in the folder of the mod that the game is using, for example:

* c:\rtcw\osp\rtcwconsole.log
* c:\rtcw\rtcwpro\rtcwconsole.log

> Why this one?

This system uses Python programming language and it relies on a popular data science package - pandas. Both are incredibly popular in 2020s and quite useful and easy to learn

> What else?

What sets apart this log processor is an ability to detect maps, times, team wins, and more metrics than any other log processor had to offer

> What do I need to run it?

Install python first. 

You can use any IDE or no IDE at all, but I recommend installing anaconda that comes with SPYDER IDE. So far it's the most useful and crafty IDE although not as colorful as say VSCode or Pycharm

Install packages next. 

cd into the directory of the project and do:

* pip install -r requirements.txt

This will install all necessary packages

Once installed, edit test/main.py to provide the path to your rtcwconsole.log file and run it

> What else does it do? 

RTCW-stats-py-sci is oriented much further than providing one html report:

* It processes the data into pandas dataframes that can be saved as excel, csv, or parquet files 
* You can pack up when it leaves off: extend your code to process dataframes differently
* Each round is provided with a hash and can be saved forever next to other processed matches. Each one will have their own hash.
* These files can be plugged into visualization and analytics tools like excel, tableau, athena, presto, etc
* Reads files from AWS S3
* Compatible with AWS lambda
* Has quite a few nifty NLP algorythms to detect clan tags and plans to decipher player name variations
* It has means of extensibility for new maps and awards

Most importantly, it has current active support

Example report (at the time of creation):

https://s3.amazonaws.com/donkanator.com/stats/forever/stats-2020-02-09-8d2e.html