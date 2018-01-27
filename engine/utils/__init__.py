import os
import engine

PATHS = {'root': os.path.dirname(engine.__file__)}
PATHS['static'] = os.path.join(PATHS['root'], "static")
PATHS['templ'] = os.path.join(PATHS['root'], "templates")
