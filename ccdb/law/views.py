from ccdb.law.models import Snapshot, public_snapshot, working_snapshot
from ccdb.law.models import Charge, Classification, Area, ChargeChildren
from ccdb.law.models import ChargeClassification, ChargeArea, Consequence
from ccdb.law.models import ClassificationConsequence
from ccdb.law.forms import AddChargeForm, EditChargeForm, AddClassificationForm
from ccdb.law.forms import EditClassificationForm, AddAreaForm, EditAreaForm
from ccdb.law.forms import AddConsequenceForm, EditConsequenceForm
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.shortcuts import render_to_response, get_object_or_404, render
from datetime import datetime
from django.template.defaultfilters import slugify
from django.utils.decorators import method_decorator
from django.views.generic.base import TemplateView, View
from django.views.generic.detail import DetailView
from json import dumps
from django.core.mail import send_mail
from zipfile import ZipFile, ZIP_DEFLATED
from django.conf import settings
import os.path
import requests


class IndexView(TemplateView):
    template_name = 'law/index.html'

    def get_context_data(self, **kwargs):
        snapshot = public_snapshot()
        return dict(charges=snapshot.top_level_charges())


class FeedbackView(View):
    def post(self, request):
        if request.POST.get('email', '') == '':
            return dict()
        if "Role:" not in request.POST.get("description", ""):
            # we know that the javascript was bypassed, so ignore it
            return dict()
        requests.post(settings.PMT_EXTERNAL_ADD_ITEM_URL,
                      dict(pid=request.POST['pid'],
                           mid=request.POST['mid'],
                           description=request.POST['description']))

        body = """%s\n\nFrom %s (%s)""" % (request.POST.get('description', ''),
                                           request.POST.get('name'),
                                           request.POST.get('email'))
        send_mail(
            'Collateral Consequences Web Feedback', body,
            settings.SERVER_EMAIL,
            [settings.SERVER_EMAIL], fail_silently=False)
        return HttpResponseRedirect("/thanks/")

    def get(self, request):
        return render(request, 'law/feedback.html', dict())


class StaffMixin(object):
    @method_decorator(login_required)
    @method_decorator(user_passes_test(lambda u: u.is_staff))
    def dispatch(self, *args, **kwargs):
        return super(StaffMixin, self).dispatch(*args, **kwargs)


class WorkingSnapshotMixin(object):
    def snapshot(self):
        return working_snapshot()


class PublicSnapshotMixin(object):
    def snapshot(self):
        return public_snapshot()


class ChargeLocatorMixin(object):
    def get_charge_by_slugs(self, slugs):
        return self.snapshot().get_charge_by_slugs(slugs)

    def charge(self, slugs):
        if slugs[-1] == "/":
            slugs = slugs[:-1]
        slugs = slugs.split("/")
        return self.get_charge_by_slugs(slugs)


class ClassificationLocatorMixin(object):
    def classification(self, slug):
        return get_object_or_404(
            Classification, snapshot=self.snapshot(), name=slug)


class AreaLocatorMixin(object):
    def area(self, slug):
        return get_object_or_404(Area, snapshot=self.snapshot(), name=slug)


class ConsequenceLocatorMixin(object):
    def consequence(self, area, cslug):
        return get_object_or_404(Consequence, area=area, name=cslug)


class EditView(StaffMixin, TemplateView):
    template_name = 'law/edit_index.html'

    def get_context_data(self, *args, **kwargs):
        return dict(snapshots=Snapshot.objects.all(),
                    working_snapshot=working_snapshot(),
                    public_snapshot=public_snapshot())


class EditSnapshotsView(StaffMixin, TemplateView):
    template_name = 'law/edit_snapshots_index.html'

    def get_context_data(self, *args, **kwargs):
        return dict(snapshots=Snapshot.objects.all().order_by("-created"))


class EditSnapshotView(StaffMixin, DetailView):
    template_name = 'law/edit_snapshot.html'
    model = Snapshot
    context_object_name = 'snapshot'


