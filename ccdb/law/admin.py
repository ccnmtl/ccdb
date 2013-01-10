from ccdb.law.models import Charge, Classification, Consequence, Area, Snapshot
from ccdb.law.models import Event
from django.contrib import admin


class ChargeAdmin(admin.ModelAdmin):
    prepopulated_fields = {"name": ("label",)}

admin.site.register(Charge, ChargeAdmin)


class ClassificationAdmin(admin.ModelAdmin):
    prepopulated_fields = {"name": ("label",)}

admin.site.register(Classification, ClassificationAdmin)


class ConsequenceAdmin(admin.ModelAdmin):
    prepopulated_fields = {"name": ("label",)}

admin.site.register(Consequence, ConsequenceAdmin)


class AreaAdmin(admin.ModelAdmin):
    prepopulated_fields = {"name": ("label",)}

admin.site.register(Area, AreaAdmin)


class SnapshotAdmin(admin.ModelAdmin):
    pass

admin.site.register(Snapshot, SnapshotAdmin)


class EventAdmin(admin.ModelAdmin):
    pass

admin.site.register(Event, EventAdmin)
