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

PMT_EXTERNAL_ADD_ITEM_URL = ("https://pmt.ccnmtl.columbia.edu"
                             "/api/external_add_item/")

SERVER_EMAIL = 'ccdb@ccnmtl.columbia.edu'
