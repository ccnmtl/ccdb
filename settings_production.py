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

SENTRY_SITE = 'ccdb'
SENTRY_SERVERS = ['http://sentry.ccnmtl.columbia.edu/sentry/store/']

import logging
from raven.contrib.django.handlers import SentryHandler
logger = logging.getLogger()
# ensure we havent already registered the handler
if SentryHandler not in map(type, logger.handlers):
    logger.addHandler(SentryHandler())

    # Add StreamHandler to sentry's default so you can catch missed exceptions
    logger = logging.getLogger('sentry.errors')
    logger.propagate = False
    logger.addHandler(logging.StreamHandler())

try:
    from local_settings import *
except ImportError:
    pass
