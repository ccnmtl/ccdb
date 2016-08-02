from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView
import ccdb.law.views as views
import os.path
admin.autodiscover()

site_media_root = os.path.join(os.path.dirname(__file__), "../media")

urlpatterns = [
    url('^$', views.IndexView.as_view()),
    url('^charge/(?P<slugs>.+)/tips/$', views.ChargeTipsView.as_view()),
    url('^charge/(?P<slugs>.+)/$', views.ChargeView.as_view()),
    url('^classification/(?P<slug>[^\/]+)/$',
        views.ClassificationView.as_view()),
    url('^area/(?P<slug>[^\/]+)/$', views.AreaView.as_view()),
    url('^area/(?P<slug>[^\/]+)/(?P<cslug>[^\/]+)/$',
        views.ConsequenceView.as_view()),

    url('^edit/$', views.EditView.as_view()),
    url('^edit/graph/$', views.GraphView.as_view()),
    url('^edit/snapshots/$', views.EditSnapshotsView.as_view()),
    url('^edit/snapshots/(?P<pk>\d+)/$', views.EditSnapshotView.as_view()),
    url('^edit/snapshots/(?P<id>\d+)/clone/$',
        views.CloneSnapshotView.as_view()),
    url('^edit/snapshots/(?P<id>\d+)/approve/$',
        views.ApproveSnapshotView.as_view()),
    url('^edit/snapshots/(?P<pk>\d+)/delete/$',
        views.DeleteSnapshotView.as_view()),

    url('^edit/charge/$', views.EditChargesView.as_view()),
    url('^edit/charge/(?P<slugs>.*)add_charge/$',
        views.AddChargeView.as_view()),
    url(('^edit/charge/(?P<slugs>.*)remove_classification/'
         '(?P<classification_id>\d+)/$'),
        views.RemoveChargeClassificationView.as_view()),
    url('^edit/charge/(?P<slugs>.*)add_classification/$',
        views.AddChargeClassificationView.as_view()),
    url('^edit/charge/(?P<slugs>.*)reparent/$',
        views.ReparentChargeView.as_view()),
    url('^edit/charge/(?P<slugs>.*)delete/$',
        views.DeleteChargeView.as_view()),
    url('^edit/charge/(?P<slugs>.*)add_area/$',
        views.AddAreaToChargeView.as_view()),
    url('^edit/charge/(?P<slugs>.*)remove_area/(?P<ca_id>\d+)/$',
        views.RemoveAreaFromChargeView.as_view()),
    url('^edit/charge/(?P<slugs>.+)/$', views.EditChargeView.as_view()),

    url('^edit/classification/$', views.EditClassificationIndexView.as_view()),
    url('^edit/classification/add/$', views.AddClassificationView.as_view()),
    url('^edit/classification/(?P<slug>[^\/]+)/$',
        views.EditClassificationView.as_view()),
    url('^edit/classification/(?P<slug>[^\/]+)/preview/$',
        views.PreviewClassificationView.as_view()),
    url('^edit/classification/(?P<slug>[^\/]+)/delete/$',
        views.DeleteClassificationView.as_view()),
    url('^edit/classification/(?P<slug>[^\/]+)/add_consequence/$',
        views.AddConsequenceToClassificationView.as_view()),
    url(('^edit/classification/(?P<slug>[^\/]+)/remove_consequence/'
         '(?P<consequence_id>\d+)/$'),
        views.RemoveConsequenceFromClassificationView.as_view()),

    url('^edit/area/$', views.EditAreaIndexView.as_view()),
    url('^edit/area/add/$', views.AddAreaView.as_view()),
    url('^edit/area/(?P<slug>[^\/]+)/$', views.EditAreaView.as_view()),
    url('^edit/area/(?P<slug>[^\/]+)/delete/$',
        views.DeleteAreaView.as_view()),
    url('^edit/area/(?P<slug>[^\/]+)/add_consequence/$',
        views.AddConsequenceView.as_view()),
    url('^edit/area/(?P<slug>[^\/]+)/(?P<cslug>[^\/]+)/$',
        views.EditConsequenceView.as_view()),
    url('^edit/area/(?P<slug>[^\/]+)/(?P<cslug>[^\/]+)/add_classification/$',
        views.AddClassificationToConsequence.as_view()),
    url('^edit/area/(?P<slug>[^\/]+)/(?P<cslug>[^\/]+)/delete/$',
        views.DeleteConsequenceView.as_view()),

    url('^edit/search/$', 'ccdb.law.views.edit_search'),

    url('^search/$', 'ccdb.law.views.search'),
    url('^autocomplete/$', views.AutocompleteView.as_view()),

    url('smoketest/', include('smoketest.urls')),

    url('^api/current/$', 'ccdb.law.views.api_current'),

    url('^feedback/$', views.FeedbackView.as_view()),
    url('^accounts/', include('djangowind.urls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^impersonate/', include('impersonate.urls')),
    url(r'^stats/$', TemplateView.as_view(template_name="law/stats.html")),
    url(r'^site_media/(?P<path>.*)$',
        'django.views.static.serve', {'document_root': site_media_root}),
    url(r'^uploads/(?P<path>.*)$',
        'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
]
