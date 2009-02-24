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
            if type(items) == type({}):
                return render_to_response(self.template_name, items, context_instance=RequestContext(request))
            else:
                return items

        return rendered_func

@rendered_with('law/index.html')
def index(request):
    snapshot = public_snapshot()
    return dict(charges=snapshot.top_level_charges())


@login_required
@rendered_with('law/edit_index.html')
def edit_index(request):
    return dict(snapshots=Snapshot.objects.all(),
                working_snapshot=working_snapshot(),
                public_snapshot=public_snapshot())

@login_required
@rendered_with('law/edit_snapshots_index.html')
def edit_snapshots(request):
    return dict(snapshots=Snapshot.objects.all().order_by("-created"))


@login_required
@rendered_with('law/edit_snapshot.html')
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
                                           

@login_required
@rendered_with('law/edit_charge_index.html')
def edit_charge_index(request):
    snapshot = working_snapshot()
    return dict(working_snapshot=snapshot,
                charges=snapshot.top_level_charges(),
                add_charge_form=AddChargeForm())
                
@login_required
def add_charge(request,slugs=""):
    if slugs != "" and slugs[-1] == "/":
        slugs = slugs[:-1]
    f = AddChargeForm(request.POST)
    snapshot = working_snapshot()
    c = Charge.objects.create(snapshot=snapshot,
                              label=request.POST['label'],
                              penal_code=request.POST['penal_code'],
                              name=slugify(request.POST['penal_code'] + " " + request.POST['label'])[:50])
    slugs = slugs.split("/")
    description = "charge %s added" % str(c)
    if len(slugs) > 0 and slugs != ['']:
        parent = snapshot.get_charge_by_slugs(slugs)
        cc = ChargeChildren.objects.create(parent=parent,child=c)
        description = "charge %s added as child of %s" % (str(c),str(parent))
    e = Event.objects.create(snapshot=snapshot,
                             user=request.user,
                             description=description)
    if len(slugs) > 0 and slugs != ['']:
        parent = snapshot.get_charge_by_slugs(slugs)
        return HttpResponseRedirect("/edit" + parent.get_absolute_url())
    else:
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
def add_area_to_charge(request,slugs=""):
    if slugs[-1] == "/":
        slugs = slugs[:-1]
    slugs = slugs.split("/")
    snapshot = working_snapshot()
    charge = snapshot.get_charge_by_slugs(slugs)    
    area = get_object_or_404(Area,id=request.POST['area_id'])
    ca = ChargeArea.objects.create(charge=charge,area=area)
    e = Event.objects.create(snapshot=snapshot,
                             user=request.user,
                             description="charge %s added to area %s" % (charge.label,area.label),
                             note=request.POST.get('comment',''))
    return HttpResponseRedirect("/edit" + charge.get_absolute_url())

@login_required
def remove_area_from_charge(request,slugs="",ca_id=""):
    if slugs[-1] == "/":
        slugs = slugs[:-1]
    slugs = slugs.split("/")
    snapshot = working_snapshot()
    charge = snapshot.get_charge_by_slugs(slugs)  
    ca = get_object_or_404(ChargeArea,id=ca_id)
    e = Event.objects.create(snapshot=snapshot,
                             user=request.user,
                             description="charge %s removed from area %s" % (charge.label,ca.area.label))
    ca.delete()
    return HttpResponseRedirect("/edit" + charge.get_absolute_url())


@login_required
def reparent_charge(request,slugs=""):
    if slugs[-1] == "/":
        slugs = slugs[:-1]
    slugs = slugs.split("/")
    snapshot = working_snapshot()
    charge = snapshot.get_charge_by_slugs(slugs)    
    new_parent = Charge.objects.get(id=request.POST['sibling_id'])
    cc = ChargeChildren.objects.filter(child=charge)
    cc.delete()
    ncc = ChargeChildren.objects.create(child=charge,parent=new_parent)
    return HttpResponseRedirect("/edit" + charge.get_absolute_url())

