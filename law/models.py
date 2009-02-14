from django.db import models

class Group(models.Model):
    slug = models.SlugField()
    label = models.CharField(max_length=256)
    penal_code = models.CharField(max_length=256)

class Menu(models.Model):
    slug = models.SlugField()
    label = models.CharField(max_length=256)
    penal_code = models.CharField(max_length=256)
    group = models.ForeignKey(Group)

class Charge(models.Model):
    slug = models.SlugField()
    offense = models.CharField(max_length=256)
    penal_code = models.CharField(max_length=256)
    degree = models.IntegerField(default=0)
    paragraph = models.IntegerField(default=0)
    menu = models.ForeignKey(Menu)

class Classification(models.Model):
    slug = models.SlugField()
    label = models.CharField(max_length=256)

class Area(models.Model):
    slug = models.SlugField()
    label = models.CharField(max_length=256)

class Consequence(models.Model):
    slug = models.SlugField()
    label = models.CharField(max_length=256)
    description = models.TextField()
    area = models.ForeignKey(Area)

class ChargeClassification(models.Model):
    charge = models.ForeignKey(Charge)
    classification = models.ForeignKey(Classification)
    certainty = models.CharField(max_length=16,choices=('yes','probably','maybe'))

class ClassificationChild(models.Model):
    parent = models.ForeignKey(Classification)
    child = models.ForeignKey(Classification)
    ordinality = models.IntegerKey(default=1)

class ClassificationConsequence(models.Model):
    classification = models.ForeignKey(Classification)
    consequence = models.ForeignKey(Consequence)
    ordinality = models.IntegerKey(default=1)


