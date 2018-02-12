# ===== Activate environment =====
# ===== Create virtual environment =====
sudo python3 -m venv .env

# ===== Activate environment =====
source .env/bin/activate

# ===== Install dependencies =====
# Dev:
sudo pip3 install --no-cache -r requirements.txt
# App(s):
sudo pip3 install --no-cache -r engine/requirements.txt
sudo pip3 install --no-cache -r gui_client/requirements.txt
sudo pip3 install --no-cache -r web_client/requirements.txt
# Tests:
sudo pip3 install --no-cache -r tests/requirements.txt

# ===== Set environment variables =====
export FLASK_APP=run.py
export FLASK_DEBUG=1
export FILE_ENCODING=utf-8
export FALLBACK_EXTENSION=jinja
export COPYRIGHT="MUEM (HSE University)"

# ===== Run application =====
# WEB:
# flask run --with-threads
# GUI:
# TODO
