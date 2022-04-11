# Django settings for ccdb project.
import os.path
import sys
from ccnmtlsettings.shared import common

project = 'ccdb'
base = os.path.dirname(__file__)

locals().update(common(project=project, base=base))

ALLOWED_HOSTS += ['.law.columbia.edu']  # noqa

PROJECT_APPS = ['ccdb.law', ]

CACHES = {
    'default': dict(
        BACKEND='django.core.cache.backends.locmem.LocMemCache',
        LOCATION='ccdb-unique-snowflake',
    )
}

MIDDLEWARE += [  # noqa
    'django_cas_ng.middleware.CASMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'django_cas_ng.backends.CASBackend'
]


INSTALLED_APPS += [  # noqa
    'django_cas_ng',
    'ccdb.law',
]

INSTALLED_APPS.remove('djangowind') # noqa

if 'test' in sys.argv or 'jenkins' in sys.argv:
    CACHES = {
        'default': dict(
            BACKEND='django.core.cache.backends.dummy.DummyCache',
        )
    }

WIND_STAFF_MAPPER_GROUPS += [  # noqa
    'caj5', 'av2285', 'alm2165', 'pld2109', 'kac2160'
]

PMT_EXTERNAL_ADD_ITEM_URL = ("https://pmt.ccnmtl.columbia.edu"
                             "/api/external_add_item/")

SERVER_EMAIL = 'ccdb@ccnmtl.columbia.edu'

SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

CAS_SERVER_URL = 'https://cas.columbia.edu/cas/'
CAS_VERSION = '3'
CAS_ADMIN_REDIRECT = False

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(base, "templates"),
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
                'stagingcontext.staging_processor',
                'gacontext.ga_processor',
                'django.template.context_processors.csrf',
                'ccdb.law.contextprocessors.add_public_snapshot'
            ],
        },
    },
]

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'
