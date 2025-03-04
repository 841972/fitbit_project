@echo off
echo Installing dependencies...

REM Install requests
pip install requests

REM Install psycopg2
pip install psycopg2
REM Install python-dotenv
pip install python-dotenv
REM Install qrcode
pip install qrcode[pil]
REM Install google-auth
pip install google-auth
REM Install google-auth-oauthlib
pip install google-auth-oauthlib
REM Install google-auth-httplib2
pip install google-auth-httplib2
REM Install google-api-python-client
pip install --upgrade google-api-python-client
REM Install flask
pip install Flask




echo Dependencies installed successfully!
pause