from django.test import TestCase
from ccdb.law.models import Snapshot, public_snapshot


class SnapshotModelTest(TestCase):
    def setUp(self):
        self.s = Snapshot.objects.create(
            label="test snapshot",
            status="vetted")

    def tearDown(self):
        self.s.delete()

    def test_unicode(self):
        self.assertEquals(unicode(self.s), "test snapshot")

    def test_dump_filename_base(self):
        assert "T" in self.s.dump_filename_base()

    def test_to_json(self):
        self.assertEqual(self.s.to_json()['label'], self.s.label)

    def test_is_most_recent_vetted(self):
        self.assertTrue(self.s.is_most_recent_vetted())

    def test_is_current_working(self):
        self.assertFalse(self.s.is_current_working())

    def test_cloneable(self):
        self.assertTrue(self.s.cloneable())

    def test_get_absolute_url(self):
        self.assertEquals(self.s.get_absolute_url(),
                          "/snapshots/%d/" % self.s.id)

    def test_clear(self):
        self.s.clear()

    def test_public_snapshot(self):
        self.assertEqual(public_snapshot(), self.s)
