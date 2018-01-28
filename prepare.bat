REM ===== Activate environment =====
".env/Scripts/activate"

REM ===== Install dependencies =====
REM Dev:
pip install --no-cache -r requirements.txt
REM App(s):
pip install --no-cache -r engine/requirements.txt
pip install --no-cache -r gui_client/requirements.txt
pip install --no-cache -r web_client/requirements.txt
REM Tests:
pip install --no-cache -r tests/requirements.txt

REM ===== Set environment variables =====
set FLASK_APP=run.py
set FLASK_DEBUG=1
set FILE_ENCODING=utf-8
set FALLBACK_EXTENSION=jinja
set COPYRIGHT="MUEM (HSE University)"

REM ===== Run application =====
REM WEB:
REM flask run --with-threads
REM GUI:
REM TODO
