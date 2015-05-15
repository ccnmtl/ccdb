from .factories import (
    SnapshotFactory, AreaFactory, ConsequenceFactory,
    ClassificationFactory, UserFactory, ChargeFactory,
    ChargeChildrenFactory,
)
from ccdb.law.models import public_snapshot, working_snapshot
from ccdb.law.models import effective_certainty, cluster_by, dtolist
from django.test import TestCase


class SnapshotModelTest(TestCase):
    def test_unicode(self):
        s = SnapshotFactory()
        self.assertTrue(unicode(s).startswith("test snapshot"))

    def test_dump_filename_base(self):
        s = SnapshotFactory()
        assert "T" in s.dump_filename_base()

    def test_to_json(self):
        s = SnapshotFactory()
        self.assertEqual(s.to_json()['label'], s.label)

    def test_is_most_recent_vetted(self):
        s = SnapshotFactory()
        self.assertTrue(s.is_most_recent_vetted())

    def test_is_current_working(self):
        s = SnapshotFactory()
        self.assertFalse(s.is_current_working())

    def test_cloneable(self):
        s = SnapshotFactory()
        self.assertTrue(s.cloneable())

    def test_get_absolute_url(self):
        s = SnapshotFactory()
        self.assertEquals(s.get_absolute_url(),
                          "/snapshots/%d/" % s.id)

    def test_clear(self):
        s = SnapshotFactory()
        s.clear()

    def test_public_snapshot(self):
        s = SnapshotFactory()
        self.assertEqual(public_snapshot(), s)

    def test_working_snapshot(self):
        self.assertIsNone(working_snapshot())
        SnapshotFactory()
        self.assertIsNone(working_snapshot())
        s2 = SnapshotFactory(status='in progress')
        self.assertEqual(working_snapshot(), s2)

    def test_clone(self):
        u = UserFactory()
        s = SnapshotFactory()
        new_snapshot = s.clone(label="test clone", user=u)
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
    def test_get_absolute_url(self):
        a = AreaFactory()
        self.assertEquals(
            a.get_absolute_url(), "/area/test/",
        )

    def test_to_json(self):
        a = AreaFactory()
        json = a.to_json()
        self.assertEquals(json['label'], a.label)
        self.assertEquals(json['slug'], a.name)
        self.assertEquals(json['id'], a.id)

    def test_clone_to(self):
        a = AreaFactory()
        new_snapshot = SnapshotFactory(
            label="New Snapshot",
            status="in progress")
        na = a.clone_to(new_snapshot)
        self.assertEquals(na.label, a.label)
        self.assertEquals(na.name, a.name)


class TestConsequence(TestCase):
    def test_unicode(self):
        cons = ConsequenceFactory()
        self.assertEquals(str(cons), cons.label)

    def test_display_label(self):
        cons = ConsequenceFactory()
        self.assertEquals(cons.display_label(), cons.label)
        cons.label = "Test Consequence [foo]"
        cons.save()
        self.assertEquals(cons.display_label(), "Test Consequence")

    def test_to_json(self):
        cons = ConsequenceFactory()
        json = cons.to_json()
        self.assertEquals(json['label'], cons.label)
        self.assertEquals(json['slug'], cons.name)
        self.assertEquals(json['description'], cons.description)

    def test_get_absolute_url(self):
        cons = ConsequenceFactory()
        self.assertEquals(cons.get_absolute_url(), "/area/test/test/")

    def test_no(self):
        cons = ConsequenceFactory()
        self.assertEquals(cons.no(), [])

    def test_add_classification_form(self):
        cons = ConsequenceFactory()
        cons.add_classification_form()

    def test_clone_to(self):
        cons = ConsequenceFactory()
        new_area = AreaFactory(
            label="New Area",
            name="new",
            snapshot=cons.area.snapshot)
        c = cons.clone_to(new_area)
        self.assertEquals(c.label, cons.label)
        self.assertEquals(c.name, cons.name)

    def test_clone_snapshot(self):
        u = UserFactory()
        cons = ConsequenceFactory()
        new_snapshot = cons.area.snapshot.clone(label="test clone", user=u)
        self.assertEqual(new_snapshot.label, "test clone")


