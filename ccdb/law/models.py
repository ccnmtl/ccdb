from django.db import models
from django.contrib.auth.models import User
from django.http import Http404
from django.shortcuts import get_object_or_404
from django import forms
import re


class Snapshot(models.Model):
    label = models.CharField(max_length=256)
    description = models.TextField(default="", blank=True)
    status = models.CharField(max_length=256,
                              choices=[('in progress', 'In Progress'),
                                       ('qa', 'In QA'),
                                       ('vetted', 'Vetted')],
                              default="in progress")
    created = models.DateTimeField(auto_now=True)
    modified = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.label

    def dump_filename_base(self):
        """ filename base for json/zip dumps """
        datestring = "%04d-%02d-%02dT%02d:%02d:%02d" % (
            self.created.year, self.created.month,
            self.created.day, self.created.hour,
            self.created.minute, self.created.second)
        return "%04d-%s" % (self.id, datestring)

    def to_json(self):
        return dict(
            label=self.label,
            description=self.description,
            status=self.status,
            created=str(self.created),
            modified=str(self.modified),
            id=self.id,
            charges=[c.to_json() for c in self.charge_set.all()
                     if not c.has_children()])

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

    def clone_charges(self, new_snapshot):
        charge_map = dict()
        for charge in self.charge_set.all():
            nc = charge.clone_to(new_snapshot)
            charge_map[charge.id] = nc
        return charge_map

    def clone_areas(self, new_snapshot):
        area_map = dict()
        consequence_map = dict()
        for area in self.area_set.all():
            na = area.clone_to(new_snapshot)
            area_map[area.id] = na
            for consequence in area.consequence_set.all():
                new_consequence = consequence.clone_to(na)
                consequence_map[consequence.id] = new_consequence
        return area_map, consequence_map

    def clone_parent_child_relationships(self, charge_map):
        # clone parent-child relationships
        for charge in self.charge_set.all():
            newparent = charge_map[charge.id]
            for cc in ChargeChildren.objects.filter(parent=charge):
                newchild = charge_map[cc.child.id]
                ChargeChildren.objects.create(parent=newparent,
                                              child=newchild)

    def clone(self, label, user, description=""):
        new_snapshot = Snapshot.objects.create(label=label,
                                               description=description)
        Event.objects.create(snapshot=new_snapshot, user=user,
                             description="snapshot created")

        charge_map = self.clone_charges(new_snapshot)
        area_map, consequence_map = self.clone_areas(new_snapshot)
        classification_map = dict()

        for classification in self.classification_set.all():
            nc = classification.clone_to(new_snapshot)
            classification_map[classification.id] = nc

        self.clone_parent_child_relationships(charge_map)

        # clone charges -> classifications

        for charge in self.charge_set.all():
            newcharge = charge_map[charge.id]
            for cc in charge.chargeclassification_set.all():
                newclassification = classification_map[cc.classification.id]
                ChargeClassification.objects.create(
                    charge=newcharge,
                    classification=newclassification,
                    certainty=cc.certainty)
            for ca in charge.chargearea_set.all():
                newarea = area_map[ca.area.id]
                ChargeArea.objects.create(
                    charge=newcharge,
                    area=newarea)

        # and classifications -> consequences

        for classification in self.classification_set.all():
            newclassification = classification_map[classification.id]
            for cc in classification.classificationconsequence_set.all():
                newconsequence = consequence_map[cc.consequence.id]
                ClassificationConsequence.objects.create(
                    classification=newclassification,
                    consequence=newconsequence,
                    certainty=cc.certainty)
        return new_snapshot

    def all_chargechildren(self):
        if hasattr(self, '__chargechildren_cache'):
            return self.__chargechildren_cache
        self.__chargechildren_cache = list(ChargeChildren.objects.all())
        return self.__chargechildren_cache

    def top_level_charges(self):
        """ charges that don't have any parents """
        all_children = set([c.child_id for c in self.all_chargechildren()])
        return [c for c in self.charge_set.all().order_by('numeric_penal_code',
                                                          'penal_code')
                if c.id not in all_children]

    def get_charge_by_slugs(self, slugs, acc=None):
        if acc is None:
            acc = []
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
            options = Charge.objects.filter(snapshot=self, name=slugs[0])
            if options.count() <= 1:
                current = get_object_or_404(Charge, snapshot=self,
                                            name=slugs[0])
            else:
                # technically, this is bad. we shouldn't let there be two
                # charges with the same name, but what can you do?
                current = options[0]

        if len(slugs) == 1:
            return current
        else:
            return self.get_charge_by_slugs(slugs[1:], acc.append(current))


