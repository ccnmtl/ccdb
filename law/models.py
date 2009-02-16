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

class Menu(models.Model):
    label = models.CharField(max_length=256)
    penal_code = models.CharField(max_length=256)
    group = models.ForeignKey(Group)
    name = models.SlugField()

    def __unicode__(self):
        return self.label

    def get_absolute_url(self):
        return "/menu/%s/" % self.name


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


class Classification(models.Model):
    snapshot = models.ForeignKey(Snapshot)
    label = models.CharField(max_length=256)
    name = models.SlugField()
    description = models.TextField()

    def __unicode__(self):
        return self.label

    def get_absolute_url(self):
        return "/classification/%s/" % self.name


class Area(models.Model):
    snapshot = models.ForeignKey(Snapshot)
    label = models.CharField(max_length=256)
    name = models.SlugField()

    def __unicode__(self):
        return self.label

    def get_absolute_url(self):
        return "/area/%s/" % self.name


class Consequence(models.Model):
    label = models.CharField(max_length=256)
    description = models.TextField()
    area = models.ForeignKey(Area)
    name = models.SlugField()

    def __unicode__(self):
        return self.label

    def get_absolute_url(self):
        return "/consequence/%s/" % self.name


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


