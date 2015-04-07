# flake8: noqa
from settings_shared import *

TEMPLATE_DIRS = (
    "/var/www/ccdb/ccdb/ccdb/templates",
)


MEDIA_ROOT = '/var/www/ccdb/uploads/'
COMPRESS_ROOT = '/var/www/ccdb/ccdb/media/'

DEBUG = False
TEMPLATE_DEBUG = DEBUG

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

AWS_STORAGE_BUCKET_NAME = "ccnmtl-ccdb-static-prod"
AWS_PRELOAD_METADATA = True
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto.S3BotoStorage'
S3_URL = 'https://%s.s3.amazonaws.com/' % AWS_STORAGE_BUCKET_NAME
# static data, e.g. css, js, etc.
STATICFILES_STORAGE = 'cacheds3storage.CompressorS3BotoStorage'
STATIC_URL = 'https://%s.s3.amazonaws.com/media/' % AWS_STORAGE_BUCKET_NAME
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
