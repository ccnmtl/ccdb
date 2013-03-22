import os, sys, site

# paths we might need to pick up the project's settings
sys.path.append('/var/www/ccdb/ccdb/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'ccdb.settings_staging'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
