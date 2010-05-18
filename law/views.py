from models import *
from forms import *
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpRequest
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
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


@rendered_with('law/feedback.html')
def feedback(request):
    return dict()

@user_passes_test(lambda u: u.is_staff)
@rendered_with('law/edit_index.html')
def edit_index(request):
    return dict(snapshots=Snapshot.objects.all(),
                working_snapshot=working_snapshot(),
                public_snapshot=public_snapshot())

@user_passes_test(lambda u: u.is_staff)
@rendered_with('law/edit_snapshots_index.html')
def edit_snapshots(request):
    return dict(snapshots=Snapshot.objects.all().order_by("-created"))


@user_passes_test(lambda u: u.is_staff)
@rendered_with('law/edit_snapshot.html')
def edit_snapshot(request,id):
    return dict(snapshot = get_object_or_404(Snapshot,id=id))

@user_passes_test(lambda u: u.is_staff)
def clone_snapshot(request,id):
    snapshot = get_object_or_404(Snapshot,id=id)
    new_snapshot = snapshot.clone(label=request.POST.get('label','new snapshot'),
                                  user=request.user,
                                  description=request.POST.get('description',''))
    return HttpResponseRedirect("/edit/")


@user_passes_test(lambda u: u.is_staff)
def approve_snapshot(request,id):
    snapshot = get_object_or_404(Snapshot,id=id)
    snapshot.status = 'vetted'
    snapshot.save()
    e = Event.objects.create(snapshot=snapshot,
                             user=request.user,
                             description="snapshot approved for production")
    # clone it to make a new working snapshot
    n = datetime.now()
    new_snapshot = snapshot.clone(label="%04d-%02d-%02d %02d:%02d" % (n.year,n.month,n.day,n.hour,n.minute),
                                  user=request.user,
                                  description="")
    return HttpResponseRedirect("/edit/snapshots/")


@rendered_with('law/graph.html')
def graph(request):
    snapshot = public_snapshot()
    return dict(snapshot=snapshot,
                charges=snapshot.top_level_charges(),
                all_charges=Charge.objects.filter(snapshot=snapshot).order_by("numeric_penal_code","penal_code","label"),
                all_classifications=Classification.objects.filter(snapshot=snapshot),
                all_areas=Area.objects.filter(snapshot=snapshot))

@user_passes_test(lambda u: u.is_staff)
@rendered_with('law/edit_charge_index.html')
def edit_charge_index(request):
    snapshot = working_snapshot()
    return dict(working_snapshot=snapshot,
                charges=snapshot.top_level_charges(),
                add_charge_form=AddChargeForm())
                
@user_passes_test(lambda u: u.is_staff)
def add_charge(request,slugs=""):
    if slugs != "" and slugs[-1] == "/":
        slugs = slugs[:-1]
    f = AddChargeForm(request.POST)
    snapshot = working_snapshot()
    slug = slugify(request.POST['penal_code'] + " " + request.POST['label'])[:50]
    # need to check for duplicate slugs and fix
    ct = Charge.objects.filter(name=slug)
    if ct.count() > 0:
        # uh oh. there's already a charge with that slug
        # need to come up with a relatively unique new one
        # this is the most reasonable approach I can think of
        slug = slug[:-3] + "%03d" % (Charge.objects.count() % 1000)
        # any better ideas?

    c = Charge.objects.create(snapshot=snapshot,
                              label=request.POST['label'],
                              penal_code=request.POST['penal_code'],
                              name=slug)
    slugs = slugs.split("/")
    description = "charge %s added" % str(c)
    if len(slugs) > 0 and slugs != ['']:
        parent = snapshot.get_charge_by_slugs(slugs)
        cc = ChargeChildren.objects.create(parent=parent,child=c)
        description = "charge **%s** added as child of **%s**" % (str(c),str(parent))
    e = Event.objects.create(snapshot=snapshot,
                             user=request.user,
                             description=description)
    if len(slugs) > 0 and slugs != ['']:
        parent = snapshot.get_charge_by_slugs(slugs)
        return HttpResponseRedirect("/edit" + parent.get_absolute_url())
    else:
        return HttpResponseRedirect("/edit/charge/")

@user_passes_test(lambda u: u.is_staff)
def add_charge_classification(request,slugs=""):
    if slugs[-1] == "/":
        slugs = slugs[:-1]
    slugs = slugs.split("/")
    snapshot = working_snapshot()
    charge = snapshot.get_charge_by_slugs(slugs)    
    classification = get_object_or_404(Classification,id=request.POST['classification_id'])
    if ChargeClassification.objects.filter(charge=charge,classification=classification).count() == 0:
        # only create if one doesn't already exist.
        # TODO: notify user
        cc = ChargeClassification.objects.create(charge=charge,classification=classification,
                                                 certainty=request.POST['certainty'])
        e = Event.objects.create(snapshot=snapshot,
                                 user=request.user,
                                 description="charge **%s** classified as (%s) **%s**" % (cc.charge.label,cc.certainty,cc.classification.label),
                                 note=request.POST.get('comment',''))
        
    return HttpResponseRedirect("/edit" + charge.get_absolute_url())

