# Create virtual environment
sudo python3 -m venv .venv

# Activate environment
source .venv/bin/activate

# Install dependencies
sudo pip3 install --no-cache -r requirements.txt

# Run web client application in debug
python3 web_client.py -d