class CloneSnapshotView(StaffMixin, View):
    def post(self, request, id):
        snapshot = get_object_or_404(Snapshot, id=id)
        snapshot.clone(label=request.POST.get('label', 'new snapshot'),
                       user=request.user,
                       description=request.POST.get('description', ''))
        return HttpResponseRedirect("/edit/")


class ApproveSnapshotView(StaffMixin, View):
    def post(self, request, id):
        snapshot = get_object_or_404(Snapshot, id=id)
        snapshot.status = 'vetted'
        snapshot.save()

        snapshot.add_event(user=request.user,
                           description="snapshot approved for production")
        # clone it to make a new working snapshot
        n = datetime.now()
        snapshot.clone(label="%04d-%02d-%02d %02d:%02d" % (
            n.year, n.month, n.day, n.hour, n.minute),
                       user=request.user,
                       description="")

        # make a static dump of the vetted one
        data = dict()
        data['snapshot'] = snapshot.to_json()
        json = dumps(data)
        media_dir = settings.MEDIA_ROOT
        filename_base = snapshot.dump_filename_base()
        json_full_path = os.path.join(media_dir, "dumps",
                                      filename_base + ".json")
        zip_full_path = os.path.join(media_dir, "dumps",
                                     filename_base + ".zip")
        with open(json_full_path, "w") as jsonfile:
            jsonfile.write(json)

        zipfile = ZipFile(zip_full_path, "w", ZIP_DEFLATED)
        zipfile.writestr("snapshot.json", json)
        zipfile.close()

        return HttpResponseRedirect("/edit/snapshots/")


class DeleteSnapshotView(StaffMixin, View):
    model = Snapshot
    success_url = "/edit/snapshots/"

    def post(self, request, pk):
        snapshot = get_object_or_404(self.model, pk=pk)
        if snapshot.is_current_working():
            # create new working snapshot to replace it
            # cloning the public snapshot
            n = datetime.now()
            snapshot.clone(label="%04d-%02d-%02d %02d:%02d" % (n.year, n.month,
                                                               n.day, n.hour,
                                                               n.minute),
                           user=request.user,
                           description="")
        else:
            # there's actually nothing to do here,
            # but keep in mind that if this was the current public
            # snapshot, when it gets deleted, the previous
            # vetted snapshot takes its place automatically.
            pass

        snapshot.delete()
        return HttpResponseRedirect(self.success_url)


class GraphView(PublicSnapshotMixin, TemplateView):
    template_name = 'law/graph.html'

    def get_context_data(self, *args, **kwargs):
        return dict(
            snapshot=self.snapshot(),
            charges=self.snapshot().top_level_charges(),
            all_charges=Charge.objects.filter(
                snapshot=self.snapshot()).order_by(
                    "numeric_penal_code", "penal_code", "label"),
            all_classifications=Classification.objects.filter(
                snapshot=self.snapshot()),
            all_areas=Area.objects.filter(snapshot=self.snapshot()))


def api_current(request):
    snapshot = public_snapshot()
    data = dict()
    filename_base = snapshot.dump_filename_base()
    data['json_url'] = settings.MEDIA_URL + "dumps/" + filename_base + ".json"
    data['zip_url'] = settings.MEDIA_URL + "dumps/" + filename_base + ".zip"
    json = dumps(data)
    return HttpResponse(json, content_type="application/json")


class EditChargesView(StaffMixin, WorkingSnapshotMixin, TemplateView):
    template_name = 'law/edit_charge_index.html'

    def get_context_data(self, *args, **kwargs):
        return dict(working_snapshot=self.snapshot(),
                    charges=self.snapshot().top_level_charges(),
                    add_charge_form=AddChargeForm())


