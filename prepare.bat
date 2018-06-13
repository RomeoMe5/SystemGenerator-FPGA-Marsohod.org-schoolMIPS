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
set STATIC_PATH=.gen

mkdir %STATIC_PATH%

REM ===== Run application =====
REM WEB:
flask db init
flask db migrate -m "initial"
flask db upgrade

REM if no translations exists
flask translate init ru
REM extract strings to translate
flask translate update
REM make translations ready to use for app
flask translate compile

REM add existing posts to database
python web_add_existing_posts.py

flask run --with-threads
