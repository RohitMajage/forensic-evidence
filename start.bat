@echo off
echo ==================================================
echo Starting Forensic Evidence Development Server
echo ==================================================
echo.

:: Open default browser to the web page
echo Launching browser to http://127.0.0.1:8000/
start http://127.0.0.1:8000/

:: Start the Django server
python manage.py runserver

pause
