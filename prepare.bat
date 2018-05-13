REM ===== Create virtual environment =====
python -m venv .venv

REM ===== Activate environment =====
".venv/Scripts/activate"

REM ===== Install dependencies =====
REM Dev:
REM contains web client dependencies
pip install --no-cache -r requirements.txt
REM App(s):
pip install --no-cache -r engine/requirements.txt
REM Tests:
pip install --no-cache -r tests/requirements.txt

REM ===== Set environment variables =====
set FLASK_APP=web_client/run.py
set FLASK_DEBUG=1

REM ===== Run application =====
REM WEB:
flask run --with-threads
