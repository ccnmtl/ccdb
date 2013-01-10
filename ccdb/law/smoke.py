from smoketest import SmokeTest
from models import Snapshot


class DBConnectivity(SmokeTest):
    def test_retrieve(self):
        cnt = Snapshot.objects.all().count()
        self.assertTrue(cnt > 0)
