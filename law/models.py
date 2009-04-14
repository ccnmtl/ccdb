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

    def clear(self):
        for charge in self.charge_set.all():
            charge.delete()
        for classification in self.classification_set.all():
            classification.delete()
        for area in self.area_set.all():
            area.delete()
        for event in self.event_set.all():
            event.delete()

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
            for ca in charge.chargearea_set.all():
                newarea = area_map[ca.area.id]
                nca = ChargeArea.objects.create(
                    charge=newcharge,
                    area=newarea)

        # and classifications -> consequences

        for classification in self.classification_set.all():
            newclassification = classification_map[classification.id]
            for cc in classification.classificationconsequence_set.all():
                newconsequence = consequence_map[cc.consequence.id]
                newcc = ClassificationConsequence.objects.create(classification=newclassification,
                                                                 consequence=newconsequence,
                                                                 certainty=cc.certainty)


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
            options = Charge.objects.filter(snapshot=self,name=slugs[0])
            if options.count() == 1:
                current = get_object_or_404(Charge,snapshot=self,name=slugs[0])
            else:
                print "Multiple charges found with the same slug"
                for c in options:
                    print c.id,c.name,c.label
                raise "Oh No!!!"

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

    class Meta:
        ordering = ('penal_code','label')

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
        return [cc.child for cc in ChargeChildren.objects.filter(parent=self).order_by('child__penal_code')]

    def parents(self,acc=None):
        if acc is None: acc = []
        try:
            ps = ChargeChildren.objects.get(child=self).parent
            acc.append(ps)
            return ps.parents(acc)
        except ChargeChildren.DoesNotExist:
            acc.reverse()
            return acc

    def siblings(self):
        try:
            ps = ChargeChildren.objects.get(child=self).parent
            return [c for c in ps.children() if c.id != self.id]
        except ChargeChildren.DoesNotExist:
            return []

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
        return list(self.chargeclassification_set.filter(certainty="yes"))


    # these are a little harder, since they need to handle the situation
    # where the certainty of the chargeclassification is different
    # than the certainty of the classificationconsequence and duplicate
    # those in the lesser column

    # when using the results of these later on, make sure that
    # instead of looping over cc.classification.classificationconsequence_set.all()
    # results, you use cc.classification.yes_consequences() etc (matching the certainty)

    def probably(self):
        plain = list(self.chargeclassification_set.filter(certainty="probably"))
        
        # also include any Charge -> YES -> Classification -> PROBABLY -> Consequences
        for cc in self.yes():
            if cc.classification.classificationconsequence_set.filter(certainty="probably").count() > 0:
                plain.append(cc)
        return plain

    def maybe(self):
        plain = list(self.chargeclassification_set.filter(certainty="maybe"))
        # also include any Charge -> YES -> Classification -> MAYBE -> Consequences
        for cc in self.yes():
            if cc.classification.classificationconsequence_set.filter(certainty="maybe").count() > 0:
                plain.append(cc)
        # also include any Charge -> PROBABLY -> Classification -> MAYBE -> Consequences
        for cc in self.probably():
            if cc.classification.classificationconsequence_set.filter(certainty="probably").count() > 0:
                plain.append(cc)
        return plain

    def all_yes(self):
        """ include parents """
        results = self.yes()
        classifications = [cc.classification for cc in results]
        for p in self.parents():
            for cc in p.yes():
                if cc.classification not in classifications:
                    results.append(cc)
                    classifications.append(cc.classification)
        return results

    def all_probably(self):
        """ include parents """
        results = self.probably()
        classifications = [cc.classification for cc in results]
        for p in self.parents():
            for cc in p.probably():
                if cc.classification not in classifications:
                    results.append(cc)
                    classifications.append(cc.classification)
        return results

    def all_maybe(self):
        """ include parents """
        results = self.maybe()
        classifications = [cc.classification for cc in results]
        for p in self.parents():
            for cc in p.maybe():
                if cc.classification not in classifications:
                    results.append(cc)
                    classifications.append(cc.classification)
        return results

    def view_yes(self):
        """ show yes results only in areas that have been vetted """
        r = self.all_yes()
        areas = self.yes_areas()
        return [cc for cc in r if cc.classification.in_areas(areas)]

    def view_probably(self):
        """ show yes results only in areas that have been vetted """
        r = self.all_probably()
        areas = self.yes_areas()
        return [cc for cc in r if cc.classification.in_areas(areas)]

    def view_maybe(self):
        """ show yes results only in areas that have been vetted """
        r = self.all_maybe()
        areas = self.yes_areas()
        return [cc for cc in r if cc.classification.in_areas(areas)]

    def view_all(self):
        """ show yes results only in areas that have been vetted """
        maybe = self.all_maybe()
        probably = self.all_probably()
        yes = self.all_yes()
        r = list(maybe) + list(probably) + list(yes)
        areas = self.yes_areas()
        return [cc for cc in r if cc.classification.in_areas(areas)]


    def no(self):
        """ return all classifications that this charge is not attached to at all """
        all_classifications = self.all_classifications()
        return [c for c in self.snapshot.classification_set.all() if c not in all_classifications]

    def all_classifications(self):
        return [cc.classification for cc in self.chargeclassification_set.all()]

    def delete_self(self):
        for child in self.children():
            child.delete_self()
        self.delete()

    def add_area_form(self):
        class AddAreaForm(forms.Form):
            area_id = forms.IntegerField(
                widget=forms.Select(choices=[(a.id,a.label) for a in self.no_areas()])
                )
            comment = forms.CharField(widget=forms.Textarea)
        f = AddAreaForm()
        return f

    def yes_areas(self):
        return [ca.area for ca in self.chargearea_set.all()]

    def no_areas(self):
        """ list the areas that this charge does not show consequences for """
        yes = self.yes_areas()
        return [area for area in Area.objects.filter(snapshot=self.snapshot) if area not in yes]

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

    def add_consequence_form(self):
        class AddConsequenceForm(forms.Form):
            consequence_id = forms.IntegerField(
                widget=forms.Select(choices=[(c.id,"%s: %s" % (c.area.label,c.label)) for c in self.no_consequences()])
                )
            certainty = forms.CharField(
                widget=forms.Select(choices=[('yes','Yes'),
                                             ('probably','Probably'),
                                             ('maybe','Maybe')])
                )
            comment = forms.CharField(widget=forms.Textarea)
        f = AddConsequenceForm()
        return f

    def yes_consequences(self):
        return self.classificationconsequence_set.filter(certainty="yes")

    def probably_consequences(self):
        return self.classificationconsequence_set.filter(certainty="probably")

    def maybe_consequences(self):
        return self.classificationconsequence_set.filter(certainty="maybe")


    def all_probably_consequences(self):
        """ include the yes ones too """
        return list(self.probably_consequences()) + list(self.yes_consequences())

    def all_maybe_consequences(self):
        return list(self.maybe_consequences()) + list(self.all_probably_consequences())
    
    def no_consequences(self):
        """ return list of consequences that are *not* 
        associated with this classification """
        allconsequences = [cc.consequence for cc in self.classificationconsequence_set.all()]
        return [c for c in Consequence.objects.filter(area__snapshot=self.snapshot) if c not in allconsequences]
        
    def in_areas(self,areas):
        in_all = True
        for consequence in self.consequences():
            if consequence.area not in areas:
                in_all = False
        return in_all

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
            certainty = forms.CharField(
                widget=forms.Select(choices=[('yes','Yes'),
                                             ('probably','Probably'),
                                             ('maybe','Maybe')])
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
    certainty = models.CharField(max_length=16,
                                 choices=(('yes','Yes'),
                                          ('probably','Probably'),
                                          ('maybe','Maybe')),
                                 default="yes")


class ChargeArea(models.Model):
    """ if one of these exists, the specified charge
    will show consequences in the specified area """
    charge = models.ForeignKey(Charge)
    area = models.ForeignKey(Area)
