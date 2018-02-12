source .venv/bin/activate
# pip3 install -r requirements.txt
export FLASK_APP=run.py
export FLASK_DEBUG=1
flask run --with-threads
