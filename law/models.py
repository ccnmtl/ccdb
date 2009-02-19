from django.db import models
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404
from django import forms

class Snapshot(models.Model):
    label = models.CharField(max_length=256)
    description = models.TextField(default="",blank=True)
    status = models.CharField(max_length=256,
                              choices=[('in progress','In Progress'),
                                       ('qa','In QA'),
                                       ('vetted','Vetted')],
                              default="in progress")
    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.label

    def is_most_recent_vetted(self):
        s = public_snapshot()
        return s.id == self.id

    def is_current_working(self):
        return self.status == "in progress" 

    def cloneable(self):
        return self.is_most_recent_vetted() and \
            Snapshot.objects.exclude(status="vetted").count() == 0

    def get_absolute_url(self):
        return "/snapshots/%d/" % self.id

    def clone(self,label,user,description=""):

        new_snapshot = Snapshot.objects.create(label=label,description=description)
        e = Event.objects.create(snapshot=new_snapshot,user=user,
                                 description="snapshot created")

        charge_map = dict()
        area_map = dict()
        classification_map = dict()
        consequence_map = dict()

        for charge in self.charge_set.all():
            nc = charge.clone_to(new_snapshot)
            charge_map[charge.id] = nc
        for area in self.area_set.all():
            na = area.clone_to(new_snapshot)
            area_map[area.id] = na
            for consequence in area.consequence_set.all():
                new_consequence = consequence.clone_to(na)
                consequence_map[consequence.id] = new_consequence

        for classification in self.classification_set.all():
            nc = classification.clone_to(new_snapshot)
            classification_map[classification.id] = nc

        # clone parent-child relationships
        for charge in self.charge_set.all():
            newparent = charge_map[charge.id]
            for cc in ChargeChildren.objects.filter(parent=charge):
                newchild = charge_map[cc.child.id]
                ncc = ChargeChildren.objects.create(parent=newparent,
                                                    child=newchild)

        # clone charges -> classifications

        for charge in self.charge_set.all():
            newcharge = charge_map[charge.id]
            for cc in charge.chargeclassification_set.all():
                newclassification = classification_map[cc.classification.id]
                ncc = ChargeClassification.objects.create(
                    charge=newcharge,
                    classification=newclassification,
                    certainty=cc.certainty,
                    )

        # and classifications -> consequences

        for classification in self.classification_set.all():
            newclassification = classification_map[classification.id]
            for cc in classification.classificationconsequence_set.all():
                newconsequence = consequence_map[cc.consequence.id]
                newcc = ClassificationConsequence.objects.create(classification=newclassification,
                                                                 consequence=newconsequence)

        return new_snapshot

    def top_level_charges(self):
        """ charges that don't have any parents """
        all_children = [c.child for c in ChargeChildren.objects.all()]
        return [c for c in self.charge_set.all().order_by("penal_code") if c not in all_children]

    def get_charge_by_slugs(self,slugs,acc=None):
        if acc is None: acc = []
        if len(acc) > 0:
            parent = acc[-1]
            children = parent.children()
            current = None
            for child in children:
                if child.name == slugs[0]:
                    current = child
            if current is None:
                raise Http404
        else:
            current = get_object_or_404(Charge,snapshot=self,name=slugs[0])

        if len(slugs) == 1:
            return current
        else:
            return self.get_charge_by_slugs(slugs[1:],acc.append(current))

def public_snapshot():
    return Snapshot.objects.filter(status='vetted').order_by("-modified")[0]

def working_snapshot():
    # should only ever be one in progress
    try:
        return Snapshot.objects.filter(status="in progress")[0]
    except Snapshot.DoesNotExist:
        return None

def is_working_snapshot():
    return Snapshot.objects.filter(status="in progress").count() == 1

def qa_snapshot():
    return Snapshot.objects.filter(status="qa")[0]

class Event(models.Model):
    snapshot = models.ForeignKey(Snapshot)
    user = models.ForeignKey(User)
    description = models.TextField()
    created = models.DateTimeField(auto_now=True)
    note = models.TextField(default="",blank=True)

