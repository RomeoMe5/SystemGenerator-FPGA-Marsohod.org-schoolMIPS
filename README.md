FPGAMarsohodCAD
===============
CAD for automatically configuring FPGA "Marsohod"

#### Requirements
* Python >= 3.6

#### Examples
See `engine_example.py` and `convert_example.py`.

FPGA Marsohod CAD web interface
-------------------------------
#### How to run [linux]?
```bash
# first, clone repository
git clone https://github.com/hell03end/FPGAMarsohodCAD

# then install dependencies
pip install --no-cache -r requirements.txt
pip install --no-cache -r engine/requirements.txt

# set environment variables [use 'set' instead of 'export' for winfows]
export FLASK_APP=run_web.py
export FLASK_DEBUG=1
export STATIC_PATH=.generated # where to store generated configs

# [use '%STATIC_PATH%' for windows]
mkdir $STATIC_PATH

# create database
flask db init
flask db upgrade # is it necessery?

# compile translations (optional)
flask translate compile

# finally, run application
flask run --with-threads
```

You also need to create `.env` file to configure mailing.

Example:
```bash
SECRET_KEY=<secret key>
MAIL_SERVER=smtp.googlemail.com
MAIL_PORT=587
MAIL_USE_TLS=1
MAIL_USERNAME="example@mail.com"
MAIL_PASSWORD=<password>
```

<!-- ```bash
# To get text run:
pybabel extract -F babel.cfg -k _l -o messages.pot .
# To add a translation run:
pybabel init -i messages.pot -d web_client/translations -l ru
# To update existing translations run:
pybabel update -i messages.pot -d web_client/translations
# To compile translations run:
pybabel compile -d web_client/translations
``` -->

Read more on **[wiki](https://github.com/hell03end/FPGAMarsohodCAD/wiki)**.

[`CHANGELOG`](https://github.com/hell03end/FPGAMarsohodCAD/wiki/Changelog)
