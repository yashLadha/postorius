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


urlpatterns = patterns('mailman_django.views',
    (r'^$', 'list_index'),
    url(r'^logout/$', 'logout', name = 'logout'),
    url(r'^administration/$', 'administration', name = 'administration'),
    url(r'^domains/$', 'domain_index', name = 'domain_index'),
    url(r'^domains/new/$', 'domain_new', name = 'domain_new'),
    url(r'^lists/$', 'list_index', name = 'list_index'),
    url(r'^lists/new/$', 'list_new', name = 'list_new'),
    url(r'^lists/(?P<fqdn_listname>[^/]+)/$', 'list_summary', name = 'list_summary'), #PUBLIC
    url(r'^subscriptions/(?P<fqdn_listname>[^/]+)/(?:(?P<option>subscribe|unsubscribe)?)(/(?P<user_email>.+))?$', 'list_subscriptions', name = 'list_subscriptions'),
    url(r'^delete_list/(?P<fqdn_listname>[^/]+)/$', 'list_delete', name = 'list_delete'),
    url(r'^user_settings/(?P<member>[^/]+)/$', 'user_settings', kwargs={"tab": "user"}, name = 'user_settings'),
    url(r'^membership_settings/(?P<member>[^/]+)/$', 'user_settings', kwargs={"tab": "membership"}, name = 'membership_settings'),
    #url(r'^settings/(?P<fqdn_listname>[^/]+)/(?P<visible_section>[^/]+)?/(?P<visible_option>.+)?$', 'list_settings', name = 'list_settings'),
    url(r'^settings/(?P<fqdn_listname>[^/]+)/(?P<visible_section>[^/]+)?(?:/(?P<visible_option>.*))?$', 'list_settings', name = 'list_settings'),    
    url(r'^settings/(?P<fqdn_listname>[^/]+)/mass_subscribe/$', 'mass_subscribe', name = 'mass_subscribe'),
    ) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)#https://docs.djangoproject.com/en/dev/howto/static-files/#serving-static-files-in-production


