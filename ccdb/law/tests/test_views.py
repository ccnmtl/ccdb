import os

from django.conf import settings
from django.test import TestCase, override_settings
from ..models import Snapshot
from .factories import (
    ChargeFactory, SnapshotFactory, ClassificationFactory,
    AreaFactory, ConsequenceFactory, UserFactory,
)


class SimpleViewTest(TestCase):
    def setUp(self):
        self.s = SnapshotFactory()

    def tearDown(self):
        self.s.delete()

    def test_index(self):
        response = self.client.get("/")
        self.assertEquals(response.status_code, 200)

    def test_feedback(self):
        response = self.client.get("/feedback/")
        self.assertEquals(response.status_code, 200)

    def test_smoke(self):
        response = self.client.get("/smoketest/")
        self.assertEquals(response.status_code, 200)


class TestAutoComplete(TestCase):
    def test_empty(self):
        r = self.client.get("/autocomplete/?term=")
        self.assertEquals(r.status_code, 302)

    def test_real(self):
        self.s = SnapshotFactory()
        r = self.client.get("/autocomplete/?term=nothing")
        self.assertEquals(r.status_code, 200)
        self.assertEquals(r.content, '[]')


class TestViewCharge(TestCase):
    def test_one(self):
        s = SnapshotFactory()
        c = ChargeFactory(snapshot=s)
        r = self.client.get(c.get_absolute_url())
        self.assertEqual(r.status_code, 200)

    def test_two(self):
        s = SnapshotFactory()
        c = ChargeFactory(snapshot=s)
        c2 = ChargeFactory(snapshot=s)
        r = self.client.get(
            c.get_absolute_url() + "?charge2=" + c2.get_absolute_url())
        self.assertEqual(r.status_code, 200)


class TestViewChargeTips(TestCase):
    def test_one(self):
        s = SnapshotFactory()
        c = ChargeFactory(snapshot=s)
        r = self.client.get(c.get_absolute_url() + "tips/")
        self.assertEqual(r.status_code, 200)


class TestViewClassification(TestCase):
    def test_view_classification(self):
        s = SnapshotFactory()
        c = ClassificationFactory(snapshot=s)
        r = self.client.get(c.get_absolute_url())
        self.assertEqual(r.status_code, 200)


class TestViewArea(TestCase):
    def test_view_aread(self):
        s = SnapshotFactory()
        a = AreaFactory(snapshot=s)
        r = self.client.get(a.get_absolute_url())
        self.assertEqual(r.status_code, 200)


class TestViewConsequence(TestCase):
    def test_view_aread(self):
        s = SnapshotFactory()
        a = AreaFactory(snapshot=s)
        c = ConsequenceFactory(area=a)
        r = self.client.get(c.get_absolute_url())
        self.assertEqual(r.status_code, 200)


class LoggedInViewTests(TestCase):
    def setUp(self):
        self.u = UserFactory(is_staff=True)
        self.u.set_password('test')
        self.u.save()
        self.client.login(username=self.u.username, password='test')
        self.public_snapshot = SnapshotFactory()
        self.working_snapshot = SnapshotFactory(status="in progress")
        self.qa_snapshot = SnapshotFactory(status="qa")

    def test_edit_index(self):
        r = self.client.get("/edit/")
        self.assertEqual(r.status_code, 200)

    def test_graph(self):
        r = self.client.get("/edit/graph/")
        self.assertEqual(r.status_code, 200)

    def test_edit_snapshots(self):
        r = self.client.get("/edit/snapshots/")
        self.assertEqual(r.status_code, 200)

    def test_edit_snapshot(self):
        r = self.client.get("/edit/snapshots/{}/".format(
            self.working_snapshot.pk))
        self.assertEqual(r.status_code, 200)

    def test_clone_snapshot(self):
        snapshot_count = Snapshot.objects.all().count()
        r = self.client.post("/edit/snapshots/{}/clone/".format(
            self.working_snapshot.pk), data=dict(description='test'))
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Snapshot.objects.all().count(), snapshot_count + 1)

    @override_settings(MEDIA_ROOT="/tmp/")
    def test_approve_snapshot(self):
        # TODO: update app so this is easier to override
        try:
            os.makedirs(os.path.join(settings.MEDIA_ROOT, "dumps"))
        except OSError:
            pass
        snapshot_count = Snapshot.objects.all().count()
        r = self.client.post("/edit/snapshots/{}/approve/".format(
            self.qa_snapshot.pk))
        self.assertEqual(r.status_code, 302)

        # qa snapshot is now vetted
        self.qa_snapshot.refresh_from_db()
        self.assertEqual(self.qa_snapshot.status, "vetted")

        # and there's a new one to replace it
        self.assertEqual(Snapshot.objects.all().count(), snapshot_count + 1)

    def test_delete_snapshot(self):
        snapshot_count = Snapshot.objects.all().count()
        r = self.client.post("/edit/snapshots/{}/delete/".format(
            self.qa_snapshot.pk), data=dict(description='test'))
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Snapshot.objects.all().count(), snapshot_count - 1)

    def test_delete_working_snapshot(self):
        snapshot_count = Snapshot.objects.all().count()
        r = self.client.post("/edit/snapshots/{}/delete/".format(
            self.working_snapshot.pk), data=dict(description='test'))
        self.assertEqual(r.status_code, 302)
        # it automatically clones a replacement if you try to delete the
        # current working snapshot
        self.assertEqual(Snapshot.objects.all().count(), snapshot_count)
