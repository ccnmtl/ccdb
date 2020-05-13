# import os

# from django.conf import settings
from django.test import TestCase
# from django.test import override_settings
# from ccdb.law.models import (
#     Snapshot, ChargeClassification, Charge, ChargeArea,
#     Classification, ClassificationConsequence, Area,
#     Consequence,
# )
from ccdb.law.tests.factories import SnapshotFactory
# from ccdb.law.tests.factories import (
#     ChargeFactory, SnapshotFactory, ClassificationFactory,
#     AreaFactory, ConsequenceFactory, UserFactory,
# )


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
        self.assertEquals(response.status_code, 302)

    def test_smoke(self):
        response = self.client.get("/smoketest/")
        self.assertEquals(response.status_code, 200)


# class TestAutoComplete(TestCase):
#     def test_empty(self):
#         r = self.client.get("/autocomplete/?term=")
#         self.assertEquals(r.status_code, 302)
#
#     def test_real(self):
#         self.s = SnapshotFactory()
#         r = self.client.get("/autocomplete/?term=nothing")
#         self.assertEquals(r.status_code, 200)
#         self.assertEquals(r.content, b'[]')
#
#
# class TestViewCharge(TestCase):
#     def test_one(self):
#         s = SnapshotFactory()
#         c = ChargeFactory(snapshot=s)
#         r = self.client.get(c.get_absolute_url())
#         self.assertEqual(r.status_code, 200)
#
#     def test_two(self):
#         s = SnapshotFactory()
#         c = ChargeFactory(snapshot=s)
#         c2 = ChargeFactory(snapshot=s)
#         r = self.client.get(
#             c.get_absolute_url() + "?charge2=" + c2.get_absolute_url())
#         self.assertEqual(r.status_code, 200)
#
#
# class TestViewChargeTips(TestCase):
#     def test_one(self):
#         s = SnapshotFactory()
#         c = ChargeFactory(snapshot=s)
#         r = self.client.get(c.get_absolute_url() + "tips/")
#         self.assertEqual(r.status_code, 200)
#
#
# class TestViewClassification(TestCase):
#     def test_view_classification(self):
#         s = SnapshotFactory()
#         c = ClassificationFactory(snapshot=s)
#         r = self.client.get(c.get_absolute_url())
#         self.assertEqual(r.status_code, 200)
#
#
# class TestViewArea(TestCase):
#     def test_view_aread(self):
#         s = SnapshotFactory()
#         a = AreaFactory(snapshot=s)
#         r = self.client.get(a.get_absolute_url())
#         self.assertEqual(r.status_code, 200)
#
#
# class TestViewConsequence(TestCase):
#     def test_view_aread(self):
#         s = SnapshotFactory()
#         a = AreaFactory(snapshot=s)
#         c = ConsequenceFactory(area=a)
#         r = self.client.get(c.get_absolute_url())
#         self.assertEqual(r.status_code, 200)
#
#
# class LoggedInViewTests(TestCase):
#     def setUp(self):
#         self.u = UserFactory(is_staff=True)
#         self.u.set_password('test')
#         self.u.save()
#         self.client.login(username=self.u.username, password='test')
#         self.public_snapshot = SnapshotFactory()
#         self.working_snapshot = SnapshotFactory(status="in progress")
#         self.qa_snapshot = SnapshotFactory(status="qa")
#
#     def test_edit_index(self):
#         r = self.client.get("/edit/")
#         self.assertEqual(r.status_code, 200)
#
#     def test_graph(self):
#         r = self.client.get("/edit/graph/")
#         self.assertEqual(r.status_code, 200)
#
#     def test_edit_snapshots(self):
#         r = self.client.get("/edit/snapshots/")
#         self.assertEqual(r.status_code, 200)
#
#     def test_edit_snapshot(self):
#         r = self.client.get("/edit/snapshots/{}/".format(
#             self.working_snapshot.pk))
#         self.assertEqual(r.status_code, 200)
#
#     def test_clone_snapshot(self):
#         snapshot_count = Snapshot.objects.all().count()
#         r = self.client.post("/edit/snapshots/{}/clone/".format(
#             self.working_snapshot.pk), data=dict(description='test'))
#         self.assertEqual(r.status_code, 302)
#         self.assertEqual(Snapshot.objects.all().count(), snapshot_count + 1)
#
#     @override_settings(MEDIA_ROOT="/tmp/")  # nosec
#     def test_approve_snapshot(self):
#         # TODO: update app so this is easier to override
#         try:
#             os.makedirs(os.path.join(settings.MEDIA_ROOT, "dumps"))
#         except OSError:
#             pass
#         snapshot_count = Snapshot.objects.all().count()
#         r = self.client.post("/edit/snapshots/{}/approve/".format(
#             self.qa_snapshot.pk))
#         self.assertEqual(r.status_code, 302)
#
#         # qa snapshot is now vetted
#         self.qa_snapshot.refresh_from_db()
#         self.assertEqual(self.qa_snapshot.status, "vetted")
#
#         # and there's a new one to replace it
#         self.assertEqual(Snapshot.objects.all().count(), snapshot_count + 1)
#
#     def test_delete_snapshot(self):
#         snapshot_count = Snapshot.objects.all().count()
#         r = self.client.post("/edit/snapshots/{}/delete/".format(
#             self.qa_snapshot.pk), data=dict(description='test'))
#         self.assertEqual(r.status_code, 302)
#         self.assertEqual(Snapshot.objects.all().count(), snapshot_count - 1)
#
#     def test_delete_working_snapshot(self):
#         snapshot_count = Snapshot.objects.all().count()
#         r = self.client.post("/edit/snapshots/{}/delete/".format(
#             self.working_snapshot.pk), data=dict(description='test'))
#         self.assertEqual(r.status_code, 302)
#         # it automatically clones a replacement if you try to delete the
#         # current working snapshot
#         self.assertEqual(Snapshot.objects.all().count(), snapshot_count)
#
#     def test_edit_charge_index(self):
#         r = self.client.get("/edit/charge/")
#         self.assertEqual(r.status_code, 200)
#
#     def test_add_charge(self):
#         r = self.client.post(
#             "/edit/charge/add_charge/",
#             dict(penal_code='100.0', label='test')
#         )
#         # add a nested child to this one while we're in here
#         r = self.client.post(
#             "/edit/charge/1000-test/add_charge/",
#             dict(penal_code='100.1', label='test2')
#         )
#         self.assertEqual(r.status_code, 302)
#
#     def test_add_charge_classification(self):
#         c = ChargeFactory(snapshot=self.working_snapshot)
#         cs = ClassificationFactory(snapshot=self.working_snapshot)
#         r = self.client.post(
#             "/edit{}add_classification/".format(c.get_absolute_url()),
#             dict(classification_id=cs.id,
#                  certainty="yes"))
#         self.assertEqual(r.status_code, 302)
#         self.assertTrue(c.chargeclassification_set.count(), 1)
#
#         # repeating it should not create duplicates
#         r = self.client.post(
#             "/edit{}add_classification/".format(c.get_absolute_url()),
#             dict(classification_id=cs.id,
#                  certainty="yes"))
#         self.assertTrue(c.chargeclassification_set.count(), 1)
#
#     def test_remove_charge_classification_form(self):
#         c = ChargeFactory(snapshot=self.working_snapshot)
#         cs = ClassificationFactory(snapshot=self.working_snapshot)
#         ChargeClassification.objects.create(
#             charge=c, classification=cs, certainty="yes")
#
#         r = self.client.get(
#             "/edit{}remove_classification/{}/".format(c.get_absolute_url(),
#                                                       cs.id))
#         self.assertEqual(r.status_code, 200)
#
#     def test_remove_charge_classification(self):
#         c = ChargeFactory(snapshot=self.working_snapshot)
#         cs = ClassificationFactory(snapshot=self.working_snapshot)
#         ChargeClassification.objects.create(
#             charge=c, classification=cs, certainty="yes")
#
#         r = self.client.post(
#             "/edit{}remove_classification/{}/".format(c.get_absolute_url(),
#                                                       cs.id), dict())
#         self.assertEqual(r.status_code, 302)
#         self.assertEqual(c.chargeclassification_set.count(), 0)
#
#     def test_delete_charge(self):
#         c = ChargeFactory(snapshot=self.working_snapshot)
#         r = self.client.post("/edit{}delete/".format(c.get_absolute_url()),
#                              dict())
#         self.assertEqual(r.status_code, 302)
#         self.assertEqual(Charge.objects.all().count(), 0)
#
#     def test_edit_charge(self):
#         c = ChargeFactory(snapshot=self.working_snapshot)
#         r = self.client.post(
#             "/edit{}".format(c.get_absolute_url()),
#             dict(label="new label",
#                  penal_code=c.penal_code,
#                  name=c.name,
#                  description=c.description,))
#         self.assertEqual(r.status_code, 302)
#         c.refresh_from_db()
#         self.assertEqual(c.label, "new label")
#
#     def test_edit_charge_form(self):
#         c = ChargeFactory(snapshot=self.working_snapshot)
#         r = self.client.get(
#             "/edit{}".format(c.get_absolute_url()))
#         self.assertEqual(r.status_code, 200)
#
#     def test_add_charge_area(self):
#         c = ChargeFactory(snapshot=self.working_snapshot)
#         cs = AreaFactory(snapshot=self.working_snapshot)
#         r = self.client.post(
#             "/edit{}add_area/".format(c.get_absolute_url()),
#             dict(area_id=cs.id))
#         self.assertEqual(r.status_code, 302)
#         self.assertTrue(c.chargearea_set.count(), 1)
#
#     def test_remove_charge_area(self):
#         c = ChargeFactory(snapshot=self.working_snapshot)
#         cs = AreaFactory(snapshot=self.working_snapshot)
#         ChargeArea.objects.create(charge=c, area=cs)
#
#         r = self.client.post(
#             "/edit{}remove_area/{}/".format(c.get_absolute_url(),
#                                             cs.id), dict())
#         self.assertEqual(r.status_code, 302)
#         self.assertEqual(c.chargearea_set.count(), 0)
#
#     def test_reparent_charge(self):
#         c = ChargeFactory(snapshot=self.working_snapshot)
#         c2 = ChargeFactory(snapshot=self.working_snapshot)
#
#         r = self.client.post(
#             "/edit{}reparent/".format(c.get_absolute_url()),
#             dict(sibling_id=c2.id))
#         self.assertEqual(r.status_code, 302)
#         self.assertEqual(c.chargearea_set.count(), 0)
#
#     def test_edit_classification_index(self):
#         r = self.client.get("/edit/classification/")
#         self.assertEqual(r.status_code, 200)
#
#     def test_add_classification(self):
#         r = self.client.post(
#             "/edit/classification/add/",
#             dict(label='new classification', description='a description')
#         )
#         self.assertEqual(r.status_code, 302)
#         self.assertEqual(Classification.objects.count(), 1)
#
#     def test_edit_classification_form(self):
#         c = ClassificationFactory(snapshot=self.working_snapshot)
#
#         r = self.client.get("/edit{}".format(c.get_absolute_url()))
#         self.assertEqual(r.status_code, 200)
#
#     def test_edit_classification(self):
#         c = ClassificationFactory(snapshot=self.working_snapshot)
#
#         r = self.client.post(
#             "/edit{}".format(c.get_absolute_url()),
#             dict(label=c.label, name=c.name,
#                  description="new description")
#         )
#         self.assertEqual(r.status_code, 302)
#
#     def test_preview_classification(self):
#         c = ClassificationFactory(snapshot=self.working_snapshot)
#         r = self.client.get("/edit{}preview/".format(c.get_absolute_url()))
#         self.assertEqual(r.status_code, 200)
#
#     def test_delete_classification(self):
#         c = ClassificationFactory(snapshot=self.working_snapshot)
#         r = self.client.post("/edit{}delete/".format(c.get_absolute_url()))
#         self.assertEqual(r.status_code, 302)
#         self.assertEqual(Classification.objects.count(), 0)
#
#     def test_add_consequence_to_classification(self):
#         c = ClassificationFactory(snapshot=self.working_snapshot)
#         a = AreaFactory(snapshot=self.working_snapshot)
#         cq = ConsequenceFactory(area=a)
#         r = self.client.post(
#             "/edit{}add_consequence/".format(c.get_absolute_url()),
#             dict(consequence_id=cq.id),
#         )
#         self.assertEqual(r.status_code, 302)
#         self.assertEqual(ClassificationConsequence.objects.count(), 1)
#
#     def test_remove_consequence_from_classification(self):
#         c = ClassificationFactory(snapshot=self.working_snapshot)
#         a = AreaFactory(snapshot=self.working_snapshot)
#         cq = ConsequenceFactory(area=a)
#         ClassificationConsequence.objects.create(
#             consequence=cq, classification=c,
#             certainty='yes',
#         )
#         r = self.client.post(
#             "/edit{}remove_consequence/{}/".format(
#                 c.get_absolute_url(), cq.id),
#             dict(consequence_id=cq.id),
#         )
#         self.assertEqual(r.status_code, 302)
#         self.assertEqual(ClassificationConsequence.objects.count(), 0)
#
#     def test_edit_area_index(self):
#         r = self.client.get("/edit/area/")
#         self.assertEqual(r.status_code, 200)
#
#     def test_add_aread(self):
#         r = self.client.post("/edit/area/add/", dict(label='test area'))
#         self.assertEqual(r.status_code, 302)
#         self.assertEqual(Area.objects.count(), 1)
#
#     def test_edit_area_form(self):
#         a = AreaFactory(snapshot=self.working_snapshot)
#         r = self.client.get("/edit{}".format(a.get_absolute_url()))
#         self.assertEqual(r.status_code, 200)
#
#     def test_edit_area(self):
#         a = AreaFactory(snapshot=self.working_snapshot)
#         r = self.client.post(
#             "/edit{}".format(a.get_absolute_url()),
#             dict(label=a.label, name=a.name)
#         )
#         self.assertEqual(r.status_code, 302)
#
#     def test_delete_area(self):
#         a = AreaFactory(snapshot=self.working_snapshot)
#         r = self.client.post(
#             "/edit{}delete/".format(a.get_absolute_url()),
#         )
#         self.assertEqual(r.status_code, 302)
#         self.assertEqual(Area.objects.count(), 0)
#
#     def test_add_consequence(self):
#         a = AreaFactory(snapshot=self.working_snapshot)
#         r = self.client.post(
#             "/edit{}add_consequence/".format(a.get_absolute_url()),
#             dict(label='new consequence', description='a description')
#         )
#         self.assertEqual(r.status_code, 302)
#         self.assertEqual(Consequence.objects.count(), 1)
#
#     def test_edit_consequence_form(self):
#         a = AreaFactory(snapshot=self.working_snapshot)
#         c = ConsequenceFactory(area=a)
#         r = self.client.get("/edit{}".format(c.get_absolute_url()))
#         self.assertEqual(r.status_code, 200)
#
#     def test_edit_consequence(self):
#         a = AreaFactory(snapshot=self.working_snapshot)
#         c = ConsequenceFactory(area=a)
#         r = self.client.post(
#             "/edit{}".format(c.get_absolute_url()),
#             dict(label=c.label, name=c.name, description="new description")
#         )
#         self.assertEqual(r.status_code, 302)
#
#     def test_delete_consequence(self):
#         a = AreaFactory(snapshot=self.working_snapshot)
#         c = ConsequenceFactory(area=a)
#         r = self.client.post(
#             "/edit{}delete/".format(c.get_absolute_url())
#         )
#         self.assertEqual(r.status_code, 302)
#         self.assertEqual(Consequence.objects.count(), 0)
#
#     def test_add_classification_to_consequence(self):
#         a = AreaFactory(snapshot=self.working_snapshot)
#         c = ConsequenceFactory(area=a)
#         cl = ClassificationFactory(snapshot=self.working_snapshot)
#         r = self.client.post(
#             "/edit{}add_classification/".format(c.get_absolute_url()),
#             dict(classification_id=cl.id)
#         )
#         self.assertEqual(r.status_code, 302)
#         self.assertEqual(ClassificationConsequence.objects.count(), 1)
