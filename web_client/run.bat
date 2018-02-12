REM ".venv\Scripts\python.exe" -m pip install -r requirements.txt
set FLASK_DEBUG=1
set FLASK_APP=web_client/run.py
".venv\Scripts\flask.exe" run --with-threads
