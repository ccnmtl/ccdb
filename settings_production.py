from settings_shared import *

TEMPLATE_DIRS = (
    "/var/www/ccdb/ccdb/templates",
)

MEDIA_ROOT = '/var/www/ccdb/uploads/'

DEBUG = False
TEMPLATE_DEBUG = DEBUG
#CACHE_BACKEND = 'locmem:///'
CACHE_BACKEND = 'johnny.backends.locmem:///'
JOHNNY_MIDDLEWARE_KEY_PREFIX='jc_ccdb'