@user_passes_test(lambda u: u.is_staff)
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
                             description="charge **%s** vetted for area **%s**" % (charge.label,area.label),
                             note=request.POST.get('comment',''))
    return HttpResponseRedirect("/edit" + charge.get_absolute_url())

@user_passes_test(lambda u: u.is_staff)
def remove_area_from_charge(request,slugs="",ca_id=""):
    if slugs[-1] == "/":
        slugs = slugs[:-1]
    slugs = slugs.split("/")
    snapshot = working_snapshot()
    charge = snapshot.get_charge_by_slugs(slugs)  
    ca = get_object_or_404(ChargeArea,id=ca_id)
    e = Event.objects.create(snapshot=snapshot,
                             user=request.user,
                             description="charge **%s** vetting removed for area **%s**" % (charge.label,ca.area.label))
    ca.delete()
    return HttpResponseRedirect("/edit" + charge.get_absolute_url())


@user_passes_test(lambda u: u.is_staff)
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

@user_passes_test(lambda u: u.is_staff)
def delete_charge(request,slugs=""):
    if slugs[-1] == "/":
        slugs = slugs[:-1]
    slugs = slugs.split("/")
    snapshot = working_snapshot()
    charge = snapshot.get_charge_by_slugs(slugs)    
    redirect_to = "/edit/charge/"
    try:
        parent = charge.parents()[-1]
        redirect_to = "/edit" + parent.get_absolute_url()
    except IndexError:
        # top level charge
        pass

    charge.delete_self()
    return HttpResponseRedirect(redirect_to)


@user_passes_test(lambda u: u.is_staff)
@rendered_with('law/edit_search.html')
def edit_search(request):
    q = request.GET['q']
    snapshot = working_snapshot()
    return dict(charges=Charge.objects.filter(snapshot=snapshot,label__icontains=q))

@rendered_with('law/search.html')
def search(request):
    q = request.GET['q']
    snapshot = public_snapshot()
    charges = Charge.objects.filter(snapshot=snapshot,label__icontains=q) | Charge.objects.filter(snapshot=snapshot,penal_code__icontains=q)
    charges = [c for c in charges if c.is_leaf()]
    return dict(charges=charges)

@user_passes_test(lambda u: u.is_staff)
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
                                 description="charge **%s** removed classification (%s) **%s**" % (cc.charge.label,cc.certainty,cc.classification.label),
                                 note=request.POST.get('comment',''))
        return HttpResponseRedirect("/edit" + charge.get_absolute_url())
    return render_to_response("law/remove_charge_classification.html",dict(charge=charge,classification=classification))


@user_passes_test(lambda u: u.is_staff)
@rendered_with('law/edit_charge.html')
def edit_charge(request,slugs):
    slugs = slugs.split("/")
    snapshot = working_snapshot()
    charge = snapshot.get_charge_by_slugs(slugs)
    edit_charge_form = EditChargeForm(instance=charge)
    if request.method == "POST":
        edit_charge_form = EditChargeForm(request.POST,instance=charge)
        if edit_charge_form.is_valid():
            edit_charge_form.save()
            return HttpResponseRedirect("/edit" + charge.get_absolute_url())
    return dict(charge=charge,
                edit_charge_form=edit_charge_form,
                add_charge_form=AddChargeForm())

@rendered_with('law/charge.html')
def view_charge(request,slugs):
    slugs = slugs.split("/")
    snapshot = public_snapshot()
    charge = snapshot.get_charge_by_slugs(slugs)
    charge2 = None
    if request.GET.get('charge2',''):
        charge2_path = request.GET.get('charge2','')[len("/charge/"):].strip("/")
        charge2_slugs = charge2_path.split("/")
        charge2 = snapshot.get_charge_by_slugs(charge2_path.split("/"))
    return dict(charge=charge,charge2=charge2,charges=snapshot.top_level_charges())


@user_passes_test(lambda u: u.is_staff)
@rendered_with('law/edit_classification_index.html')
def edit_classification_index(request):
    snapshot = working_snapshot()
    return dict(classifications=Classification.objects.filter(snapshot=snapshot),
                add_classification_form=AddClassificationForm())

