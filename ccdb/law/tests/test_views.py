from django.test import TestCase
from .factories import (
    ChargeFactory, SnapshotFactory, ClassificationFactory,
    AreaFactory, ConsequenceFactory,
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