class TestClassification(TestCase):
    def test_unicode(self):
        c = ClassificationFactory()
        self.assertEquals(str(c), c.label)

    def test_display_label(self):
        c = ClassificationFactory()
        self.assertEquals(c.display_label(), c.label)
        c.label = "Test Classification [foo]"
        self.assertEquals(
            c.display_label(),
            "Test Classification"
        )

    def test_get_absolute_url(self):
        c = ClassificationFactory()
        self.assertEquals(
            c.get_absolute_url(),
            "/classification/test/"
        )

    def test_json(self):
        c = ClassificationFactory()
        json = c.to_json()
        self.assertEquals(json['label'], c.label)
        self.assertEquals(json['slug'], c.name)
        self.assertEquals(json['description'], c.description)

    def test_clone_to(self):
        c = ClassificationFactory()
        new_snapshot = SnapshotFactory(
            label="New Snapshot",
            status="in progress")
        na = c.clone_to(new_snapshot)
        self.assertEquals(na.label, c.label)
        self.assertEquals(na.name, c.name)

    def test_clone_snapshot(self):
        c = ClassificationFactory()
        u = UserFactory()
        new_snapshot = c.snapshot.clone(label="test clone", user=u)
        self.assertEqual(new_snapshot.label, "test clone")

    def test_yes(self):
        c = ClassificationFactory()
        self.assertEquals(c.yes().count(), 0)

    def test_probably(self):
        c = ClassificationFactory()
        self.assertEquals(c.probably().count(), 0)

    def test_maybe(self):
        c = ClassificationFactory()
        self.assertEquals(c.maybe().count(), 0)

    def test_no(self):
        c = ClassificationFactory()
        self.assertEquals(len(c.no()), 0)

    def test_all_charges(self):
        c = ClassificationFactory()
        self.assertEquals(c.all_charges(), [])

    def test_consequences(self):
        c = ClassificationFactory()
        self.assertEquals(c.consequences(), [])

    def test_add_consequence_form(self):
        c = ClassificationFactory()
        c.add_consequence_form()

    def test_yes_consequences(self):
        c = ClassificationFactory()
        self.assertEquals(c.yes_consequences().count(), 0)

    def test_probably_consequences(self):
        c = ClassificationFactory()
        self.assertEquals(c.probably_consequences().count(), 0)

    def test_maybe_consequences(self):
        c = ClassificationFactory()
        self.assertEquals(c.maybe_consequences().count(), 0)

    def test_all_probably_consequences(self):
        c = ClassificationFactory()
        self.assertEquals(c.all_probably_consequences(), [])

    def test_all_maybe_consequences(self):
        c = ClassificationFactory()
        self.assertEquals(c.all_maybe_consequences(), [])

    def test_all_consequences(self):
        c = ClassificationFactory()
        self.assertEquals(c.all_consequences(), [])

    def test_no_consequences(self):
        c = ClassificationFactory()
        self.assertEquals(c.no_consequences(), [])

    def test_in_areas(self):
        c = ClassificationFactory()
        self.assertTrue(c.in_areas([]))


