from settings_shared import *

TEMPLATE_DIRS = (
    "/var/www/ccdb/ccdb/templates",
)

MEDIA_ROOT = '/var/www/ccdb/uploads/'

DEBUG = False
TEMPLATE_DEBUG = DEBUG
#CACHE_BACKEND = 'locmem:///'
CACHE_BACKEND = 'file:///var/www/ccdb/cache/'
JOHNNY_MIDDLEWARE_KEY_PREFIX='jc_ccdb'

try:
    from local_settings import *
except ImportError:
    pass

    