class Charge(models.Model):
    label = models.CharField(max_length=256)
    # maybe rename this, as some charges will be non penal code:
    penal_code = models.CharField(max_length=256)
    snapshot = models.ForeignKey(Snapshot)
    name = models.SlugField()

    def __unicode__(self):
        return self.label

    def get_absolute_url(self):
        parents = self.parents()
        if len(parents) == 0:
            return "/charge/%s/" % self.name
        else:
            return "/charge/" + "/".join([p.name for p in parents]) + "/" + self.name + "/"

    def clone_to(self,new_snapshot):
        return Charge.objects.create(snapshot=new_snapshot,label=self.label,
                                     penal_code=self.penal_code,name=self.name)

    def children(self):
        return [cc.child for cc in ChargeChildren.objects.filter(parent=self)]

    def parents(self,acc=None):
        if acc is None: acc = []
        try:
            ps = ChargeChildren.objects.get(child=self).parent
            acc.append(ps)
            return ps.parents(acc)
        except ChargeChildren.DoesNotExist:
            acc.reverse()
            return acc

    def add_classification_form(self):
        class AddClassificationForm(forms.Form):
            classification_id = forms.IntegerField(
                widget=forms.Select(choices=[(c.id,c.label) for c in self.no()])
                )
            certainty = forms.CharField(
                widget=forms.Select(choices=[('yes','Yes'),
                                             ('probably','Probably'),
                                             ('maybe','Maybe')]))
            comment = forms.CharField(widget=forms.Textarea)
        f = AddClassificationForm()
        return f

    def yes(self):
        return self.chargeclassification_set.filter(certainty="yes")

    def probably(self):
        return self.chargeclassification_set.filter(certainty="probably")

    def maybe(self):
        return self.chargeclassification_set.filter(certainty="maybe")

    def no(self):
        """ return all classifications that this charge is not attached to at all """
        all_classifications = self.all_classifications()
        return [c for c in self.snapshot.classification_set.all() if c not in all_classifications]

    def all_classifications(self):
        return [cc.classification for cc in self.chargeclassification_set.all()]

class ChargeChildren(models.Model):
    parent = models.ForeignKey(Charge,related_name="parent")
    child = models.ForeignKey(Charge,related_name="child")
    # ordering is always by penal_code

class Classification(models.Model):
    snapshot = models.ForeignKey(Snapshot)
    label = models.CharField(max_length=256)
    name = models.SlugField()
    description = models.TextField()

    def __unicode__(self):
        return self.label

    def get_absolute_url(self):
        return "/classification/%s/" % self.name

    def clone_to(self,new_snapshot):
        return Classification.objects.create(snapshot=new_snapshot,
                                             label=self.label,name=self.name,
                                             description=self.description)


    def yes(self):
        return self.chargeclassification_set.filter(certainty="yes")

    def probably(self):
        return self.chargeclassification_set.filter(certainty="probably")

    def maybe(self):
        return self.chargeclassification_set.filter(certainty="maybe")

    def no(self):
        """ return all charges that this classification is not attached to at all """
        all_charges = self.all_charges()
        return [c for c in self.snapshot.charge_set.all() if c not in all_charges]

    def all_charges(self):
        return [cc.charge for cc in self.chargeclassification_set.all()]

    def consequences(self):
        return [cc.consequence for cc in self.classificationconsequence_set.all()]


class Area(models.Model):
    snapshot = models.ForeignKey(Snapshot)
    label = models.CharField(max_length=256)
    name = models.SlugField()

    def __unicode__(self):
        return self.label

    def get_absolute_url(self):
        return "/area/%s/" % self.name

    def clone_to(self,new_snapshot):
        return Area.objects.create(snapshot=new_snapshot,label=self.label,
                                   name=self.name)

class Consequence(models.Model):
    label = models.CharField(max_length=256)
    description = models.TextField()
    area = models.ForeignKey(Area)
    name = models.SlugField()

    def __unicode__(self):
        return self.label

    def get_absolute_url(self):
        return self.area.get_absolute_url() + self.name + "/"

    def clone_to(self,new_area):
        return Consequence.objects.create(area=new_area,label=self.label,
                                          description=self.description,
                                          name=self.name)

    def add_classification_form(self):
        class AddClassificationForm(forms.Form):
            classification_id = forms.IntegerField(
                widget=forms.Select(choices=[(c.id,c.label) for c in self.no()])
                )
            comment = forms.CharField(widget=forms.Textarea)
        f = AddClassificationForm()
        return f

    def no(self):
        """ return list of classifications that are *not* 
        associated with this consequence """
        allclassifications = [cc.classification for cc in self.classificationconsequence_set.all()]
        return [c for c in Classification.objects.filter(snapshot=self.area.snapshot) if c not in allclassifications]


class ChargeClassification(models.Model):
    charge = models.ForeignKey(Charge)
    classification = models.ForeignKey(Classification)
    certainty = models.CharField(max_length=16,
                                 choices=(('yes','Yes'),
                                          ('probably','Probably'),
                                          ('maybe','Maybe')))

class ClassificationChild(models.Model):
    parent = models.ForeignKey(Classification,related_name="parent")
    child = models.ForeignKey(Classification,related_name="child")
    ordinality = models.IntegerField(default=1)

class ClassificationConsequence(models.Model):
    classification = models.ForeignKey(Classification)
    consequence = models.ForeignKey(Consequence)
    ordinality = models.IntegerField(default=1)


