# -*- coding: utf-8 -*-
# Copyright (C) 1998-2010 by the Free Software Foundation, Inc.
#
# This file is part of GNU Mailman.
#
# GNU Mailman is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# GNU Mailman is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# GNU Mailman.  If not, see <http://www.gnu.org/licenses/>.

from django.conf.urls.defaults import *
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = patterns('mailmanweb.views',
    (r'^$', 'list_index'),
    url(r'^accounts/login/$', 'user_login', name='user_login'),
    url(r'^accounts/logout/$', 'user_logout', name='user_logout'),
    url(r'^accounts/profile/$', 'user_profile', name='user_profile'),
    url(r'^administration/$', 'administration', name='administration'),
    url(r'^domains/$', 'domain_index', name='domain_index'),
    url(r'^domains/new/$', 'domain_new', name='domain_new'),
    url(r'^lists/$', 'list_index', name='list_index'),
    url(r'^lists/new/$', 'list_new', name='list_new'),
    url(r'^lists/(?P<fqdn_listname>[^/]+)/metrics$', 'list_metrics',
        name='list_metrics'),
    url(r'^lists/(?P<fqdn_listname>[^/]+)/$', 'list_summary',
        name='list_summary'),
    url(r'^lists/(?P<fqdn_listname>[^/]+)/subscribe$',
        'list_subscribe', name='list_subscribe'),
    url(r'^lists/(?P<fqdn_listname>[^/]+)/subscriptions$',
        'list_subscriptions', name='list_subscriptions'),
    url(r'^subscriptions/(?P<fqdn_listname>[^/]+)/mass_subscribe/$',
        'mass_subscribe', name='mass_subscribe'),
    url(r'^delete_list/(?P<fqdn_listname>[^/]+)/$', 'list_delete',
        name='list_delete'),
    url(r'^user_settings/$', 'user_settings', kwargs={"tab": "user"},
        name='user_settings'),
    url(r'^membership_settings/(?:(?P<fqdn_listname>[^/]+)/)?$',
        'user_settings', kwargs={"tab": "membership"},
        name='membership_settings'),
    url(r'^settings/(?P<fqdn_listname>[^/]+)/(?P<visible_section>[^/]+)?(?:/(?P<visible_option>.*))?$',
        'list_settings', name='list_settings'),    
    ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


