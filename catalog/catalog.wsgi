#!/usr/bin/python

import sys
import logging
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/var/www/catalog/")

from catalog import app as application
application.secret_key = 'catalogkey'
# from catalog import app

# app.secret_key = 'super_secret_key'
# app.debug = True
# app.run()
