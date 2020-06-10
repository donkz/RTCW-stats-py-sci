@echo This will delete junk files from this folder %CD%
@pause

@echo Deleting all html files(reports)...
@del /S *.html
@echo.

@echo Deleting all csv files(aggregate results)...
@del /S *.csv
@echo.

@echo Deleting testfile.txt (debugging)
@del *testfile.txt
@echo.

@echo Deleting pychache folders
@rmdir /s /q "constants/__pycache__"
@rmdir /s /q "tests/__pycache__"
@rmdir /s /q "textsci/__pycache__"
@rmdir /s /q "utils/__pycache__"
@rmdir /s /q "seasons_code/__pycache__"
@rmdir /s /q "__pycache__"
@rmdir /s /q "temp"
@echo. 

@pause