class AddChargeView(StaffMixin, WorkingSnapshotMixin,
                    ChargeLocatorMixin, View):
    def post(self, request, slugs=""):
        if slugs != "" and slugs[-1] == "/":
            slugs = slugs[:-1]
        AddChargeForm(request.POST)
        slug = slugify(request.POST['penal_code'] + " " +
                       request.POST['label'])[:50]
        # need to check for duplicate slugs and fix
        ct = Charge.objects.filter(name=slug)
        if ct.count() > 0:
            # uh oh. there's already a charge with that slug
            # need to come up with a relatively unique new one
            # this is the most reasonable approach I can think of
            slug = slug[:-3] + "%03d" % (Charge.objects.count() % 1000)
            # any better ideas?

        c = Charge.objects.create(snapshot=self.snapshot(),
                                  label=request.POST['label'],
                                  penal_code=request.POST['penal_code'],
                                  name=slug)
        slugs = slugs.split("/")
        description = "charge %s added" % str(c)
        if len(slugs) > 0 and slugs != ['']:
            parent = self.get_charge_by_slugs(slugs)
            ChargeChildren.objects.create(parent=parent, child=c)
            description = "charge **%s** added as child of **%s**" % (
                str(c), str(parent))
        self.snapshot().add_event(user=request.user,
                                  description=description)
        if len(slugs) > 0 and slugs != ['']:
            parent = self.get_charge_by_slugs(slugs)
            return HttpResponseRedirect("/edit" + parent.get_absolute_url())
        else:
            return HttpResponseRedirect("/edit/charge/")


class AddChargeClassificationView(StaffMixin, WorkingSnapshotMixin,
                                  ChargeLocatorMixin, View):
    def post(self, request, slugs=""):
        charge = self.charge(slugs)

        classification = get_object_or_404(
            Classification, id=request.POST['classification_id'])
        if ChargeClassification.objects.filter(
                charge=charge, classification=classification).count() == 0:
            # only create if one doesn't already exist.
            # TODO: notify user
            cc = ChargeClassification.objects.create(
                charge=charge, classification=classification,
                certainty=request.POST['certainty'])
            self.snapshot().add_event(
                user=request.user,
                description=("charge **%s** classified as (%s) **%s**" %
                             (cc.charge.label, cc.certainty,
                              cc.classification.label)),
                note=request.POST.get('comment', ''))
        return HttpResponseRedirect("/edit" + charge.get_absolute_url())


class AddAreaToChargeView(StaffMixin, WorkingSnapshotMixin,
                          ChargeLocatorMixin, View):
    def post(self, request, slugs=""):
        charge = self.charge(slugs)
        area = get_object_or_404(Area, id=request.POST['area_id'])
        ChargeArea.objects.create(charge=charge, area=area)
        self.snapshot().add_event(
            user=request.user,
            description="charge **%s** vetted for area **%s**" % (charge.label,
                                                                  area.label),
            note=request.POST.get('comment', ''))
        return HttpResponseRedirect("/edit" + charge.get_absolute_url())


class RemoveAreaFromChargeView(StaffMixin, WorkingSnapshotMixin,
                               ChargeLocatorMixin, View):
    def post(self, request, slugs="", ca_id=""):
        charge = self.charge(slugs)
        ca = get_object_or_404(ChargeArea, id=ca_id)
        self.snapshot().add_event(
            user=request.user,
            description=("charge **%s** vetting removed for area **%s**" %
                         (charge.label, ca.area.label)))
        ca.delete()
        return HttpResponseRedirect("/edit" + charge.get_absolute_url())


class ReparentChargeView(StaffMixin, WorkingSnapshotMixin,
                         ChargeLocatorMixin, View):
    def post(self, request, slugs=""):
        charge = self.charge(slugs)
        new_parent = Charge.objects.get(id=request.POST['sibling_id'])
        cc = ChargeChildren.objects.filter(child=charge)
        cc.delete()
        ChargeChildren.objects.create(child=charge, parent=new_parent)
        self.snapshot().add_event(
            user=request.user,
            description="charge **%s** reparented to **%s**" % (
                charge.label, new_parent.label),
            note='')
        return HttpResponseRedirect("/edit" + charge.get_absolute_url())


