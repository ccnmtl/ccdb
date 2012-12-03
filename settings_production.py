from settings_shared import *

TEMPLATE_DIRS = (
    "/var/www/ccdb/ccdb/templates",
)

MEDIA_ROOT = '/var/www/ccdb/uploads/'
COMPRESS_ROOT = '/var/www/ccdb/ccdb/media/'

DEBUG = False
TEMPLATE_DEBUG = DEBUG
#CACHE_BACKEND = 'locmem:///'
CACHE_BACKEND = 'file:///var/www/ccdb/cache/'
JOHNNY_MIDDLEWARE_KEY_PREFIX='jc_ccdb'

DATABASES = {
    'default' : {
        'ENGINE' : 'django.db.backends.postgresql_psycopg2',
        'NAME' : 'ccdb',
        'HOST' : '',
        'PORT' : 6432,
        'USER' : '',
        'PASSWORD' : '',
        }
}

import logging
from sentry.client.handlers import SentryHandler
logger = logging.getLogger()
if SentryHandler not in map(lambda x: x.__class__, logger.handlers):
    logger.addHandler(SentryHandler())
    logger = logging.getLogger('sentry.errors')
    logger.propagate = False
    logger.addHandler(logging.StreamHandler())
    SENTRY_REMOTE_URL = 'http://sentry.ccnmtl.columbia.edu/sentry/store/'
SENTRY_KEY = 'EWv5EELZnZIrOY'
SENTRY_SITE = 'ccdb'

try:
    from local_settings import *
except ImportError:
    pass

    