@user_passes_test(lambda u: u.is_staff)
def add_classification(request):
    f = AddClassificationForm(request.POST)
    snapshot = working_snapshot()
    slug = slugify(request.POST['label'])[:50]
    # need to check for duplicate slugs and fix
    try:
        ct = Classification.objects.get(name=slug)
        # uh oh. there's already a charge with that slug
        # need to come up with a relatively unique new one
        # this is the most reasonable approach I can think of
        slug = slug[:-3] + "%03d" % (Classification.objects.count() % 1000)
        # any better ideas?
    except Classification.DoesNotExist:
        # that's good
        pass

    c = Classification.objects.create(snapshot=snapshot,
                                      label=request.POST['label'],
                                      description=request.POST['description'],
                                      name=slug,
                                      )
    e = Event.objects.create(snapshot=snapshot,
                             user=request.user,
                             description="added classification **%s**" % c.label)

    return HttpResponseRedirect("/edit/classification/%s/" % c.name)

@user_passes_test(lambda u: u.is_staff)
@rendered_with('law/edit_classification.html')
def edit_classification(request,slug):
    snapshot = working_snapshot()
    classification = get_object_or_404(Classification,snapshot=snapshot,name=slug)

    edit_classification_form = EditClassificationForm(instance=classification)
    if request.method == "POST":
        edit_classification_form = EditClassificationForm(request.POST,instance=classification)
        if edit_classification_form.is_valid():
            edit_classification_form.save()
            return HttpResponseRedirect("/edit" + classification.get_absolute_url())

    return dict(classification=classification,
                edit_classification_form=edit_classification_form)

@rendered_with('law/view_classification.html')
def view_classification(request,slug):
    snapshot = public_snapshot()
    classification = get_object_or_404(Classification,snapshot=snapshot,name=slug)
    return dict(classification=classification)

@rendered_with('law/view_classification.html')
def preview_classification(request,slug):
    snapshot = working_snapshot()
    classification = get_object_or_404(Classification,snapshot=snapshot,name=slug)
    return dict(classification=classification)


@user_passes_test(lambda u: u.is_staff)
def delete_classification(request,slug):
    snapshot = working_snapshot()
    classification = get_object_or_404(Classification,snapshot=snapshot,name=slug)
    e = Event.objects.create(snapshot=snapshot,
                             user=request.user,
                             description="deleted classification **%s**" % classification.label,
                             note=request.POST.get('comment',''))
    classification.delete()
    return HttpResponseRedirect("/edit/classification/")


@user_passes_test(lambda u: u.is_staff)
@rendered_with('law/edit_area_index.html')
def edit_area_index(request):
    snapshot = working_snapshot()
    return dict(areas=Area.objects.filter(snapshot=snapshot),
                add_area_form=AddAreaForm())

@user_passes_test(lambda u: u.is_staff)
def add_area(request):
    f = AddAreaForm(request.POST)
    snapshot = working_snapshot()
    a = Area.objects.create(snapshot=snapshot,
                            label=request.POST['label'],
                            name=slugify(request.POST['label']),
                            )
    e = Event.objects.create(snapshot=snapshot,
                             user=request.user,
                             description="added area **%s**" % a.label)

    return HttpResponseRedirect("/edit/area/")

@user_passes_test(lambda u: u.is_staff)
@rendered_with('law/edit_area.html')
def edit_area(request,slug):
    snapshot = working_snapshot()
    area = get_object_or_404(Area,snapshot=snapshot,name=slug)

    edit_area_form = EditAreaForm(instance=area)
    if request.method == "POST":
        edit_area_form = EditAreaForm(request.POST,instance=area)
        if edit_area_form.is_valid():
            edit_area_form.save()
            return HttpResponseRedirect("/edit" + area.get_absolute_url())

    return dict(area=area,add_consequence_form=AddConsequenceForm(),
                edit_area_form=edit_area_form)

@rendered_with('law/view_area.html')
def view_area(request,slug):
    snapshot = public_snapshot()
    area = get_object_or_404(Area,snapshot=snapshot,name=slug)
    return dict(area=area,add_consequence_form=AddConsequenceForm())


@user_passes_test(lambda u: u.is_staff)
def delete_area(request,slug):
    snapshot = working_snapshot()
    area = get_object_or_404(Area,snapshot=snapshot,name=slug)
    e = Event.objects.create(snapshot=snapshot,
                             user=request.user,
                             description="area **%s** deleted" % area.label,
                             note=request.POST.get('comment',''),
                             )
    area.delete()
    return HttpResponseRedirect("/edit/area/")