class DeleteChargeView(StaffMixin, WorkingSnapshotMixin,
                       ChargeLocatorMixin, View):
    def post(self, request, slugs=""):
        charge = self.charge(slugs)
        redirect_to = "/edit/charge/"
        try:
            parent = charge.parents()[-1]
            redirect_to = "/edit" + parent.get_absolute_url()
        except IndexError:
            # top level charge
            pass
        self.snapshot().add_event(
            user=request.user,
            description="charge **%s** deleted" % (charge.label),
            note='')
        charge.delete_self()
        return HttpResponseRedirect(redirect_to)


@user_passes_test(lambda u: u.is_staff)
def edit_search(request):
    q = request.GET.get('q', '')
    if q == '':
        return HttpResponseRedirect("/")
    snapshot = working_snapshot()
    return render(
        request,
        'law/edit_search.html',
        dict(charges=Charge.objects.filter(snapshot=snapshot,
                                           label__icontains=q)))


def search(request):
    q = request.GET.get('q', '')
    if q == '':
        return HttpResponseRedirect("/")

    snapshot = public_snapshot()
    charges = Charge.objects.filter(
        snapshot=snapshot,
        label__icontains=q) | Charge.objects.filter(snapshot=snapshot,
                                                    penal_code__icontains=q)
    charges = [c for c in charges if c.is_leaf()]
    return render(request, 'law/search.html', dict(charges=charges))


class AutocompleteView(PublicSnapshotMixin, View):
    def get(self, request):
        q = request.GET.get('term', '')
        if q == '':
            return HttpResponseRedirect("/")
        q = q.lower()
        # NYS criminal code always calls it "marihuana" so this is a
        # common issue when searching
        q = q.replace("marij", "marih")
        charges = Charge.objects.filter(
            snapshot=self.snapshot(),
            label__icontains=q) | Charge.objects.filter(
                snapshot=self.snapshot(), penal_code__icontains=q)
        charges = list(set([c.label for c in charges if c.is_leaf()]))
        json = dumps(charges)
        return HttpResponse(json, content_type='application/json')


class RemoveChargeClassificationView(StaffMixin, WorkingSnapshotMixin,
                                     ChargeLocatorMixin, View):
    template_name = "law/remove_charge_classification.html"

    def get(self, request, slugs="", classification_id=""):
        charge = self.charge(slugs)

        classification = get_object_or_404(Classification,
                                           id=classification_id)
        return render_to_response(self.template_name,
                                  dict(charge=charge,
                                       classification=classification))

    def post(self, request, slugs="", classification_id=""):
        charge = self.charge(slugs)

        classification = get_object_or_404(Classification,
                                           id=classification_id)

        cc = ChargeClassification.objects.get(charge=charge,
                                              classification=classification)
        cc.delete()
        self.snapshot().add_event(
            user=request.user,
            description=("charge **%s** removed classification (%s) **%s**" %
                         (cc.charge.label, cc.certainty,
                          cc.classification.label)),
            note=request.POST.get('comment', ''))
        return HttpResponseRedirect("/edit" + charge.get_absolute_url())


class EditChargeView(StaffMixin, WorkingSnapshotMixin, ChargeLocatorMixin,
                     View):
    template_name = 'law/edit_charge.html'

    def get(self, request, slugs):
        slugs = slugs.split("/")
        charge = self.get_charge_by_slugs(slugs)
        edit_charge_form = EditChargeForm(instance=charge)
        return self.render(request, charge, edit_charge_form)

    def post(self, request, slugs):
        slugs = slugs.split("/")
        charge = self.get_charge_by_slugs(slugs)
        edit_charge_form = EditChargeForm(request.POST, instance=charge)
        if edit_charge_form.is_valid():
            edit_charge_form.save()
            self.snapshot().add_event(
                user=request.user,
                description="charge **%s** edited" % (charge.label),
                note=request.POST.get('comment', ''))

            return HttpResponseRedirect("/edit" + charge.get_absolute_url())
        return self.render(request, charge, edit_charge_form)

    def render(self, request, charge, edit_charge_form):
        return render(request, self.template_name,
                      dict(charge=charge,
                           edit_charge_form=edit_charge_form,
                           add_charge_form=AddChargeForm()))