@login_required
def delete_charge(request,slugs=""):
    if slugs[-1] == "/":
        slugs = slugs[:-1]
    slugs = slugs.split("/")
    snapshot = working_snapshot()
    charge = snapshot.get_charge_by_slugs(slugs)    
    parent = charge.parents()[-1]
    charge.delete_self()
    return HttpResponseRedirect("/edit" + parent.get_absolute_url())


@login_required
@rendered_with('law/edit_search.html')
def edit_search(request):
    q = request.GET['q']
    return dict(charges=Charge.objects.filter(label__icontains=q))


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


@login_required
@rendered_with('law/edit_charge.html')
def edit_charge(request,slugs):
    slugs = slugs.split("/")
    snapshot = working_snapshot()
    charge = snapshot.get_charge_by_slugs(slugs)
    return dict(charge=charge,add_charge_form=AddChargeForm())

@rendered_with('law/charge.html')
def view_charge(request,slugs):
    slugs = slugs.split("/")
    snapshot = public_snapshot()
    charge = snapshot.get_charge_by_slugs(slugs)
    all = charge.view_all()
    return dict(charge=charge)


@login_required
@rendered_with('law/edit_classification_index.html')
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

@login_required
@rendered_with('law/edit_classification.html')
def edit_classification(request,slug):
    snapshot = working_snapshot()
    classification = get_object_or_404(Classification,snapshot=snapshot,name=slug)
    return dict(classification=classification)

@login_required
def delete_classification(request,slug):
    snapshot = working_snapshot()
    classification = get_object_or_404(Classification,snapshot=snapshot,name=slug)
    e = Event.objects.create(snapshot=snapshot,
                             user=request.user,
                             description="deleted classification %s" % classification.label,
                             note=request.POST.get('comment',''))
    classification.delete()
    return HttpResponseRedirect("/edit/classification/")


@login_required
@rendered_with('law/edit_area_index.html')
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

@login_required
@rendered_with('law/edit_area.html')
def edit_area(request,slug):
    snapshot = working_snapshot()
    area = get_object_or_404(Area,snapshot=snapshot,name=slug)
    return dict(area=area,add_consequence_form=AddConsequenceForm())

@login_required
def delete_area(request,slug):
    snapshot = working_snapshot()
    area = get_object_or_404(Area,snapshot=snapshot,name=slug)
    e = Event.objects.create(snapshot=snapshot,
                             user=request.user,
                             description="area %s deleted" % area.label,
                             note=request.POST.get('comment',''),
                             )
    area.delete()
    return HttpResponseRedirect("/edit/area/")

@login_required
def add_consequence(request,slug):
    snapshot = working_snapshot()
    area = get_object_or_404(Area,snapshot=snapshot,name=slug)
    consequence = Consequence.objects.create(area=area,
                                             label=request.POST['label'],
                                             description=request.POST.get('description',''),
                                             name=slugify(request.POST['label'])[:50])
    e = Event.objects.create(snapshot=snapshot,
                             user=request.user,
                             description="consequence %s added to %s" % (consequence.label,area.label))
    return HttpResponseRedirect("/edit" + area.get_absolute_url())


@login_required
@rendered_with('law/edit_consequence.html')
def edit_consequence(request,slug,cslug):
    snapshot = working_snapshot()
    area = get_object_or_404(Area,snapshot=snapshot,name=slug)
    consequence = get_object_or_404(Consequence,area=area,name=cslug)
    return dict(consequence=consequence)


@login_required
def delete_consequence(request,slug,cslug):
    snapshot = working_snapshot()
    area = get_object_or_404(Area,snapshot=snapshot,name=slug)
    consequence = get_object_or_404(Consequence,area=area,name=cslug)
    e = Event.objects.create(snapshot=snapshot,user=request.user,
                             description="deleting consequence %s" % consequence.label,
                             note=request.POST.get('comment',''))
    consequence.delete()
    return HttpResponseRedirect("/edit" + area.get_absolute_url())

