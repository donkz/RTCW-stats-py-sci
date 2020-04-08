@echo This will create a lambda folder in %CD%\lambda
@pause

@echo Deleting previous folder...
@rmdir /s /q "lambda"
@echo.


@echo Creating new folder structure %CD%\lambda...
@mkdir lambda
@mkdir lambda\utils
@mkdir lambda\textsci
@mkdir lambda\constants
@mkdir lambda\test_samples

@echo Copying essential files into %CD%\lambda...
copy constants\__init__.py lambda\constants
copy constants\awardtext.py lambda\constants
copy constants\logtext.py lambda\constants
copy constants\maps.py lambda\constants

copy test_samples\rtcwconsole-2020-02-17.log lambda\test_samples

copy textsci\__init__.py lambda\textsci
copy textsci\aliases.py lambda\textsci
copy textsci\awards.py lambda\textsci
copy textsci\matchstats.py lambda\textsci
copy textsci\teams.py lambda\textsci

copy utils\__init__.py lambda\utils
copy utils\rtcwcolors.py lambda\utils
copy utils\htmlreports.py lambda\utils

copy processfile.py lambda\
copy lambda_function.py lambda\

@pause