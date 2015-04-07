# flake8: noqa
from settings_shared import *
import os

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), "templates"),
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

AWS_S3_CUSTOM_DOMAIN = "d2k49vc6oxh5lr.cloudfront.net"
AWS_STORAGE_BUCKET_NAME = "ccnmtl-ccdb-static-stage"
AWS_PRELOAD_METADATA = True
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
S3_URL = 'https://%s/' % AWS_S3_CUSTOM_DOMAIN
STATIC_URL = 'https://%s/media/' % AWS_S3_CUSTOM_DOMAIN
# static data, e.g. css, js, etc.
STATICFILES_STORAGE = 'cacheds3storage.CompressorS3BotoStorage'
COMPRESS_ENABLED = True
COMPRESS_OFFLINE = True
COMPRESS_ROOT = STATIC_ROOT
COMPRESS_URL = STATIC_URL
COMPRESS_STORAGE = 'cacheds3storage.CompressorS3BotoStorage'
# uploaded images
MEDIA_URL = 'https://%s.s3.amazonaws.com/uploads/' % AWS_STORAGE_BUCKET_NAME

if 'migrate' not in sys.argv:
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')

try:
    from local_settings import *
except ImportError:
    pass
