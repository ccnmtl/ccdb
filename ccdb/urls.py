import ccdb.law.views as views
import django.views.static
import os.path
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.urls import path
from django.views.generic import TemplateView
from django_cas_ng import views as cas_views

admin.autodiscover()

site_media_root = os.path.join(os.path.dirname(__file__), "../media")

urlpatterns = [
    url(r'^accounts/', include('django.contrib.auth.urls')),
    path('cas/login', cas_views.LoginView.as_view(),
         name='cas_ng_login'),
    path('cas/logout', cas_views.LogoutView.as_view(),
         name='cas_ng_logout'),

    url('^$', views.IndexView.as_view()),
    url('^charge/(?P<slugs>.+)/tips/$', views.RedirectIndexView.as_view()),
    url('^charge/(?P<slugs>.+)/$',  views.RedirectIndexView.as_view()),
    url('^classification/(?P<slug>[^\/]+)/$',
        views.RedirectIndexView.as_view()),
    url('^area/(?P<slug>[^\/]+)/$',  views.RedirectIndexView.as_view()),
    url('^area/(?P<slug>[^\/]+)/(?P<cslug>[^\/]+)/$',
        views.RedirectIndexView.as_view()),

    url('^edit/$', views.RedirectIndexView.as_view()),
    url('^edit/graph/$', views.RedirectIndexView.as_view()),
    url('^edit/snapshots/$', views.RedirectIndexView.as_view()),
    url('^edit/snapshots/(?P<pk>\d+)/$', views.RedirectIndexView.as_view()),
    url('^edit/snapshots/(?P<id>\d+)/clone/$',
        views.RedirectIndexView.as_view()),
    url('^edit/snapshots/(?P<id>\d+)/approve/$',
        views.RedirectIndexView.as_view()),
    url('^edit/snapshots/(?P<pk>\d+)/delete/$',
        views.RedirectIndexView.as_view()),

    url('^edit/charge/$', views.EditChargesView.as_view()),
    url('^edit/charge/(?P<slugs>.*)add_charge/$',
        views.RedirectIndexView.as_view()),
    url(('^edit/charge/(?P<slugs>.*)remove_classification/'
         '(?P<classification_id>\d+)/$'),
        views.RedirectIndexView.as_view()),
    url('^edit/charge/(?P<slugs>.*)add_classification/$',
        views.RedirectIndexView.as_view()),
    url('^edit/charge/(?P<slugs>.*)reparent/$',
        views.RedirectIndexView.as_view()),
    url('^edit/charge/(?P<slugs>.*)delete/$',
        views.RedirectIndexView.as_view()),
    url('^edit/charge/(?P<slugs>.*)add_area/$',
        views.RedirectIndexView.as_view()),
    url('^edit/charge/(?P<slugs>.*)remove_area/(?P<ca_id>\d+)/$',
        views.RedirectIndexView.as_view()),
    url('^edit/charge/(?P<slugs>.+)/$', views.RedirectIndexView.as_view()),

    url('^edit/classification/$', views.RedirectIndexView.as_view()),
    url('^edit/classification/add/$', views.RedirectIndexView.as_view()),
    url('^edit/classification/(?P<slug>[^\/]+)/$',
        views.RedirectIndexView.as_view()),
    url('^edit/classification/(?P<slug>[^\/]+)/preview/$',
        views.RedirectIndexView.as_view()),
    url('^edit/classification/(?P<slug>[^\/]+)/delete/$',
        views.RedirectIndexView.as_view()),
    url('^edit/classification/(?P<slug>[^\/]+)/add_consequence/$',
        views.RedirectIndexView.as_view()),
    url(('^edit/classification/(?P<slug>[^\/]+)/remove_consequence/'
         '(?P<consequence_id>\d+)/$'),
        views.RedirectIndexView.as_view()),

    url('^edit/area/$', views.RedirectIndexView.as_view()),
    url('^edit/area/add/$', views.RedirectIndexView.as_view()),
    url('^edit/area/(?P<slug>[^\/]+)/$', views.RedirectIndexView.as_view()),
    url('^edit/area/(?P<slug>[^\/]+)/delete/$',
        views.RedirectIndexView.as_view()),
    url('^edit/area/(?P<slug>[^\/]+)/add_consequence/$',
        views.RedirectIndexView.as_view()),
    url('^edit/area/(?P<slug>[^\/]+)/(?P<cslug>[^\/]+)/$',
        views.RedirectIndexView.as_view()),
    url('^edit/area/(?P<slug>[^\/]+)/(?P<cslug>[^\/]+)/add_classification/$',
        views.RedirectIndexView.as_view()),
    url('^edit/area/(?P<slug>[^\/]+)/(?P<cslug>[^\/]+)/delete/$',
        views.RedirectIndexView.as_view()),

    url('^edit/search/$', views.RedirectIndexView.as_view()),

    url('^search/$', views.RedirectIndexView.as_view()),
    url('^autocomplete/$', views.RedirectIndexView.as_view()),

    url('smoketest/', include('smoketest.urls')),

    url('^api/current/$', views.RedirectIndexView.as_view()),

    url('^feedback/$', views.RedirectIndexView.as_view()),
    url(r'^admin/', admin.site.urls),
    url(r'^impersonate/', include('impersonate.urls')),
    url(r'^stats/$', TemplateView.as_view(template_name="law/stats.html")),

    url(r'^site_media/(?P<path>.*)$', django.views.static.serve,
        {'document_root': site_media_root}),
    url(r'^uploads/(?P<path>.*)$', django.views.static.serve,
        {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
