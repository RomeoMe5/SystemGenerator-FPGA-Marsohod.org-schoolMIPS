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
# export FLASK_APP=app.py
export FLASK_DEBUG=1
export STATIC_PATH=.gen

mkdir $STATIC_PATH

mkdir configs

# ===== Run application =====
# WEB:
flask db init
flask db migrate -m "initial"
flask db upgrade

# if no translations exists
flask translate init ru
# extract strings to translate
flask translate update
# make translations ready to use for app
flask translate compile

# add existing posts to database
python3 web_add_existing_posts.py

flask run --with-threads
