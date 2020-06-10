@echo This will create a lambda folder in %CD%\lambda
@pause

@echo Deleting previous folder...
@rmdir /s /q "tmp"
@echo.


@echo Creating new folder structure %CD%\lambda...
@mkdir tmp
@mkdir tmp\utils
@mkdir tmp\textsci
@mkdir tmp\constants
@mkdir tmp\test_samples

@echo Copying essential files into %CD%\lambda...
copy ..\constants\__init__.py tmp\constants
copy ..\constants\awardtext.py tmp\constants
copy ..\constants\logtext.py tmp\constants
copy ..\constants\maps.py tmp\constants

copy ..\test_samples\rtcwconsole-2020-02-17.log tmp\test_samples

copy ..\textsci\__init__.py tmp\textsci
copy ..\textsci\aliases.py tmp\textsci
copy ..\textsci\awards.py tmp\textsci
copy ..\textsci\matchstats.py tmp\textsci
copy ..\textsci\teams.py tmp\textsci

copy ..\utils\__init__.py tmp\utils
copy ..\utils\rtcwcolors.py tmp\utils
copy ..\utils\htmlreports.py tmp\utils

copy ..\processfile.py tmp\
copy lambda_function.py tmp\

@pause