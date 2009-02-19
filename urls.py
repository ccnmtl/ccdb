from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
import os.path
admin.autodiscover()

site_media_root = os.path.join(os.path.dirname(__file__),"media")

urlpatterns = patterns('',
                       ('^$','ccdb.law.views.index'),
                       ('^edit/$','ccdb.law.views.edit_index'),
                       ('^edit/snapshots/$','ccdb.law.views.edit_snapshots'),
                       ('^edit/snapshots/(?P<id>\d+)/$','ccdb.law.views.edit_snapshot'),
                       ('^edit/snapshots/(?P<id>\d+)/clone/$','ccdb.law.views.clone_snapshot'),
                       ('^edit/snapshots/(?P<id>\d+)/approve/$','ccdb.law.views.approve_snapshot'),

                       ('^edit/charge/$','ccdb.law.views.edit_charge_index'),
                       ('^edit/charge/(?P<slugs>.*)add_charge/$','ccdb.law.views.add_charge'),
                       ('^edit/charge/(?P<slugs>.*)remove_classification/(?P<classification_id>\d+)/$','ccdb.law.views.remove_charge_classification'),
                       ('^edit/charge/(?P<slugs>.*)add_classification/$','ccdb.law.views.add_charge_classification'),
                       ('^edit/charge/(?P<slugs>.+)/$','ccdb.law.views.edit_charge'),

                       ('^edit/classification/$','ccdb.law.views.edit_classification_index'),
                       ('^edit/classification/add/$','ccdb.law.views.add_classification'),
                       ('^edit/classification/(?P<slug>[^\/]+)/$','ccdb.law.views.edit_classification'),

                       ('^edit/area/$','ccdb.law.views.edit_area_index'),
                       ('^edit/area/add/$','ccdb.law.views.add_area'),
                       ('^edit/area/(?P<slug>[^\/]+)/$','ccdb.law.views.edit_area'),


                       ('^accounts/',include('djangowind.urls')),
                       (r'^admin/(.*)', admin.site.root),
                       (r'^site_media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': site_media_root}),
                       (r'^uploads/(?P<path>.*)$','django.views.static.serve',{'document_root' : settings.MEDIA_ROOT}),
)
