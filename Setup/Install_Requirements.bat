echo You need to have Python 3.7 (and the included PIP package) installed for this to work!  Click OK to install all required packages.
pause

start "" https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-v5.0.1.20220118.exe

echo Install this program in its default directory before starting the bot! 
pause

py -3.7 -m pip install --upgrade pip setuptools wheel --user

py -3.7 -m pip install -r requirements.txt --user --no-warn-script-location

py -3.7 ../RxBot/Settings.py --g



pause