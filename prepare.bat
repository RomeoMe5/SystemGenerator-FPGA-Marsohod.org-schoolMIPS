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
set FLASK_APP=run_web.py
set FLASK_DEBUG=1
set STATIC_PATH=.generated

mkdir %STATIC_PATH%

REM ===== Run application =====
REM WEB:
flask db init
flask db migrate
flask db upgrade

flask translate init ru
flask translate update
flask translate compile

flask run --with-threads
