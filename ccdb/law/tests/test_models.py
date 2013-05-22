from django.test import TestCase
from ccdb.law.models import Snapshot


class SnapshotModelTest(TestCase):
    def setUp(self):
        self.s = Snapshot.objects.create(
            label="test snapshot",
            status="vetted")

    def tearDown(self):
        self.s.delete()

    def test_unicode(self):
        self.assertEquals(unicode(self.s), "test snapshot")
