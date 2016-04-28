from django.conf.urls import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView
import ccdb.law.views as views
import os.path
admin.autodiscover()

site_media_root = os.path.join(os.path.dirname(__file__), "../media")

urlpatterns = patterns(
    '',
    ('^$', views.IndexView.as_view()),
    ('^charge/(?P<slugs>.+)/tips/$', views.ChargeTipsView.as_view()),
    ('^charge/(?P<slugs>.+)/$', views.ChargeView.as_view()),
    ('^classification/(?P<slug>[^\/]+)/$',
     views.ClassificationView.as_view()),
    ('^area/(?P<slug>[^\/]+)/$', views.AreaView.as_view()),
    ('^area/(?P<slug>[^\/]+)/(?P<cslug>[^\/]+)/$',
     views.ConsequenceView.as_view()),

    ('^edit/$', views.EditView.as_view()),
    ('^edit/graph/$', views.GraphView.as_view()),
    ('^edit/snapshots/$', views.EditSnapshotsView.as_view()),
    ('^edit/snapshots/(?P<pk>\d+)/$', views.EditSnapshotView.as_view()),
    ('^edit/snapshots/(?P<id>\d+)/clone/$', views.CloneSnapshotView.as_view()),
    ('^edit/snapshots/(?P<id>\d+)/approve/$',
     views.ApproveSnapshotView.as_view()),
    ('^edit/snapshots/(?P<pk>\d+)/delete/$',
     views.DeleteSnapshotView.as_view()),

    ('^edit/charge/$', 'ccdb.law.views.edit_charge_index'),
    ('^edit/charge/(?P<slugs>.*)add_charge/$', 'ccdb.law.views.add_charge'),
    (('^edit/charge/(?P<slugs>.*)remove_classification/'
      '(?P<classification_id>\d+)/$'),
     'ccdb.law.views.remove_charge_classification'),
    ('^edit/charge/(?P<slugs>.*)add_classification/$',
     'ccdb.law.views.add_charge_classification'),
    ('^edit/charge/(?P<slugs>.*)reparent/$', 'ccdb.law.views.reparent_charge'),
    ('^edit/charge/(?P<slugs>.*)delete/$', 'ccdb.law.views.delete_charge'),
    ('^edit/charge/(?P<slugs>.*)add_area/$',
     'ccdb.law.views.add_area_to_charge'),
    ('^edit/charge/(?P<slugs>.*)remove_area/(?P<ca_id>\d+)/$',
     'ccdb.law.views.remove_area_from_charge'),
    ('^edit/charge/(?P<slugs>.+)/$', 'ccdb.law.views.edit_charge'),

    ('^edit/classification/$', 'ccdb.law.views.edit_classification_index'),
    ('^edit/classification/add/$', 'ccdb.law.views.add_classification'),
    ('^edit/classification/(?P<slug>[^\/]+)/$',
     'ccdb.law.views.edit_classification'),
    ('^edit/classification/(?P<slug>[^\/]+)/preview/$',
     'ccdb.law.views.preview_classification'),
    ('^edit/classification/(?P<slug>[^\/]+)/delete/$',
     'ccdb.law.views.delete_classification'),
    ('^edit/classification/(?P<slug>[^\/]+)/add_consequence/$',
     'ccdb.law.views.add_consequence_to_classification'),
    (('^edit/classification/(?P<slug>[^\/]+)/remove_consequence/'
      '(?P<consequence_id>\d+)/$'),
     'ccdb.law.views.remove_consequence_from_classification'),

    ('^edit/area/$', 'ccdb.law.views.edit_area_index'),
    ('^edit/area/add/$', 'ccdb.law.views.add_area'),
    ('^edit/area/(?P<slug>[^\/]+)/$', 'ccdb.law.views.edit_area'),
    ('^edit/area/(?P<slug>[^\/]+)/delete/$', 'ccdb.law.views.delete_area'),
    ('^edit/area/(?P<slug>[^\/]+)/add_consequence/$',
     'ccdb.law.views.add_consequence'),
    ('^edit/area/(?P<slug>[^\/]+)/(?P<cslug>[^\/]+)/$',
     'ccdb.law.views.edit_consequence'),
    ('^edit/area/(?P<slug>[^\/]+)/(?P<cslug>[^\/]+)/add_classification/$',
     'ccdb.law.views.add_classification_to_consequence'),
    ('^edit/area/(?P<slug>[^\/]+)/(?P<cslug>[^\/]+)/delete/$',
     'ccdb.law.views.delete_consequence'),

    ('^edit/search/$', 'ccdb.law.views.edit_search'),

    ('^search/$', 'ccdb.law.views.search'),
    ('^autocomplete/$', views.AutocompleteView.as_view()),

    ('smoketest/', include('smoketest.urls')),

    ('^api/current/$', 'ccdb.law.views.api_current'),

    ('^feedback/$', views.FeedbackView.as_view()),
    ('^accounts/', include('djangowind.urls')),
    (r'^admin/', include(admin.site.urls)),
    url(r'^impersonate/', include('impersonate.urls')),
    (r'^stats/$', TemplateView.as_view(template_name="law/stats.html")),
    (r'^site_media/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': site_media_root}),
    (r'^uploads/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)
