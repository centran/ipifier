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
    url(r'^list/domains/$', 'iptracker.views.list_domains', name='list-domains'),
    url(r'^list/entries$', 'iptracker.views.list_entries', name='list-entries'),
    url(r'^list/domains/(?P<domain_id>\d+)/$', 'iptracker.views.list_domains_entries', name='list-domains-entries'),
    url(r'^edit/$', 'iptracker.views.edit', name='edit'),
    url(r'^edit/record/saved/$', 'iptracker.views.edit_record_saved', name='edit-record-saved'),
    url(r'^edit/record/(?P<record_id>\d+)/$', 'iptracker.views.edit_record', name='edit-record'),
    url(r'^add/$', 'iptracker.views.add', name='add'),
    url(r'^add/domain/$', 'iptracker.views.add_domain', name='add-domain'),
    url(r'^add/iprange/$', 'iptracker.views.add_iprange', name='add-iprange'),
    url(r'^add/entry$', 'iptracker.views.add_entry', name='add-entry'),
    url(r'^add/saved/$', 'iptracker.views.add_saved', name='add-saved'),
)
