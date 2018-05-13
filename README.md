FPGAMarsohodCAD
===============
CAD for automatically configuring FPGA "Marsohod"

Read more on **[wiki](https://github.com/hell03end/FPGAMarsohodCAD/wiki)**.

[`CHANGELOG`](https://github.com/hell03end/FPGAMarsohodCAD/wiki/Changelog)


FPGA Marsohod CAD web interface
-------------------------------

```bash
# To get text run:
pybabel extract -F babel.cfg -k _l -o messages.pot .
# To add a translation run:
pybabel init -i messages.pot -d web_client/translations -l ru
# To update existing translations run:
pybabel update -i messages.pot -d web_client/translations
# To compile translations run:
pybabel compile -d web_client/translations
```
