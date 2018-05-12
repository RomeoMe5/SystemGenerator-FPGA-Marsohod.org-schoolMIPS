REM ===== Create virtual environment =====
python -m venv .env

REM ===== Activate environment =====
".env/Scripts/activate"

REM ===== Install dependencies =====
REM Dev:
pip install --no-cache -r requirements.txt
REM App(s):
pip install --no-cache -r engine/requirements.txt
pip install --no-cache -r web_client/requirements.txt
REM Tests:
pip install --no-cache -r tests/requirements.txt

REM ===== Set environment variables =====
set FLASK_APP=web_client/run.py
set FLASK_DEBUG=1

REM ===== Run application =====
REM WEB:
flask run --with-threads
