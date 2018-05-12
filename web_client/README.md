# FPGA Marsohod CAD web interface

```bash
# To get text run:
pybabel extract -F babel.cfg -k _l -o messages.pot .
# To add a translation run:
pybabel init -i messages.pot -d app/translations -l ru
# To update existing translations run:
pybabel update -i messages.pot -d app/translations
# To compile translations run:
pybabel compile -d app/translations
```
