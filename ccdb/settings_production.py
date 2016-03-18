# flake8: noqa
from settings_shared import *
from ccnmtlsettings.production import common

locals().update(
    common(
        project=project,
        base=base,
        INSTALLED_APPS=INSTALLED_APPS,
        STATIC_ROOT=STATIC_ROOT,
        cloudfront="d3uosc1woidfa6",
    ))

CACHES = {
    'default': dict(
        BACKEND='django.core.cache.backends.filebased.FileBasedCache',
        LOCATION='file:///var/www/ccdb/cache/',
    )
}

INSTALLED_APPS += [
    'opbeat',
]
MIDDLEWARE_CLASSES.insert(0, 'opbeat.contrib.django.middleware.OpbeatAPMMiddleware')


try:
    from local_settings import *
except ImportError:
    pass