class ChargeView(PublicSnapshotMixin, ChargeLocatorMixin, View):
    template_name = 'law/charge.html'

    def get(self, request, slugs):
        slugs = slugs.split("/")
        charge = self.get_charge_by_slugs(slugs)
        charge2 = None
        if request.GET.get('charge2', ''):
            charge2_path = request.GET.get(
                'charge2', '')[len("/charge/"):].strip("/")
            charge2_slugs = charge2_path.split("/")
            charge2 = self.get_charge_by_slugs(charge2_slugs)
        return render(request, self.template_name,
                      dict(charge=charge, charge2=charge2,
                           charges=self.snapshot().top_level_charges()))


class ChargeTipsView(PublicSnapshotMixin, ChargeLocatorMixin, View):
    template_name = 'law/charge_description.html'

    def get(self, request, slugs):
        slugs = slugs.split("/")
        charge = self.get_charge_by_slugs(slugs)
        return render(request, self.template_name, dict(charge=charge))


class EditClassificationIndexView(StaffMixin, WorkingSnapshotMixin,
                                  TemplateView):
    template_name = 'law/edit_classification_index.html'

    def get_context_data(self):
        return dict(
            classifications=Classification.objects.filter(
                snapshot=self.snapshot()),
            add_classification_form=AddClassificationForm())


class AddClassificationView(StaffMixin, WorkingSnapshotMixin, View):
    def post(self, request):
        slug = slugify(request.POST['label'])[:50]
        # need to check for duplicate slugs and fix
        try:
            Classification.objects.filter(name=slug)
            # uh oh. there's already a charge with that slug
            # need to come up with a relatively unique new one
            # this is the most reasonable approach I can think of
            slug = slug[:-3] + "%03d" % (Classification.objects.count() % 1000)
            # any better ideas?
        except Classification.DoesNotExist:
            # that's good
            pass

        c = Classification.objects.create(
            snapshot=self.snapshot(),
            label=request.POST['label'],
            description=request.POST['description'],
            name=slug,
        )
        self.snapshot().add_event(
            user=request.user,
            description="added classification **%s**" % c.label)

        return HttpResponseRedirect("/edit/classification/%s/" % c.name)


class EditClassificationView(StaffMixin, WorkingSnapshotMixin,
                             ClassificationLocatorMixin, View):
    template_name = 'law/edit_classification.html'

    def render(self, request, classification, edit_classification_form):
        return render(request, self.template_name,
                      dict(classification=classification,
                           edit_classification_form=edit_classification_form))

    def get(self, request, slug):
        classification = self.classification(slug)

        edit_classification_form = EditClassificationForm(
            instance=classification)
        return self.render(request, classification, edit_classification_form)

    def post(self, request, slug):
        classification = self.classification(slug)
        edit_classification_form = EditClassificationForm(
            request.POST,
            instance=classification)
        if edit_classification_form.is_valid():
            edit_classification_form.save()
            self.snapshot().add_event(
                user=request.user,
                description=("classification **%s** edited" %
                             (classification.label)),
                note=request.POST.get('comment', ''))

            return HttpResponseRedirect(
                "/edit" + classification.get_absolute_url())
        return self.render(request, classification, edit_classification_form)


class ClassificationView(PublicSnapshotMixin, ClassificationLocatorMixin,
                         View):
    template_name = 'law/view_classification.html'

    def get(self, request, slug):
        return render(request, self.template_name,
                      dict(classification=self.classification(slug)))


class PreviewClassificationView(
        WorkingSnapshotMixin, ClassificationLocatorMixin, TemplateView):
    template_name = 'law/view_classification.html'

    def get_context_data(self, slug):
        return dict(classification=self.classification(slug))


class DeleteClassificationView(StaffMixin, WorkingSnapshotMixin,
                               ClassificationLocatorMixin, View):
    def post(self, request, slug):
        classification = self.classification(slug)
        self.snapshot().add_event(
            user=request.user,
            description="deleted classification **%s**" % classification.label,
            note=request.POST.get('comment', ''))

        classification.delete()
        return HttpResponseRedirect("/edit/classification/")


