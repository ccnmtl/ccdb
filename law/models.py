from django.db import models

class Group(models.Model):
    label = models.CharField(max_length=256)
    penal_code = models.CharField(max_length=256)
    name = models.SlugField()

class Menu(models.Model):
    label = models.CharField(max_length=256)
    penal_code = models.CharField(max_length=256)
    group = models.ForeignKey(Group)
    name = models.SlugField()

class Charge(models.Model):
    offense = models.CharField(max_length=256)
    penal_code = models.CharField(max_length=256)
    degree = models.IntegerField(default=0)
    paragraph = models.IntegerField(default=0)
    menu = models.ForeignKey(Menu)
    name = models.SlugField()

class Classification(models.Model):
    label = models.CharField(max_length=256)
    name = models.SlugField()
    description = models.TextField()

class Area(models.Model):
    label = models.CharField(max_length=256)
    name = models.SlugField()

class Consequence(models.Model):
    label = models.CharField(max_length=256)
    description = models.TextField()
    area = models.ForeignKey(Area)
    name = models.SlugField()

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


