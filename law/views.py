from models import *
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404
from django import forms
from datetime import datetime
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
    return dict(groups=snapshot.group_set.all())


@rendered_with('law/edit_index.html')
@login_required
def edit_index(request):
    return dict(snapshots=Snapshot.objects.all())

@rendered_with('law/edit_snapshot.html')
@login_required
def edit_snapshot(request,id):
    return dict(snapshot = get_object_or_404(Snapshot,id=id))

@login_required
def clone_snapshot(request,id):
    snapshot = get_object_or_404(Snapshot,id=id)
    new_snapshot = Snapshot.objects.create(label=request.POST.get('label','new snapshot'),
                                           description=request.POST.get('description',''))
    e = Event.objects.create(snapshot=new_snapshot,
                             user=request.user,
                             description="snapshot created")
    snapshot.clone_to(new_snapshot)
    return HttpResponseRedirect("/edit/")
                                           
