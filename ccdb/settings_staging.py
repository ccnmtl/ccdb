# flake8: noqa
from settings_shared import *

TEMPLATE_DIRS = (
    "/var/www/ccdb/ccdb/ccdb/templates",
)


MEDIA_ROOT = '/var/www/ccdb/uploads/'
COMPRESS_ROOT = '/var/www/ccdb/ccdb/media/'

DEBUG = False
TEMPLATE_DEBUG = DEBUG
STAGING_ENV = True
STATSD_PREFIX = 'ccdb-staging'

JOHNNY_MIDDLEWARE_KEY_PREFIX='jc_ccdb'

CACHES = {
    'default': dict(
        BACKEND='johnny.backends.filebased.FileBasedCache',
        LOCATION='file:///var/www/ccdb/cache/',
        JOHNNY_CACHE=True,
    )
}


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

if 'migrate' not in sys.argv:
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')

try:
    from local_settings import *
except ImportError:
    pass
