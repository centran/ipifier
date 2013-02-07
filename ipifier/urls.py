from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', login),
    url(r'^accounts/logout/$', logout, {'next_page': '/logout/'}),
    url(r'^logout/$', 'auth.views.logout'),
    url(r'^$', 'iptracker.views.default', name='home'),
    url(r'^search/$', 'iptracker.views.search', name='search'),
    url(r'^list/$', 'iptracker.views.list', name='list'),

)
