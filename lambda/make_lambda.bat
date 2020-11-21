@echo This will create a lambda folder in %CD%\lambda
@pause

@echo Deleting previous folder...
@rmdir /s /q "tmp"
@echo.


@echo Creating new folder structure %CD%\tmp...
@echo When done, zip inner contents of %CD%\tmp\
@mkdir tmp
@mkdir tmp\rtcwlog
@mkdir tmp\rtcwlog\constants
@mkdir tmp\rtcwlog\io
@mkdir tmp\rtcwlog\report
@mkdir tmp\rtcwlog\textsci
@mkdir tmp\rtcwlog\utils

@mkdir tmp\seasons

@mkdir tmp\data
@mkdir tmp\data\test_samples


@echo Copying essential files into %CD%\lambda...
copy ..\rtcwlog\constants\__init__.py tmp\rtcwlog\constants
copy ..\rtcwlog\constants\const_osp.py tmp\rtcwlog\constants
copy ..\rtcwlog\constants\logtext.py tmp\rtcwlog\constants
copy ..\rtcwlog\constants\maps.py tmp\rtcwlog\constants

copy ..\rtcwlog\io\__init__.py tmp\rtcwlog\io
copy ..\rtcwlog\io\statswriter.py tmp\rtcwlog\io

copy ..\rtcwlog\report\__init__.py tmp\rtcwlog\report
copy ..\rtcwlog\report\awards.py tmp\rtcwlog\report
copy ..\rtcwlog\report\awardtext.py tmp\rtcwlog\report
copy ..\rtcwlog\report\htmlreports.py tmp\rtcwlog\report
copy ..\rtcwlog\report\matchstats.py tmp\rtcwlog\report

copy ..\rtcwlog\textsci\__init__.py tmp\rtcwlog\textsci
copy ..\rtcwlog\textsci\aliases.py tmp\rtcwlog\textsci
copy ..\rtcwlog\textsci\teams.py tmp\rtcwlog\textsci

copy ..\rtcwlog\utils\__init__.py tmp\rtcwlog\utils
copy ..\rtcwlog\utils\decorators.py tmp\rtcwlog\utils
copy ..\rtcwlog\utils\ospstrings.py tmp\rtcwlog\utils
copy ..\rtcwlog\utils\rtcwcolors.py tmp\rtcwlog\utils

copy ..\rtcwlog\__init__.py tmp\rtcwlog
copy ..\rtcwlog\clientlog.py tmp\rtcwlog

copy ..\seasons\season_medals.py tmp\seasons

copy ..\data\test_samples\rtcwconsole-2020-02-17.log tmp\data\test_samples

copy lambda_function.py tmp\

7z a lambda.zip tmp

@pause


