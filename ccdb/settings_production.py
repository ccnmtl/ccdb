# flake8: noqa
from ccdb.settings_shared import *
from ccnmtlsettings.production import common
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
￼

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


try:
    from ccdb.local_settings import *
except ImportError:
    pass

if hasattr(settings, 'SENTRY_DSN'):
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
    )
