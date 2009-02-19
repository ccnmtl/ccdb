from models import *
from forms import *
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django import forms
from datetime import datetime
from django.template.defaultfilters import slugify
import simplejson

class rendered_with(object):
    def __init__(self, template_name):
        self.template_name = template_name

    def __call__(self, func):
        def rendered_func(request, *args, **kwargs):
            items = func(request, *args, **kwargs)
            return render_to_response(self.template_name, items, context_instance=RequestContext(request))

        return rendered_func

@rendered_with('law/index.html')
def index(request):
    snapshot = public_snapshot()
    return dict(charges=snapshot.charge_set.all())


@rendered_with('law/edit_index.html')
@login_required
def edit_index(request):
    return dict(snapshots=Snapshot.objects.all(),
                working_snapshot=working_snapshot(),
                public_snapshot=public_snapshot())

@rendered_with('law/edit_snapshots_index.html')
@login_required
def edit_snapshots(request):
    return dict(snapshots=Snapshot.objects.all().order_by("-created"))


@rendered_with('law/edit_snapshot.html')
@login_required
def edit_snapshot(request,id):
    return dict(snapshot = get_object_or_404(Snapshot,id=id))

@login_required
def clone_snapshot(request,id):
    snapshot = get_object_or_404(Snapshot,id=id)
    new_snapshot = snapshot.clone(label=request.POST.get('label','new snapshot'),
                                  user=request.user,
                                  description=request.POST.get('description',''))
    return HttpResponseRedirect("/edit/")


@login_required
def approve_snapshot(request,id):
    snapshot = get_object_or_404(Snapshot,id=id)
    snapshot.status = 'vetted'
    snapshot.save()
    e = Event.objects.create(snapshot=snapshot,
                             user=request.user,
                             description="snapshot approved for production")
    return HttpResponseRedirect("/edit/snapshots/")
                                           

@rendered_with('law/edit_charge_index.html')
@login_required
def edit_charge_index(request):
    snapshot = working_snapshot()
    return dict(working_snapshot=snapshot,
                charges=snapshot.top_level_charges(),
                add_charge_form=AddChargeForm())
                
@login_required
def add_charge(request,slugs=""):
    if slugs[-1] == "/":
        slugs = slugs[:-1]
    f = AddChargeForm(request.POST)
    snapshot = working_snapshot()
    c = Charge.objects.create(snapshot=snapshot,
                              label=request.POST['label'],
                              penal_code=request.POST['penal_code'],
                              name=slugify(request.POST['penal_code'] + " " + request.POST['label']))
    slugs = slugs.split("/")
    description = "charge %s added" % str(c)
    if len(slugs) > 0:
        parent = snapshot.get_charge_by_slugs(slugs)
        cc = ChargeChildren.objects.create(parent=parent,child=c)
        description = "charge %s added as child of %s" % (str(c),str(parent))
    e = Event.objects.create(snapshot=snapshot,
                             user=request.user,
                             description=description)
    return HttpResponseRedirect("/edit/charge/")

@login_required
def add_charge_classification(request,slugs=""):
    if slugs[-1] == "/":
        slugs = slugs[:-1]
    slugs = slugs.split("/")
    snapshot = working_snapshot()
    charge = snapshot.get_charge_by_slugs(slugs)    
    classification = get_object_or_404(Classification,id=request.POST['classification_id'])
    cc = ChargeClassification.objects.create(charge=charge,classification=classification,
                                             certainty=request.POST['certainty'])
    e = Event.objects.create(snapshot=snapshot,
                             user=request.user,
                             description="charge %s classified as (%s) %s" % (cc.charge.label,cc.certainty,cc.classification.label),
                             note=request.POST.get('comment',''))
    return HttpResponseRedirect("/edit" + charge.get_absolute_url())


@login_required
def remove_charge_classification(request,slugs="",classification_id=""):
    if slugs[-1] == "/":
        slugs = slugs[:-1]
    slugs = slugs.split("/")
    snapshot = working_snapshot()
    charge = snapshot.get_charge_by_slugs(slugs)    
    classification = get_object_or_404(Classification,id=classification_id)

    cc = ChargeClassification.objects.get(charge=charge,classification=classification)

    if request.POST:
        cc.delete()
        e = Event.objects.create(snapshot=snapshot,
                                 user=request.user,
                                 description="charge %s removed classification (%s) %s" % (cc.charge.label,cc.certainty,cc.classification.label),
                                 note=request.POST.get('comment',''))
        return HttpResponseRedirect("/edit" + charge.get_absolute_url())
    return render_to_response("law/remove_charge_classification.html",dict(charge=charge,classification=classification))


@rendered_with('law/edit_charge.html')
@login_required
def edit_charge(request,slugs):
    slugs = slugs.split("/")
    snapshot = working_snapshot()
    charge = snapshot.get_charge_by_slugs(slugs)
    return dict(charge=charge,add_charge_form=AddChargeForm())

@rendered_with('law/edit_classification_index.html')
@login_required
def edit_classification_index(request):
    snapshot = working_snapshot()
    return dict(classifications=Classification.objects.filter(snapshot=snapshot),
                add_classification_form=AddClassificationForm())

@login_required
def add_classification(request):
    f = AddClassificationForm(request.POST)
    snapshot = working_snapshot()
    c = Classification.objects.create(snapshot=snapshot,
                                      label=request.POST['label'],
                                      description=request.POST['description'],
                                      name=slugify(request.POST['label']),
                                      )
    e = Event.objects.create(snapshot=snapshot,
                             user=request.user,
                             description="added classification %s" % c.label)

    return HttpResponseRedirect("/edit/classification/")

@rendered_with('law/edit_classification.html')
@login_required
def edit_classification(request,slug):
    snapshot = working_snapshot()
    classification = get_object_or_404(Classification,snapshot=snapshot,name=slug)
    return dict(classification=classification)


@rendered_with('law/edit_area_index.html')
@login_required
def edit_area_index(request):
    snapshot = working_snapshot()
    return dict(areas=Area.objects.filter(snapshot=snapshot),
                add_area_form=AddAreaForm())

@login_required
def add_area(request):
    f = AddAreaForm(request.POST)
    snapshot = working_snapshot()
    a = Area.objects.create(snapshot=snapshot,
                            label=request.POST['label'],
                            name=slugify(request.POST['label']),
                            )
    e = Event.objects.create(snapshot=snapshot,
                             user=request.user,
                             description="added area %s" % a.label)

    return HttpResponseRedirect("/edit/area/")

@rendered_with('law/edit_area.html')
@login_required
def edit_area(request,slug):
    snapshot = working_snapshot()
    area = get_object_or_404(Area,snapshot=snapshot,name=slug)
    return dict(area=area)


