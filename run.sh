# Create virtual environment
python3 -m venv .venv

# Activate environment
source .venv/bin/activate

# Install dependencies
pip3 install --no-cache -r requirements.txt

# Run tests
pip3 install -U pytest
pytest

# Run web client application in debug
python3 web_client.py -d
