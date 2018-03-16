# flake8: noqa
from ccdb.settings_shared import *
try:
    from ccdb.local_settings import *
except ImportError:
    pass
