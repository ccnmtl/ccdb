from django.test import TestCase
from django.test.client import Client
from ccdb.law.models import Snapshot


class SimpleViewTest(TestCase):
    def setUp(self):
        self.s = Snapshot.objects.create(
            label="test snapshot",
            status="vetted")
        self.c = Client()

    def tearDown(self):
        self.s.delete()

    def test_index(self):
        response = self.c.get("/")
        self.assertEquals(response.status_code, 200)

    def test_smoke(self):
        response = self.c.get("/smoketest/")
        self.assertEquals(response.status_code, 200)