class EditAreaIndexView(StaffMixin, WorkingSnapshotMixin, TemplateView):
    template_name = 'law/edit_area_index.html'

    def get_context_data(self):
        return dict(areas=Area.objects.filter(snapshot=self.snapshot()),
                    add_area_form=AddAreaForm())


class AddAreaView(StaffMixin, WorkingSnapshotMixin, View):
    def post(self, request):
        a = Area.objects.create(snapshot=self.snapshot(),
                                label=request.POST['label'],
                                name=slugify(request.POST['label']),
                                )
        self.snapshot().add_event(
            user=request.user,
            description="added area **%s**" % a.label)

        return HttpResponseRedirect("/edit/area/")


class EditAreaView(StaffMixin, WorkingSnapshotMixin, AreaLocatorMixin, View):
    template_name = 'law/edit_area.html'

    def render(self, request, area, edit_area_form):
        return render(
            request, self.template_name,
            dict(area=area, add_consequence_form=AddConsequenceForm(),
                 edit_area_form=edit_area_form))

    def get(self, request, slug):
        area = self.area(slug)
        edit_area_form = EditAreaForm(instance=area)
        return self.render(request, area, edit_area_form)

    def post(self, request, slug):
        area = self.area(slug)
        edit_area_form = EditAreaForm(request.POST, instance=area)
        if edit_area_form.is_valid():
            edit_area_form.save()
            self.snapshot().add_event(
                user=request.user,
                description="area **%s** edited" % (area.label),
                note=request.POST.get('comment', ''))

            return HttpResponseRedirect("/edit" + area.get_absolute_url())
        return self.render(request, area, edit_area_form)


class AreaView(PublicSnapshotMixin, AreaLocatorMixin, View):
    template_name = 'law/view_area.html'

    def get(self, request, slug):
        return render(
            request, self.template_name,
            dict(area=self.area(slug),
                 add_consequence_form=AddConsequenceForm()))


class DeleteAreaView(StaffMixin, WorkingSnapshotMixin, AreaLocatorMixin, View):
    def post(self, request, slug):
        area = self.area(slug)
        self.snapshot().add_event(
            user=request.user,
            description="area **%s** deleted" % area.label,
            note=request.POST.get('comment', ''),
        )
        area.delete()
        return HttpResponseRedirect("/edit/area/")


class AddConsequenceView(StaffMixin, WorkingSnapshotMixin, AreaLocatorMixin,
                         View):
    def post(self, request, slug):
        area = self.area(slug)
        name = slugify(request.POST['label'])[:50]
        # they really like naming consequences similarly so we have to
        # work hard to keep slugs unique
        i = 1
        while 1:
            r = Consequence.objects.filter(area=area, name=name)
            if r.count() == 0:
                break
            else:
                appendix = "-%d" % i
                i += 1
                lapp = len(appendix)
                name = name[:-lapp] + appendix

        consequence = Consequence.objects.create(
            area=area,
            label=request.POST['label'],
            description=request.POST.get('description', ''),
            name=name)
        self.snapshot().add_event(
            user=request.user,
            description="consequence **%s** added to **%s**" % (
                consequence.label, area.label))
        return HttpResponseRedirect("/edit" + area.get_absolute_url())


class EditConsequenceView(StaffMixin, WorkingSnapshotMixin,
                          AreaLocatorMixin, ConsequenceLocatorMixin, View):
    template_name = 'law/edit_consequence.html'

    def render(self, request, consequence, edit_consequence_form):
        return render(request, self.template_name,
                      dict(consequence=consequence,
                           edit_consequence_form=edit_consequence_form))

    def get(self, request, slug, cslug):
        area = self.area(slug)
        consequence = self.consequence(area, cslug)
        edit_consequence_form = EditConsequenceForm(instance=consequence)
        return self.render(request, consequence, edit_consequence_form)

    def post(self, request, slug, cslug):
        area = self.area(slug)
        consequence = self.consequence(area, cslug)
        edit_consequence_form = EditConsequenceForm(
            request.POST, instance=consequence)
        if edit_consequence_form.is_valid():
            edit_consequence_form.save()
            self.snapshot().add_event(
                user=request.user,
                description="consequence **%s** edited" % (consequence.label),
                note=request.POST.get('comment', ''))
            return HttpResponseRedirect(
                "/edit" + consequence.get_absolute_url())
        return self.render(request, consequence, edit_consequence_form)


