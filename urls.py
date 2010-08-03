# -*- coding: utf-8 -*-
from django.conf.urls.defaults import *
from django.conf import settings

urlpatterns = patterns('mailman_django.views',
    (r'^$', 'list_index'),
    url(r'^lists/$', 'list_index', name = 'list_index'),
    url(r'^lists/new/$', 'list_new', name = 'list_new'),
    url(r'^lists/(?P<fqdn_listname>.+)/$', 'list_info', name = 'list_info'),
    url(r'^delete_list/(?P<fqdn_listname>[^/]+)/$', 'list_delete', name = 'list_delete'),
    url(r'^settings/(?P<fqdn_listname>[^/]+)/$', 'list_settings', name = 'list_settings'),
    url(r'^settings/(?P<fqdn_listname>[^/]+)/mass_subscribe/$', 'mass_subscribe', name = 'mass_subscribe'),
    # to override the default templates specifiy your own:
    # url(r'lists/(?P<fqdn_listname>.+)/$', 'list_info', dict(template = 'path/to/template.html'), name = 'list_info'),
)