class TestCharge(TestCase):
    def test_unicode(self):
        c = ChargeFactory()
        self.assertEquals(str(c), c.label)

    def test_get_absolute_url(self):
        c = ChargeFactory()
        self.assertTrue(
            c.get_absolute_url().startswith("/charge/127-0"))
        cc = ChargeChildrenFactory()
        self.assertEquals(
            cc.child.get_absolute_url(),
            cc.parent.get_absolute_url() + cc.child.name + "/")

        self.assertEquals(c.snapshot.get_charge_by_slugs([c.name]), c)
        self.assertEquals(
            cc.parent.snapshot.get_charge_by_slugs(
                [cc.parent.name, cc.child.name]),
            cc.child)

    def test_to_json(self):
        c = ChargeFactory()
        json = c.to_json()
        self.assertEquals(json['label'], c.label)
        self.assertEquals(json['penal_code'], c.penal_code)
        self.assertEquals(json['slug'], c.name)
        self.assertEquals(json['numeric_penal_code'],
                          c.numeric_penal_code)
        self.assertEquals(json['description'], c.description)

    def test_get_description(self):
        c = ChargeFactory()
        self.assertEquals(c.get_description(), c.description)
        cc = ChargeChildrenFactory()
        cc.child.description = ""
        self.assertEquals(cc.child.get_description(), cc.parent.description)

    def test_clone_to(self):
        c = ChargeFactory()
        new_snapshot = SnapshotFactory(
            label="New Snapshot",
            status="in progress")
        na = c.clone_to(new_snapshot)
        self.assertEquals(na.label, c.label)
        self.assertEquals(na.name, c.name)

    def test_clone_snapshot(self):
        u = UserFactory()
        c = ChargeFactory()
        new_snapshot = c.snapshot.clone(label="test clone", user=u)
        self.assertEqual(new_snapshot.label, "test clone")

    def test_children(self):
        c = ChargeFactory()
        self.assertEquals(c.children(), [])
        cc = ChargeChildrenFactory()
        self.assertEquals(cc.parent.children(), [cc.child])

    def test_has_children(self):
        c = ChargeFactory()
        self.assertFalse(c.has_children())
        cc = ChargeChildrenFactory()
        self.assertFalse(cc.child.has_children())
        self.assertTrue(cc.parent.has_children())

    def test_has_parents(self):
        c = ChargeFactory()
        self.assertFalse(c.has_parents())
        cc = ChargeChildrenFactory()
        self.assertFalse(cc.parent.has_parents())
        self.assertTrue(cc.child.has_parents())

    def test_is_leaf(self):
        c = ChargeFactory()
        self.assertTrue(c.is_leaf())
        cc = ChargeChildrenFactory()
        self.assertTrue(cc.child.is_leaf())
        self.assertFalse(cc.parent.is_leaf())

    def test_as_ul(self):
        c = ChargeFactory()
        ul = c.as_ul()
        self.assertTrue(
            '<li class="menuitem leaf">' in ul)
        self.assertTrue(
            '<span class="charge"' in ul)
        self.assertTrue(
            c.get_absolute_url() in ul)
        ul = c.as_ul(hs=False)
        self.assertTrue(
            '<li class="menuitem leaf">' in ul)
        self.assertTrue(
            '<span class="charge"' in ul)
        self.assertTrue(
            c.get_absolute_url() in ul)
        cc = ChargeChildrenFactory()
        ul = cc.parent.as_ul()
        self.assertTrue(
            '<li class="menuitem leaf">' in ul)
        self.assertTrue(
            '<span class="charge"' in ul)
        self.assertTrue(
            cc.parent.get_absolute_url() in ul)
        ul = cc.parent.as_ul(hs=False)
        self.assertTrue(
            '<li class="menuitem leaf">' in ul)
        self.assertTrue(
            '<span class="charge"' in ul)
        self.assertTrue(
            cc.parent.get_absolute_url() in ul)

    def test_as_view_ul(self):
        c = ChargeFactory()
        self.assertEqual(c.as_ul(), c.as_view_ul())

    def test_as_edit_ul(self):
        c = ChargeFactory()
        ul = c.as_edit_ul()
        self.assertTrue(
            '<li class="menuitem leaf">' in ul)
        self.assertTrue(
            '<span class="charge"' in ul)

    def test_as_compare_ul(self):
        c = ChargeFactory()
        ul = c.as_compare_ul()
        self.assertTrue(
            '<li class="menuitem"><span class="compare" '
            in ul)
        self.assertTrue(
            'href="?charge2=' + c.get_absolute_url()
            in ul)

        cc = ChargeChildrenFactory()
        ul = cc.parent.as_compare_ul()
        self.assertTrue(
            '<li class="menuitem"><span class="compare" '
            in ul)
        self.assertTrue(
            'href="?charge2=' + cc.parent.get_absolute_url()
            in ul)

    def test_as_view_compare_ul(self):
        c = ChargeFactory()
        self.assertEqual(c.as_compare_ul(),
                         c.as_view_compare_ul())
        cc = ChargeChildrenFactory()
        self.assertEqual(cc.parent.as_compare_ul(),
                         cc.parent.as_view_compare_ul())

    def test_rparents(self):
        c = ChargeFactory()
        self.assertEqual(c.rparents(), [])
        cc = ChargeChildrenFactory()
        self.assertEqual(cc.child.rparents(), [cc.parent])

    def test_siblings(self):
        c = ChargeFactory()
        self.assertEqual(c.siblings(), [])

    def test_add_classification_form(self):
        c = ChargeFactory()
        c.add_classification_form()

    def test_yes(self):
        c = ChargeFactory()
        self.assertEqual(c.yes(), [])

    def test_probably(self):
        c = ChargeFactory()
        self.assertEqual(c.probably(), [])

    def test_maybe(self):
        c = ChargeFactory()
        self.assertEqual(c.maybe(), [])

    def test_all_yes(self):
        c = ChargeFactory()
        self.assertEqual(c.all_yes(), [])

    def test_all_probably(self):
        c = ChargeFactory()
        self.assertEqual(c.all_probably(), [])

    def test_all_maybe(self):
        c = ChargeFactory()
        self.assertEqual(c.all_maybe(), [])

    def test_view_yes(self):
        c = ChargeFactory()
        self.assertEqual(c.view_yes(), [])

    def test_view_probably(self):
        c = ChargeFactory()
        self.assertEqual(c.view_probably(), [])

    def test_view_maybe(self):
        c = ChargeFactory()
        self.assertEqual(c.view_maybe(), [])

    def test_view_all(self):
        c = ChargeFactory()
        self.assertEqual(c.view_all(), [])

    def test_no(self):
        c = ChargeFactory()
        self.assertEqual(c.no(), [])

    def test_add_area_form(self):
        c = ChargeFactory()
        c.add_area_form()

    def test_yes_areas(self):
        c = ChargeFactory()
        self.assertEqual(c.yes_areas(), [])

    def test_no_areas(self):
        c = ChargeFactory()
        self.assertEqual(c.no_areas(), [])

    def test_yes_areas_for_edit_page(self):
        c = ChargeFactory()
        self.assertEqual(c.yes_areas_for_edit_page(), [])

    def test_all_consequences_by_area(self):
        c = ChargeFactory()
        self.assertEqual(c.all_consequences_by_area(), [])

    def test_all_consequences_by_area_json(self):
        c = ChargeFactory()
        self.assertEqual(c.all_consequences_by_area_json(), [])

    def test_gather_all_consequences(self):
        c = ChargeFactory()
        self.assertEqual(c.gather_all_consequences(), [])
