from django.conf.urls import patterns, include, url
from django.contrib.auth.views import login, logout

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

import iptracker.views 
urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', login),
    url(r'^accounts/logout/$', logout, {'next_page': '/logout/'}),
    url(r'^logout/$', 'auth.views.logout'),
    url(r'^$', 'iptracker.views.default', name='home'),
    url(r'^search/$', 'iptracker.views.search', name='search'),
    url(r'^list/$', 'iptracker.views.list_default', name='list'),
    url(r'^list/domains/$', 'iptracker.views.list_domains', name='list-domains'),
    url(r'^list/entries$', 'iptracker.views.list_entries', name='list-entries'),
    url(r'^list/ip$', 'iptracker.views.list_ips', name='list-ips'),
    url(r'^list/domains/(?P<domain_id>\d+)/$', 'iptracker.views.list_domains_entries', name='list-domains-entries'),
    url(r'^list/iprange/$', 'iptracker.views.list_iprange', name='list-iprange'),
    url(r'^list/iprange/(?P<range_id>\d+)/$', 'iptracker.views.list_iprange_entries', name='list-iprange-entries'),
    url(r'^edit/$', 'iptracker.views.edit', name='edit'),
    url(r'^edit/error/name/$', 'iptracker.views.edit_error_name', name='edit-error-name'),
    url(r'^edit/record/saved/$', 'iptracker.views.edit_record_saved', name='edit-record-saved'),
    url(r'^edit/record/(?P<record_id>\d+)/$', 'iptracker.views.edit_record', name='edit-record'),
    url(r'^edit/domain/(?P<domain_id>\d+)/$', 'iptracker.views.edit_domain', name='edit-domain'),
    url(r'^edit/ip/(?P<ip_id>\d+)/$', 'iptracker.views.edit_ip', name='edit-ip'),
    url(r'^del/$', 'iptracker.views.delete', name='del'),
    url(r'^del/record/(?P<record_id>\d+)/$', 'iptracker.views.del_record', name='del-record'),
    url(r'^del/domain/(?P<domain_id>\d+)/$', 'iptracker.views.del_domain', name='del-domain'),
    url(r'^del/ip/(?P<ip_id>\d+)/$', 'iptracker.views.del_ip', name='del-ip'),
    url(r'^del/del/record/(?P<record_id>\d+)/$', 'iptracker.views.del_del_record', name='del-del-record'),
    url(r'^del/del/domain/(?P<domain_id>\d+)/$', 'iptracker.views.del_del_domain', name='del-del-domain'),
    url(r'^del/del/ip/(?P<ip_id>\d+)/$', 'iptracker.views.del_del_ip', name='del-del-ip'),
    url(r'^add/$', 'iptracker.views.add', name='add'),
    url(r'^add/domain/$', 'iptracker.views.add_domain', name='add-domain'),
    url(r'^add/iprange/$', 'iptracker.views.add_iprange', name='add-iprange'),
    url(r'^add/entry$', 'iptracker.views.add_entry', name='add-entry'),
    url(r'^add/entry/(?P<ip>[\w\.]+)/$', 'iptracker.views.add_entry_ip', name='add-entry-ip'),
    url(r'^add/saved/$', 'iptracker.views.add_saved', name='add-saved'),
    url(r'^add/ip/$', 'iptracker.views.add_ip', name='add-ip'),
    url(r'^add/error/ip/$', 'iptracker.views.add_error_ip', name='add-error-ip'),
    url(r'^add/error/range/$', 'iptracker.views.add_error_range', name='add-error-range'),
    url(r'^add/error/range/ip/$', 'iptracker.views.add_error_range_ip', name='add-error-range-ip'),
    url(r'^add/error/name/$', 'iptracker.views.add_error_name', name='add-error-name'),
    url(r'^add/error/ip/exists$', 'iptracker.views.add_error_ip_exists', name='add-error-ip-exists'),
    url(r'^add/error/mac/exists$', 'iptracker.views.add_error_mac_exists', name='add-error-mac-exists'),
    url(r'^search/global/$', 'iptracker.views.search_global', name='search-global'),
    url(r'^search/ip/$', 'iptracker.views.search_ip', name='search-ip'),
)
