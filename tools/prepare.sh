# Create virtual environment
sudo python3 -m venv .venv

# Activate environment
source .venv/bin/activate

# Install dependencies
sudo pip3 install --no-cache -r requirements.txt

# Set environment variables
export FLASK_APP=api_client.py
export FLASK_ENV=development

# Run application
flask run --with-threads