def public_snapshot():
    return Snapshot.objects.filter(status='vetted').order_by("-modified")[0]


def working_snapshot():
    # should only ever be one in progress
    return Snapshot.objects.filter(status="in progress").first()


def is_working_snapshot():
    return Snapshot.objects.filter(status="in progress").count() == 1


def qa_snapshot():
    return Snapshot.objects.filter(status="qa")[0]


class Event(models.Model):
    snapshot = models.ForeignKey(Snapshot)
    user = models.ForeignKey(User)
    description = models.TextField()
    created = models.DateTimeField(auto_now=True)
    note = models.TextField(default="", blank=True)


class Charge(models.Model):
    label = models.CharField(max_length=256)
    # maybe rename this, as some charges will be non penal code:
    penal_code = models.CharField(max_length=256)
    snapshot = models.ForeignKey(Snapshot, editable=False)
    name = models.SlugField(
        help_text="""unique identifier that appears in the URL. """
        """must be less than 50 characters long """
        """and no two charges can have the same name""")
    # for sorting purposes
    numeric_penal_code = models.FloatField(editable=False, blank=True,
                                           null=True)
    description = models.TextField(
        blank=True, null=True, default="",
        help_text=("""tips/strategies. if this is empty, it will inherit """
                   """from its parent Charge"""))

    class Meta:
        ordering = ('numeric_penal_code', 'penal_code', 'label')

    def save(self, *args, **kwargs):
        if not self.numeric_penal_code:
            self.numeric_penal_code = float(re.findall('\d+\.?\d*',
                                                       self.penal_code)[0])
        # Call the "real" save() method.
        return super(Charge, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.label

    def get_absolute_url(self):
        parents = self.parents()
        if len(parents) == 0:
            return "/charge/%s/" % self.name
        else:
            return ("/charge/" +
                    "/".join([p.name for p in parents]) +
                    "/" + self.name + "/")

    def to_json(self):
        return dict(
            label=self.label,
            penal_code=self.penal_code,
            slug=self.name,
            numeric_penal_code=self.numeric_penal_code,
            description=self.description,
            consequences=self.all_consequences_by_area_json())

    def get_description(self):
        """ inherit description from parent if it isn't set """
        if self.description != "":
            return self.description
        parents = self.parents()
        if len(parents) == 0:
            return ""
        else:
            return parents[-1].get_description()

    def clone_to(self, new_snapshot):
        return Charge.objects.create(
            snapshot=new_snapshot, label=self.label,
            penal_code=self.penal_code, name=self.name,
            description=self.description,
            numeric_penal_code=self.numeric_penal_code)

    def children(self):
        return [cc.child for cc in
                ChargeChildren.objects.filter(parent=self).order_by(
                    'child__numeric_penal_code', 'child__penal_code')]

    def has_children(self):
        return ChargeChildren.objects.filter(parent=self).count() > 0

    def has_parents(self):
        return ChargeChildren.objects.filter(child=self).count() > 0

    def is_leaf(self):
        return not self.has_children()

    def as_edit_ul(self):
        """ return html for the charge and its children as an <ul> """
        return self.as_ul(link_prefix="/edit", hs=False)

    def as_view_ul(self):
        """ return html for the charge and its children as an <ul> """
        return self.as_ul(link_prefix="", hs=True)

    def as_ul(self, link_prefix="", hs=True):
        """ return html for the charge and its children as an <ul> """
        leaf = not self.has_children()

        if leaf:
            link = ("<span class=\"charge\" href=\"" + link_prefix +
                    self.get_absolute_url() + "\"></span>")
        else:
            if not hs:
                link = ("<a href=\"" + link_prefix +
                        self.get_absolute_url() + "\">")
            else:
                link = ("<a href=\"#charge-" + str(self.id) +
                        "\" class=\"" + "hs-control" + "\">")
        parts = ["<li class=\"menuitem leaf\">", link, self.penal_code, " ",
                 self.label, "</a>"]

        if not leaf:
            hsclass = "hs-init-hide"
            if not hs:
                hsclass = ""
            parts.append("<ul id=\"charge-" + str(self.id) + "\" class=\"" +
                         hsclass + " menu\">")
            for child in self.children():
                parts.append(child.as_ul(link_prefix=link_prefix, hs=hs))
            parts.append("</ul>")
        parts.append("</li>")
        return "".join(parts)

    # Blech. Should convert this to the pagetree approach
    # where menus can be edited in a template instead of here
    def as_view_compare_ul(self):
        """ return html for the charge and its children as an <ul> """
        return self.as_compare_ul(link_prefix="")

    def as_compare_ul(self, link_prefix=""):
        """ return html for the charge and its children as an <ul> """
        leaf = not self.has_children()

        if leaf:
            link = ("<span class=\"compare\" href=\"?charge2=" +
                    self.get_absolute_url() + "\"></span>")
        else:
            link = ("<a href=\"#compare-charge-" + str(self.id) +
                    "\" class=\"hs-control\">")
        parts = ["<li class=\"menuitem\">", link, self.penal_code, " ",
                 self.label, "</a>"]

        if not leaf:
            parts.append("<ul id=\"compare-charge-" + str(self.id) +
                         "\" class=\"hs-init-hide menu\">")
            for child in self.children():
                parts.append(child.as_compare_ul(link_prefix=link_prefix))
            parts.append("</ul>")
        parts.append("</li>")
        return "".join(parts)

    def parents(self, acc=None):
        if acc is None:
            acc = []
        try:
            ps = ChargeChildren.objects.get(child=self).parent
            acc.append(ps)
            return ps.parents(acc)
        except ChargeChildren.DoesNotExist:
            acc.reverse()
            return acc

    def rparents(self):
        p = self.parents()
        p.reverse()
        return p

    def siblings(self):
        try:
            ps = ChargeChildren.objects.get(child=self).parent
            return [c for c in ps.children() if c.id != self.id]
        except ChargeChildren.DoesNotExist:
            return []

    def add_classification_form(self):
        class AddClassificationForm(forms.Form):
            classification_id = forms.IntegerField(
                widget=forms.Select(
                    choices=[(c.id, c.label) for c in self.no()]))
            certainty = forms.CharField(
                widget=forms.Select(choices=[('yes', 'Yes'),
                                             ('probably', 'Probably'),
                                             ('maybe', 'Maybe')]))
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
    # instead of looping over
    # cc.classification.classificationconsequence_set.all()
    # results, you use cc.classification.yes_consequences() etc
    # (matching the certainty)

    def probably(self):
        plain = list(
            self.chargeclassification_set.filter(
                certainty="probably"))
        # also include any Charge -> YES -> Classification -> PROBABLY
        #   -> Consequences
        for cc in self.yes():
            if cc.classification.classificationconsequence_set.filter(
                    certainty="probably").count() > 0:
                plain.append(cc)
        return plain

    def maybe(self):
        plain = list(self.chargeclassification_set.filter(certainty="maybe"))
        # also include any Charge -> YES -> Classification -> MAYBE
        #   -> Consequences
        for cc in self.yes():
            if cc.classification.classificationconsequence_set.filter(
                    certainty="maybe").count() > 0:
                plain.append(cc)
        # also include any Charge -> PROBABLY -> Classification -> MAYBE
        #   -> Consequences
        for cc in self.probably():
            if cc.classification.classificationconsequence_set.filter(
                    certainty="probably").count() > 0:
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
        """ return all classifications that this charge is
        not attached to at all """
        all_classifications = self.all_classifications()
        return [c for c in
                self.snapshot.classification_set.all().order_by("label")
                if c not in all_classifications]

    def all_classifications(self):
        return [cc.classification for cc in
                self.chargeclassification_set.all()]

    def delete_self(self):
        for child in self.children():
            child.delete_self()
        self.delete()

    def add_area_form(self):
        class AddAreaForm(forms.Form):
            area_id = forms.IntegerField(
                widget=forms.Select(
                    choices=[(a.id, a.label) for a in self.no_areas()]))
            comment = forms.CharField(widget=forms.Textarea)
        f = AddAreaForm()
        return f

    def yes_areas(self):
        parent_areas = []
        for p in self.parents():
            pa = p.yes_areas()
            if len(pa) > 0:
                for a in pa:
                    parent_areas.append(a)
        return [ca.area for ca in self.chargearea_set.all()] + parent_areas

    def yes_areas_for_edit_page(self):
        """ same thing but we add a flag to indicate whether
        it's directly attached or comes down via inheritance """
        parent_areas = []
        for p in self.parents():
            pa = p.yes_areas()
            if len(pa) > 0:
                for a in pa:
                    parent_areas.append(a)
        direct = dict()
        for ca in self.chargearea_set.all():
            direct[ca.area.id] = ca
        all_yes_areas = [ca.area for ca in
                         self.chargearea_set.all()] + parent_areas
        all_yes_areas = list(set(all_yes_areas))
        return [dict(area=area,
                     ca=direct.get(area.id, None)) for area in all_yes_areas]

    def no_areas(self):
        """ list the areas that this charge does not show consequences for """
        yes = self.yes_areas()
        return [area for area in Area.objects.filter(snapshot=self.snapshot)
                if area not in yes]

    def all_consequences_by_area_json(self):
        """ get a flat json serialized version of the consequences data"""
        data = self.all_consequences_by_area()
        clean_data = []
        for a in data:
            clean_a = dict()
            clean_a['area'] = a['area'].to_json()
            clean_a['yes'] = [
                dict(
                    classification=cc['classification'].to_json(),
                    consequences=[c.consequence.to_json() for c in
                                  cc['consequences']])
                for cc in a['yes']]
            clean_a['probably'] = [
                dict(
                    classification=cc['classification'].to_json(),
                    consequences=[c.consequence.to_json() for c in
                                  cc['consequences']])
                for cc in a['probably']]
            clean_a['maybe'] = [
                dict(
                    classification=cc['classification'].to_json(),
                    consequences=[c.consequence.to_json() for c in
                                  cc['consequences']])
                for cc in a['maybe']]
            clean_data.append(clean_a)
        return clean_data

    def gather_all_consequences(self):
        all_classifications = self.view_all()
        all_consequences = []

        for cc in all_classifications:
            ccs = cc.classification.classificationconsequence_set.all()
            for consequence in ccs:
                all_consequences.append(
                    dict(consequence=consequence,
                         certainty=effective_certainty(cc.certainty,
                                                       consequence.certainty)))
        all_consequences.sort(
            key=lambda x: (x['consequence'].consequence.area.label,
                           x['certainty']))
        return all_consequences

    def all_consequences_by_area(self):
        """ return all consequences for the charge, organized by
        Area -> Certainty. for ease of template display.
        Include ones from parents """

        certainties = ["yes", "probably", "maybe"]
        all_areas = self.snapshot.area_set.all()
        all_consequences = self.gather_all_consequences()

        results = []
        for area in all_areas:
            area_results = dict(area=area)
            for c in certainties:
                area_results[c] = []

            for c in all_consequences:
                if c['consequence'].consequence.area == area:
                    area_results[c['certainty']].append(c['consequence'])

            total_count = 0
            for c in certainties:
                # need to uniquify
                area_results[c] = list(set(area_results[c]))
                area_results[c].sort(key=lambda x: x.consequence.label)
                # stick counts in here
                area_results[c + "_count"] = len(area_results[c])
                total_count += len(area_results[c])
                # still need the consequences grouped by their classification
                area_results[c] = dtolist(
                    cluster_by(lambda x: x.classification, area_results[c]))
            area_results['total_count'] = total_count
            # a convenient flag for the situation when
            # this charge has no consequences in an area *AND* it's vetted
            # for the area
            if total_count == 0 and area in self.yes_areas():
                area_results['no_consequences'] = True
            results.append(area_results)
        return results


def dtolist(d):
    r = []
    for (k, v) in d.items():
        r.append(dict(classification=k, consequences=v))
    return r


def cluster_by(f, lst):
    transformed = [f(x) for x in lst]
    d = dict()
    for t, i in zip(transformed, lst):
        d.setdefault(t, []).append(i)
    return d


class ChargeChildren(models.Model):
    parent = models.ForeignKey(Charge, related_name="parent")
    child = models.ForeignKey(Charge, related_name="child")
    # ordering is always by penal_code


class Classification(models.Model):
    snapshot = models.ForeignKey(Snapshot, editable=False)
    label = models.CharField(max_length=256)
    name = models.SlugField()
    description = models.TextField()

    def __unicode__(self):
        return self.label

    def display_label(self):
        if "[" in self.label:
            return re.sub(r"\s*\[[^\[]+\]", "", self.label)
        else:
            return self.label

    def get_absolute_url(self):
        return "/classification/%s/" % self.name

    def to_json(self):
        return dict(label=self.display_label(),
                    slug=self.name,
                    description=self.description)

    def clone_to(self, new_snapshot):
        return Classification.objects.create(snapshot=new_snapshot,
                                             label=self.label, name=self.name,
                                             description=self.description)

    def yes(self):
        return self.chargeclassification_set.filter(certainty="yes")

    def probably(self):
        return self.chargeclassification_set.filter(certainty="probably")

    def maybe(self):
        return self.chargeclassification_set.filter(certainty="maybe")

    def no(self):
        """ return all charges that this classification is not
        attached to at all """
        all_charges = self.all_charges()
        return [c for c in self.snapshot.charge_set.all()
                if c not in all_charges]

    def all_charges(self):
        return [cc.charge for cc in self.chargeclassification_set.all()]

    def consequences(self):
        return [cc.consequence for cc in
                self.classificationconsequence_set.all().order_by(
                    "consequence__label")]

    def add_consequence_form(self):
        class AddConsequenceForm(forms.Form):
            consequence_id = forms.IntegerField(
                widget=forms.Select(
                    choices=[(c.id, "%s: %s" % (c.area.label, c.label))
                             for c in self.no_consequences()]))
            certainty = forms.CharField(
                widget=forms.Select(choices=[('yes', 'Yes'),
                                             ('probably', 'Probably'),
                                             ('maybe', 'Maybe')]))
            comment = forms.CharField(widget=forms.Textarea)
        f = AddConsequenceForm()
        return f

    def yes_consequences(self):
        return self.classificationconsequence_set.filter(
            certainty="yes").order_by("consequence__label")

    def probably_consequences(self):
        return self.classificationconsequence_set.filter(
            certainty="probably").order_by("consequence__label")

    def maybe_consequences(self):
        return self.classificationconsequence_set.filter(
            certainty="maybe").order_by("consequence__label")

    def all_probably_consequences(self):
        """ include the yes ones too """
        return (list(self.probably_consequences()) +
                list(self.yes_consequences()))

    def all_maybe_consequences(self):
        return (list(self.maybe_consequences()) +
                list(self.all_probably_consequences()))

    def all_consequences(self):
        all_consequences = (list(self.yes_consequences()) +
                            list(self.probably_consequences()) +
                            list(self.maybe_consequences()))
        all_consequences.sort(key=lambda x: x.ordinality)
        return all_consequences

    def no_consequences(self):
        """ return list of consequences that are *not*
        associated with this classification """
        allconsequences = [cc.consequence for cc in
                           self.classificationconsequence_set.all()]
        return [c for c in Consequence.objects.filter(
                area__snapshot=self.snapshot)
                if c not in allconsequences]

    def in_areas(self, areas):
        in_all = True
        for consequence in self.consequences():
            if consequence.area not in areas:
                in_all = False
        return in_all


class Area(models.Model):
    snapshot = models.ForeignKey(Snapshot, editable=False)
    label = models.CharField(max_length=256)
    name = models.SlugField(
        help_text="""unique identifier that appears in the URL. """
        """must be less than 50 characters long """
        """and no two areas can have the same name""")

    def __unicode__(self):
        return self.label

    def get_absolute_url(self):
        return "/area/%s/" % self.name

    def clone_to(self, new_snapshot):
        return Area.objects.create(snapshot=new_snapshot, label=self.label,
                                   name=self.name)

    def to_json(self):
        return dict(label=self.label,
                    slug=self.name,
                    id=self.id)


class Consequence(models.Model):
    label = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    area = models.ForeignKey(Area, editable=False)
    name = models.SlugField()

    def __unicode__(self):
        return self.label

    def display_label(self):
        if "[" in self.label:
            return re.sub(r"\s*\[[^\[]+\]", "", self.label)
        else:
            return self.label

    def to_json(self):
        return dict(label=self.display_label(),
                    description=self.description,
                    slug=self.name)

    def get_absolute_url(self):
        return self.area.get_absolute_url() + self.name + "/"

    def clone_to(self, new_area):
        return Consequence.objects.create(area=new_area, label=self.label,
                                          description=self.description,
                                          name=self.name)

    def add_classification_form(self):
        class AddClassificationForm(forms.Form):
            classification_id = forms.IntegerField(
                widget=forms.Select(
                    choices=[(c.id, c.label) for c in self.no()]))
            certainty = forms.CharField(
                widget=forms.Select(choices=[('yes', 'Yes'),
                                             ('probably', 'Probably'),
                                             ('maybe', 'Maybe')]))
            comment = forms.CharField(widget=forms.Textarea)
        f = AddClassificationForm()
        return f

    def no(self):
        """ return list of classifications that are *not*
        associated with this consequence """
        allclassifications = [cc.classification for cc in
                              self.classificationconsequence_set.all()]
        return [c for c in Classification.objects.filter(
                snapshot=self.area.snapshot).order_by("label")
                if c not in allclassifications]


class ChargeClassification(models.Model):
    charge = models.ForeignKey(Charge)
    classification = models.ForeignKey(Classification)
    certainty = models.CharField(max_length=16,
                                 choices=(('yes', 'Yes'),
                                          ('probably', 'Probably'),
                                          ('maybe', 'Maybe')))


class ClassificationChild(models.Model):
    parent = models.ForeignKey(Classification, related_name="parent")
    child = models.ForeignKey(Classification, related_name="child")
    ordinality = models.IntegerField(default=1)


def effective_certainty(ch_cl_certainty, cl_co_certainty):
    nvals = dict(yes=1, probably=2, maybe=3)
    effective_val = max(nvals[ch_cl_certainty], nvals[cl_co_certainty])
    return ["yes", "probably", "maybe"][effective_val - 1]


class ClassificationConsequence(models.Model):
    classification = models.ForeignKey(Classification)
    consequence = models.ForeignKey(Consequence)
    ordinality = models.IntegerField(default=1)
    certainty = models.CharField(max_length=16,
                                 choices=(('yes', 'Yes'),
                                          ('probably', 'Probably'),
                                          ('maybe', 'Maybe')),
                                 default="yes")


class ChargeArea(models.Model):
    """ if one of these exists, the specified charge
    will show consequences in the specified area """
    charge = models.ForeignKey(Charge)
    area = models.ForeignKey(Area)
