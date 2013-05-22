from ccdb.law.models import Snapshot, public_snapshot
from ccdb.law.models import effective_certainty
from ccdb.law.models import Area, Consequence
from django.test import TestCase
from django.contrib.auth.models import User


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

    def test_clone(self):
        u = User.objects.create(username="testuser")
        new_snapshot = self.s.clone(label="test clone", user=u)
        self.assertEqual(new_snapshot.label, "test clone")
        new_snapshot.delete()


class TestEffectiveCertainty(TestCase):
    def test_basics(self):
        self.assertEquals(effective_certainty("yes", "yes"), "yes")
        self.assertEquals(effective_certainty("yes", "maybe"), "maybe")
        self.assertEquals(effective_certainty("yes", "probably"), "probably")

        self.assertEquals(effective_certainty("probably", "yes"), "probably")
        self.assertEquals(effective_certainty("probably", "maybe"), "maybe")
        self.assertEquals(effective_certainty("probably", "probably"),
                          "probably")

        self.assertEquals(effective_certainty("maybe", "yes"), "maybe")
        self.assertEquals(effective_certainty("maybe", "maybe"), "maybe")
        self.assertEquals(effective_certainty("maybe", "probably"), "maybe")


class TestArea(TestCase):
    def setUp(self):
        self.s = Snapshot.objects.create(
            label="test snapshot",
            status="vetted")
        self.a = Area.objects.create(
            label="Test Area",
            name="test",
            snapshot=self.s)

    def tearDown(self):
        self.a.delete()
        self.s.delete()

    def test_unicode(self):
        self.assertEquals(str(self.a), "Test Area")

    def test_get_absolute_url(self):
        self.assertEquals(
            self.a.get_absolute_url(), "/area/test/",
        )

    def test_to_json(self):
        json = self.a.to_json()
        self.assertEquals(json['label'], self.a.label)
        self.assertEquals(json['slug'], self.a.name)
        self.assertEquals(json['id'], self.a.id)

    def test_clone_to(self):
        new_snapshot = Snapshot.objects.create(
            label="New Snapshot",
            status="in progress")
        na = self.a.clone_to(new_snapshot)
        self.assertEquals(na.label, self.a.label)
        self.assertEquals(na.name, self.a.name)
        na.delete()
        new_snapshot.delete()


class TestConsequence(TestCase):
    def setUp(self):
        self.s = Snapshot.objects.create(
            label="test snapshot",
            status="vetted")
        self.a = Area.objects.create(
            label="Test Area",
            name="test",
            snapshot=self.s)
        self.cons = Consequence.objects.create(
            label="Test Consequence",
            area=self.a,
            name="test",
        )

    def tearDown(self):
        self.cons.delete()
        self.a.delete()
        self.s.delete()

    def test_unicode(self):
        self.assertEquals(str(self.cons), "Test Consequence")

    def test_display_label(self):
        self.assertEquals(self.cons.display_label(), "Test Consequence")
        self.cons.label = "Test Consequence [foo]"
        self.cons.save()
        self.assertEquals(self.cons.display_label(), "Test Consequence")
        self.cons.label = "Test Consequence"
        self.cons.save()

    def test_to_json(self):
        json = self.cons.to_json()
        self.assertEquals(json['label'], self.cons.label)
        self.assertEquals(json['slug'], self.cons.name)
        self.assertEquals(json['description'], self.cons.description)

    def test_get_absolute_url(self):
        self.assertEquals(self.cons.get_absolute_url(), "/area/test/test/")

    def test_no(self):
        self.assertEquals(self.cons.no(), [])

    def test_add_classification_form(self):
        f = self.cons.add_classification_form()

    def test_clone_to(self):
        new_area = Area.objects.create(
            label="New Area",
            name="new",
            snapshot=self.s)
        c = self.cons.clone_to(new_area)
        self.assertEquals(c.label, self.cons.label)
        self.assertEquals(c.name, self.cons.name)
        c.delete()
        new_area.delete()
