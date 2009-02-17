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
                                           

@rendered_with('law/edit_charge_index.html')
@login_required
def edit_charge_index(request):
    snapshot = working_snapshot()
    return dict(working_snapshot=snapshot,
                charges=snapshot.top_level_charges(),
                add_charge_form=AddChargeForm())
                
@login_required
def add_charge(request):
    f = AddChargeForm(request.POST)
    snapshot = working_snapshot()
    c = Charge.objects.create(snapshot=snapshot,
                              label=request.POST['label'],
                              penal_code=request.POST['penal_code'],
                              name=slugify(request.POST['label']))
    e = Event.objects.create(snapshot=snapshot,
                             user=request.user,
                             description="charge %s added" % str(c))
    return HttpResponseRedirect("/edit/charge/")
