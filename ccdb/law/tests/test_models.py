from ccdb.law.models import Snapshot, public_snapshot
from ccdb.law.models import effective_certainty, cluster_by, dtolist
from ccdb.law.models import Area, Consequence
from ccdb.law.models import Classification
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


class TestClusterBy(TestCase):
    def test_basics(self):
        alist = [1, 2, 3]
        f = lambda x: x + 4
        self.assertEquals(
            cluster_by(f, alist),
            {5: [1], 6: [2], 7: [3]})

        alist = [1, 2, 3, 1]
        self.assertEquals(
            cluster_by(f, alist),
            {5: [1, 1], 6: [2], 7: [3]})


class TestDToList(TestCase):
    def test_basics(self):
        self.assertEquals(
            dtolist({'foo': 'bar'}),
            [{'classification': 'foo', 'consequences': 'bar'}]
        )


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
        self.cons.add_classification_form()

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


class TestClassification(TestCase):
    def setUp(self):
        self.s = Snapshot.objects.create(
            label="test snapshot",
            status="vetted")
        self.c = Classification.objects.create(
            snapshot=self.s,
            label="Test Classification",
            name="test",
        )

    def tearDown(self):
        self.c.delete()
        self.s.delete()

    def test_unicode(self):
        self.assertEquals(str(self.c), "Test Classification")

    def test_display_label(self):
        self.assertEquals(
            self.c.display_label(),
            "Test Classification"
        )
        self.c.label = "Test Classification [foo]"
        self.c.save()
        self.assertEquals(
            self.c.display_label(),
            "Test Classification"
        )
        self.c.label = "Test Classification"
        self.c.save()

    def test_get_absolute_url(self):
        self.assertEquals(
            self.c.get_absolute_url(),
            "/classification/test/"
        )

    def test_json(self):
        json = self.c.to_json()
        self.assertEquals(json['label'], self.c.label)
        self.assertEquals(json['slug'], self.c.name)
        self.assertEquals(json['description'], self.c.description)

    def test_clone_to(self):
        new_snapshot = Snapshot.objects.create(
            label="New Snapshot",
            status="in progress")
        na = self.c.clone_to(new_snapshot)
        self.assertEquals(na.label, self.c.label)
        self.assertEquals(na.name, self.c.name)
        na.delete()
        new_snapshot.delete()

    def test_yes(self):
        self.assertEquals(self.c.yes().count(), 0)

    def test_probably(self):
        self.assertEquals(self.c.probably().count(), 0)

    def test_maybe(self):
        self.assertEquals(self.c.maybe().count(), 0)

    def test_no(self):
        self.assertEquals(len(self.c.no()), 0)

    def test_all_charges(self):
        self.assertEquals(self.c.all_charges(), [])

    def test_consequences(self):
        self.assertEquals(self.c.consequences(), [])

    def test_add_consequence_form(self):
        self.c.add_consequence_form()

    def test_yes_consequences(self):
        self.assertEquals(self.c.yes_consequences().count(), 0)

    def test_probably_consequences(self):
        self.assertEquals(self.c.probably_consequences().count(), 0)

    def test_maybe_consequences(self):
        self.assertEquals(self.c.maybe_consequences().count(), 0)

    def test_all_probably_consequences(self):
        self.assertEquals(self.c.all_probably_consequences(), [])

    def test_all_maybe_consequences(self):
        self.assertEquals(self.c.all_maybe_consequences(), [])

    def test_all_consequences(self):
        self.assertEquals(self.c.all_consequences(), [])

    def test_no_consequences(self):
        self.assertEquals(self.c.no_consequences(), [])

    def test_in_areas(self):
        self.assertTrue(self.c.in_areas([]))