@user_passes_test(lambda u: u.is_staff)
def add_consequence(request,slug):
    snapshot = working_snapshot()
    area = get_object_or_404(Area,snapshot=snapshot,name=slug)
    name = slugify(request.POST['label'])[:50]
    # they really like naming consequences similarly so we have to 
    # work hard to keep slugs unique
    i = 1
    while 1:
        r = Consequence.objects.filter(area=area,name=name)
        if r.count() == 0:
            break
        else:
            appendix = "-%d" % i
            i += 1
            lapp = len(appendix)
            name = name[:-lapp] + appendix
        
    consequence = Consequence.objects.create(area=area,
                                             label=request.POST['label'],
                                             description=request.POST.get('description',''),
                                             name=name)
    e = Event.objects.create(snapshot=snapshot,
                             user=request.user,
                             description="consequence **%s** added to **%s**" % (consequence.label,area.label))
    return HttpResponseRedirect("/edit" + area.get_absolute_url())


@user_passes_test(lambda u: u.is_staff)
@rendered_with('law/edit_consequence.html')
def edit_consequence(request,slug,cslug):
    snapshot = working_snapshot()
    area = get_object_or_404(Area,snapshot=snapshot,name=slug)
    consequence = get_object_or_404(Consequence,area=area,name=cslug)

    edit_consequence_form = EditConsequenceForm(instance=consequence)
    if request.method == "POST":
        edit_consequence_form = EditConsequenceForm(request.POST,instance=consequence)
        if edit_consequence_form.is_valid():
            edit_consequence_form.save()
            return HttpResponseRedirect("/edit" + consequence.get_absolute_url())
        else:
            return dict(consequence=consequence,
                        edit_consequence_form=edit_consequence_form)
    return dict(consequence=consequence,
                edit_consequence_form=edit_consequence_form)

@rendered_with('law/view_consequence.html')
def view_consequence(request,slug,cslug):
    snapshot = public_snapshot()
    area = get_object_or_404(Area,snapshot=snapshot,name=slug)
    consequence = get_object_or_404(Consequence,area=area,name=cslug)
    return dict(consequence=consequence)



@user_passes_test(lambda u: u.is_staff)
def delete_consequence(request,slug,cslug):
    snapshot = working_snapshot()
    area = get_object_or_404(Area,snapshot=snapshot,name=slug)
    consequence = get_object_or_404(Consequence,area=area,name=cslug)
    e = Event.objects.create(snapshot=snapshot,user=request.user,
                             description="deleting consequence **%s**" % consequence.label,
                             note=request.POST.get('comment',''))
    consequence.delete()
    return HttpResponseRedirect("/edit" + area.get_absolute_url())

@user_passes_test(lambda u: u.is_staff)
def add_classification_to_consequence(request,slug,cslug):
    snapshot = working_snapshot()
    area = get_object_or_404(Area,snapshot=snapshot,name=slug)
    consequence = get_object_or_404(Consequence,area=area,name=cslug)
    classification = get_object_or_404(Classification,id=request.POST['classification_id'])
    cc = ClassificationConsequence.objects.create(consequence=consequence,
                                                  classification=classification,
                                                  certainty=request.POST.get('certainty','yes'))
    e = Event.objects.create(snapshot=snapshot,user=request.user,
                             description="consequence **%s** associated with classification **%s**" % (consequence.label,classification.label),
                             note=request.POST.get('comment',''))
    return HttpResponseRedirect("/edit" + consequence.get_absolute_url())

@user_passes_test(lambda u: u.is_staff)
def add_consequence_to_classification(request,slug):
    snapshot = working_snapshot()
    consequence = get_object_or_404(Consequence,id=request.POST['consequence_id'])
    classification = get_object_or_404(Classification,snapshot=snapshot,name=slug)
    cc = ClassificationConsequence.objects.create(consequence=consequence,
                                                  classification=classification,
                                                  certainty=request.POST.get('certainty','yes'))
    e = Event.objects.create(snapshot=snapshot,user=request.user,
                             description="consequence **%s** associated with classification **%s**" % (consequence.label,classification.label),
                             note=request.POST.get('comment',''))
    return HttpResponseRedirect("/edit" + classification.get_absolute_url())


@user_passes_test(lambda u: u.is_staff)
def remove_consequence_from_classification(request,slug,consequence_id):
    snapshot = working_snapshot()
    consequence = get_object_or_404(Consequence,id=consequence_id)
    classification = get_object_or_404(Classification,snapshot=snapshot,name=slug)
    cc = get_object_or_404(ClassificationConsequence,consequence=consequence,classification=classification)
    e = Event.objects.create(snapshot=snapshot,user=request.user,
                             description="consequence **%s** removed from classification **%s**" % (consequence.label,classification.label))
    cc.delete()
    return HttpResponseRedirect("/edit" + classification.get_absolute_url())







