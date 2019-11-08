# flake8: noqa
from ccdb.settings_shared import *
from ccnmtlsettings.staging import common
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

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
    from ccdb.local_settings import *
except ImportError:
    pass

if hasattr(settings, 'SENTRY_DSN'):
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        debug=True,
    )