@login_required
def add_classification_to_consequence(request,slug,cslug):
    snapshot = working_snapshot()
    area = get_object_or_404(Area,snapshot=snapshot,name=slug)
    consequence = get_object_or_404(Consequence,area=area,name=cslug)
    classification = get_object_or_404(Classification,id=request.POST['classification_id'])
    cc = ClassificationConsequence.objects.create(consequence=consequence,
                                                  classification=classification,
                                                  certainty=request.POST.get('certainty','yes'))
    e = Event.objects.create(snapshot=snapshot,user=request.user,
                             description="consequence %s associated with classification %s" % (consequence.label,classification.label),
                             note=request.POST.get('comment',''))
    return HttpResponseRedirect("/edit" + consequence.get_absolute_url())

@login_required
def add_consequence_to_classification(request,slug):
    snapshot = working_snapshot()
    consequence = get_object_or_404(Consequence,id=request.POST['consequence_id'])
    classification = get_object_or_404(Classification,snapshot=snapshot,name=slug)
    cc = ClassificationConsequence.objects.create(consequence=consequence,
                                                  classification=classification,
                                                  certainty=request.POST.get('certainty','yes'))
    e = Event.objects.create(snapshot=snapshot,user=request.user,
                             description="consequence %s associated with classification %s" % (consequence.label,classification.label),
                             note=request.POST.get('comment',''))
    return HttpResponseRedirect("/edit" + classification.get_absolute_url())


@login_required
def remove_consequence_from_classification(request,slug,consequence_id):
    snapshot = working_snapshot()
    consequence = get_object_or_404(Consequence,id=consequence_id)
    classification = get_object_or_404(Classification,snapshot=snapshot,name=slug)
    cc = get_object_or_404(ClassificationConsequence,consequence=consequence,classification=classification)
    e = Event.objects.create(snapshot=snapshot,user=request.user,
                             description="consequence %s removed from classification %s" % (consequence.label,classification.label))
    cc.delete()
    return HttpResponseRedirect("/edit" + classification.get_absolute_url())


def remove_comment(line):
    if "#" in line:
        line = line[:line.index("#")]
    return line

import re
def normalize_whitespace(line):
    p = re.compile(r"\s+")
    return p.sub(" ",line)

def bootstrap(request):
    snapshot = working_snapshot()
    print "clearing..."
    snapshot.clear()
    print "cleared."
    current_group = ""
    current_menu = ""
    current_offense = ""
    mode = "group"
    label = ""
    penal_code = ""
    paragraph = ""
    for line in open('n3/menus.n3').readlines():
        line = normalize_whitespace(remove_comment(line.strip())).strip()
        if not line:
            continue
        if line.endswith("a :Group;"):
            mode = "group"
            parts = line.split(' ')
            print "Group: " + parts[0]
            current_group = parts[0]
            paragraph = ""
            current_menu = ""
            current_offense = ""
        if line.endswith("a :MENU;"):
            mode = "menu"
            parts = line.split(' ')
            print "%s / %s" % (current_group,parts[0])
            current_menu = parts[0]
            current_offense = ""
            paragraph = ""
        if ":in " in line:
            mode = "offense"
            parts = line.split(" ")
            print "%s / %s / %s" % (current_group,current_menu,parts[0])
            current_offense = parts[0]
            paragraph = ""
        
        if line.startswith('rdfs:label'):
            label = line[len('rdfs:label ') + 1:-2]
            print "label: %s" % label

        if line.startswith(':penal-code'):
            penal_code = line[len(':penal-code ') + 1:-2]
            print "penal-code: %s" % penal_code

        if line.startswith(":paragraph"):
            paragraph = line[len(':paragraph ') + 1:-2]

        if line.endswith("."):
            print "-- end of %s --" % mode
            if paragraph != "" and mode == "offense":
                label = label + " (%s)" % paragraph
            c = Charge.objects.create(snapshot=snapshot,
                                      label=label,
                                      penal_code=penal_code,
                                      name=slugify(penal_code + " " + label)[:50])

            if mode == "group":
                current_group = c
            if mode == "menu":
                # make it a child of the group
                cc = ChargeChildren.objects.create(parent=current_group,child=c)
                current_menu = c
            if mode == "offense":
                # make it a child of the menu
                cc = ChargeChildren.objects.create(parent=current_menu,child=c)

    return HttpResponse("ok")

