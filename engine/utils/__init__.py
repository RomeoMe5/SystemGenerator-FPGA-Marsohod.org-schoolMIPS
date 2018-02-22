import os

PATHS = {'root': os.path.dirname(os.path.dirname(__file__))}
PATHS['static'] = os.path.join(PATHS['root'], "static")
PATHS['templ'] = os.path.join(PATHS['root'], "templates")
