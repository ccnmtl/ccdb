from django.conf import settings
from smoketest import SmokeTest
from ccdb.law.models import Snapshot


class DBConnectivity(SmokeTest):
    def test_retrieve(self):
        cnt = Snapshot.objects.all().count()
        self.assertTrue(cnt > 0)


class RequiredSettings(SmokeTest):
    def test_pmt_url(self):
        self.assertTrue(hasattr(settings, 'PMT_EXTERNAL_ADD_ITEM_URL'))
