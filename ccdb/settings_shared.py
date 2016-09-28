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

TEMPLATES[0]['OPTIONS']['context_processors'].append(  # noqa
    'ccdb.law.contextprocessors.add_public_snapshot'
)


INSTALLED_APPS += [  # noqa
    'ccdb.law',
]

if 'test' in sys.argv or 'jenkins' in sys.argv:
    CACHES = {
        'default': dict(
            BACKEND='django.core.cache.backends.dummy.DummyCache',
        )
    }

WIND_STAFF_MAPPER_GROUPS += [  # noqa
    'caj5', 'av2285', 'alm2165', 'pld2109', 'kac2160'
]

# TinyMCE settings

TINYMCE_JS_URL = '/site_media/js/tiny_mce/tiny_mce.js'
TINYMCE_JS_ROOT = 'media/js/tiny_mce'

# if you set this to True, you may have to
# override TINYMCE_JS_ROOT with the full path on production
TINYMCE_COMPRESSOR = False
TINYMCE_SPELLCHECKER = True

PMT_EXTERNAL_ADD_ITEM_URL = ("https://pmt.ccnmtl.columbia.edu"
                             "/api/external_add_item/")

TINYMCE_DEFAULT_CONFIG = {'cols': 80,
                          'rows': 30,
                          'plugins': 'table,spellchecker,paste,searchreplace',
                          'theme': 'simple',
                          }

SERVER_EMAIL = 'ccdb@ccnmtl.columbia.edu'
