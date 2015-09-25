# flake8: noqa
from settings_shared import *
from ccnmtlsettings.staging import common

locals().update(
    common(
        project=project,
        base=base,
        INSTALLED_APPS=INSTALLED_APPS,
        STATIC_ROOT=STATIC_ROOT,
        cloudfront="d2k49vc6oxh5lr",
    ))

CACHES = {
    'default': dict(
        BACKEND='django.core.cache.backends.filebased.FileBasedCache',
        LOCATION='file:///var/www/ccdb/cache/',
    )
}

try:
    from local_settings import *
except ImportError:
    pass
