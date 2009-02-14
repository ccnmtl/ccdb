from law.models import *
from django.contrib import admin

class ChargeAdmin(admin.ModelAdmin):
    prepopulated_fields = {"name": ("offense","degree","paragraph")}


admin.site.register(Charge,ChargeAdmin)

class MenuAdmin(admin.ModelAdmin):
    prepopulated_fields = {"name": ("label",)}

admin.site.register(Menu,MenuAdmin)

class GroupAdmin(admin.ModelAdmin):
    prepopulated_fields = {"name": ("label",)}

admin.site.register(Group,GroupAdmin)

class ClassificationAdmin(admin.ModelAdmin):
    prepopulated_fields = {"name": ("label",)}

admin.site.register(Classification,ClassificationAdmin)

class ConsequenceAdmin(admin.ModelAdmin):
    prepopulated_fields = {"name": ("label",)}

admin.site.register(Consequence,ConsequenceAdmin)

class AreaAdmin(admin.ModelAdmin):
    prepopulated_fields = {"name": ("label",)}

admin.site.register(Area,AreaAdmin)
