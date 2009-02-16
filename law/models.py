from django.db import models
from django.contrib.auth.models import User

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

    def cloneable(self):
        return self.is_most_recent_vetted() and \
            Snapshot.objects.exclude(status="vetted").count() == 0

    def get_absolute_url(self):
        return "/snapshots/%d/" % self.id

    def clone_to(self,new_snapshot):
        group_map = dict()
        area_map = dict()
        classification_map = dict()
        for group in self.group_set.all():
            ng = group.clone_to(new_snapshot)
            group_map[group.id] = ng
        for area in self.area_set.all():
            na = area.clone_to(new_snapshot)
            area_map[area.id] = na
        for classification in self.classification_set.all():
            nc = classification.clone_to(new_snapshot)
            classification_map[classification.id] = nc

def public_snapshot():
    return Snapshot.objects.filter(status='vetted').order_by("-modified")[0]

def student_snapshot():
    # should only ever be one in progress
    return Snapshot.objects.filter(status="in progress")[0]

def qa_snapshot():
    return Snapshot.objects.filter(status="qa")[0]

class Event(models.Model):
    snapshot = models.ForeignKey(Snapshot)
    user = models.ForeignKey(User)
    description = models.TextField()
    created = models.DateTimeField(auto_now=True)
    note = models.TextField(default="",blank=True)

class Group(models.Model):
    snapshot = models.ForeignKey(Snapshot)
    label = models.CharField(max_length=256)
    penal_code = models.CharField(max_length=256)
    name = models.SlugField()

    def __unicode__(self):
        return self.label

    def get_absolute_url(self):
        return "/group/%s/" % self.name

    def clone_to(self,new_snapshot):
        return Group.objects.create(snapshot=new_snapshot,
                                    label=self.label,penal_code=self.penal_code,
                                    name=self.name)

class Menu(models.Model):
    label = models.CharField(max_length=256)
    penal_code = models.CharField(max_length=256)
    group = models.ForeignKey(Group)
    name = models.SlugField()

    def __unicode__(self):
        return self.label

    def get_absolute_url(self):
        return "/menu/%s/" % self.name

    def clone_to(self,new_group):
        return Menu.objects.create(group=new_group,label=self.label,
                                   penal_code=self.penal_code,
                                   name=self.name)


class Charge(models.Model):
    offense = models.CharField(max_length=256)
    penal_code = models.CharField(max_length=256)
    degree = models.IntegerField(default=0)
    paragraph = models.IntegerField(default=0)
    menu = models.ForeignKey(Menu)
    name = models.SlugField()

    def __unicode__(self):
        return self.label

    def get_absolute_url(self):
        return "/charge/%s/" % self.name

    def clone_to(self,new_menu):
        return Charge.objects.create(menu=new_menu,offense=self.offense,
                                     penal_code=self.penal_code,degree=self.degree,
                                     paragraph=self.paragraph,name=self.name)

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
        return "/consequence/%s/" % self.name

    def clone_to(self,new_area):
        return Consequence.objects.create(area=new_area,label=self.label,
                                          description=self.description,
                                          name=self.name)


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


