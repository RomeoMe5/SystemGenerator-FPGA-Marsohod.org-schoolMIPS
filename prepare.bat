REM ===== Create virtual environment =====
python -m venv .venv

REM ===== Activate environment =====
".venv/Scripts/activate"

REM ===== Install dependencies =====
REM Dev:
pip install --no-cache -r requirements.txt REM contains web client dependencies
pip install --no-cache -r engine/requirements.txt REM engine
pip install --no-cache -r tests/requirements.txt REM tests

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

REM if not translations exists
flask translate init ru
flask translate update
flask translate compile

python web_client_config.py REM add existing posts to database

flask run --with-threads
