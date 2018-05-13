# ===== Create virtual environment =====
sudo python3 -m venv .venv

# ===== Activate environment =====
source .venv/bin/activate

# ===== Install dependencies =====
# Dev:
sudo pip3 install --no-cache -r requirements.txt  # contains web client dependencies
# App(s):
sudo pip3 install --no-cache -r engine/requirements.txt
# Tests:
sudo pip3 install --no-cache -r tests/requirements.txt

# ===== Set environment variables =====
export FLASK_APP=web_client/run.py
export FLASK_DEBUG=1

# ===== Run application =====
# WEB:
flask run --with-threads
