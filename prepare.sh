# ===== Create virtual environment =====
sudo python3 -m venv .venv

# ===== Activate environment =====
source .venv/bin/activate

# ===== Install dependencies =====
# Dev:
sudo pip3 install --no-cache -r requirements.txt # contains web client dependencies
sudo pip3 install --no-cache -r engine/requirements.txt # engine
sudo pip3 install --no-cache -r tests/requirements.txt # tests

# ===== Set environment variables =====
export FLASK_APP=run_web.py
export FLASK_DEBUG=1
export STATIC_PATH=.generated

mkdir $STATIC_PATH

mkdir configs

# ===== Run application =====
# WEB:
flask db init
flask db migrate
flask db upgrade

flask translate init ru
flask translate update
flask translate compile

python3 web_client_config.py # add existing posts to database

flask run --with-threads
