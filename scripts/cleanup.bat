@echo This will delete junk files from working folder
@pause

@echo Deleting all html files(reports)...
@del /S ..\*.html
@echo.

@echo Deleting all csv files(aggregate results)...
@del /S ..\*.csv
@echo.

@echo Deleting testfile.txt (debugging)
@del ..\testfile.txt
@del ..\tests\testfile.txt
@echo.

@echo Deleting pychache folders
@rmdir /s /q "../rtcwlog/constants/__pycache__"
@rmdir /s /q "../rtcwlog/io/__pycache__"
@rmdir /s /q "../rtcwlog/textsci/__pycache__"
@rmdir /s /q "../rtcwlog/utils/__pycache__"
@rmdir /s /q "../rtcwlog/seasons/__pycache__"

@rmdir /s /q "../tests/__pycache__"
@rmdir /s /q "../__pycache__"
@echo. 

@pause