class ConsequenceView(PublicSnapshotMixin, AreaLocatorMixin,
                      ConsequenceLocatorMixin, View):
    template_name = 'law/view_consequence.html'

    def get(self, request, slug, cslug):
        area = self.area(slug)
        consequence = self.consequence(area, cslug)
        return render(request, self.template_name,
                      dict(consequence=consequence))


class DeleteConsequenceView(StaffMixin, WorkingSnapshotMixin,
                            AreaLocatorMixin, ConsequenceLocatorMixin, View):
    def post(self, request, slug, cslug):
        area = self.area(slug)
        consequence = self.consequence(area, cslug)
        self.snapshot().add_event(
            user=request.user,
            description="deleting consequence **%s**" % consequence.label,
            note=request.POST.get('comment', ''))
        consequence.delete()
        return HttpResponseRedirect("/edit" + area.get_absolute_url())


class AddClassificationToConsequence(
        StaffMixin, WorkingSnapshotMixin, AreaLocatorMixin,
        ConsequenceLocatorMixin, View):
    def post(self, request, slug, cslug):
        area = self.area(slug)
        consequence = self.consequence(area, cslug)

        classification = get_object_or_404(
            Classification, id=request.POST['classification_id'])
        ClassificationConsequence.objects.create(
            consequence=consequence,
            classification=classification,
            certainty=request.POST.get('certainty', 'yes'))
        self.snapshot().add_event(
            user=request.user,
            description=(
                "consequence **%s** associated with classification **%s**" %
                (consequence.label, classification.label)),
            note=request.POST.get('comment', ''))
        return HttpResponseRedirect("/edit" + consequence.get_absolute_url())


class AddConsequenceToClassificationView(StaffMixin, WorkingSnapshotMixin,
                                         ClassificationLocatorMixin, View):
    def post(self, request, slug):
        consequence = get_object_or_404(
            Consequence, id=request.POST['consequence_id'])

        classification = self.classification(slug)
        # first, check if one already exists
        if ClassificationConsequence.objects.filter(
                consequence=consequence,
                classification=classification).count() > 0:
            return HttpResponse(
                ("this consequence is already associated "
                 "with this classification"))
        ClassificationConsequence.objects.create(
            consequence=consequence,
            classification=classification,
            certainty=request.POST.get('certainty', 'yes'))
        self.snapshot().add_event(
            user=request.user,
            description=(
                "consequence **%s** associated with classification **%s**" %
                (consequence.label, classification.label)),
            note=request.POST.get('comment', ''))
        return HttpResponseRedirect(
            "/edit" + classification.get_absolute_url())


class RemoveConsequenceFromClassificationView(
        StaffMixin, WorkingSnapshotMixin, ClassificationLocatorMixin, View):
    template_name = "law/remove_classification_consequence.html"

    def get(self, request, slug, consequence_id):
        consequence = get_object_or_404(Consequence, id=consequence_id)

        classification = self.classification(slug)
        return render_to_response(self.template_name,
                                  dict(consequence=consequence,
                                       classification=classification))

    def post(self, request, slug, consequence_id):
        consequence = get_object_or_404(Consequence, id=consequence_id)

        classification = self.classification(slug)
        ccs = ClassificationConsequence.objects.filter(
            consequence=consequence, classification=classification)
        for cc in ccs:
            cc.delete()
            self.snapshot().add_event(
                user=request.user,
                description=(
                    "consequence **%s** removed from classification **%s**" %
                    (consequence.label, cc.classification.label)),
                note=request.POST.get('comment', ''))
        return HttpResponseRedirect(
            "/edit" + classification.get_absolute_url())
