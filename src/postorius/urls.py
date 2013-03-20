# -*- coding: utf-8 -*-
# Copyright (C) 1998-2012 by the Free Software Foundation, Inc.
#
# This file is part of Postorius.
#
# Postorius is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# Postorius is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# Postorius.  If not, see <http://www.gnu.org/licenses/>.

from django.conf.urls.defaults import *
from django.conf import settings
from django.conf.urls.static import static

from postorius.views import *
from postorius.views.generic import *


urlpatterns = patterns(
    'postorius.views',
    (r'^$', 'list_index'),
    # /account/
    url(r'^accounts/login/$', 'user_login', name='user_login'),
    url(r'^accounts/logout/$', 'user_logout', name='user_logout'),
    url(r'^accounts/profile/$', 'user_profile', name='user_profile'),
    url(r'^tasks/$', 'user_tasks', name='user_tasks'),
    url(r'^accounts/subscriptions/$', UserSubscriptionsView.as_view(),
        name='user_subscriptions'),
    url(r'^accounts/mailmansettings/$',
        'user_mailmansettings',
        name='user_mailmansettings'),
    # /settings/
    url(r'^settings/$', 'site_settings', name="site_settings"),
    url(r'^domains/$', 'domain_index', name='domain_index'),
    url(r'^domains/new/$', 'domain_new', name='domain_new'),
    url(r'^domains/(?P<domain>[^/]+)/delete$',
        'domain_delete', name='domain_delete'),
    # /lists/
    url(r'^lists/$', 'list_index', name='list_index'),
    url(r'^lists/new/$', 'list_new', name='list_new'),
    url(r'^lists/(?P<fqdn_listname>[^/]+)/members/$',
        ListMembersView.as_view(), name='list_members'),
    url(r'^lists/(?P<fqdn_listname>[^/]+)/metrics$',
        ListMetricsView.as_view(), name='list_metrics'),
    url(r'^lists/(?P<fqdn_listname>[^/]+)/$',
        ListSummaryView.as_view(), name='list_summary'),
    url(r'^lists/(?P<fqdn_listname>[^/]+)/subscribe$',
        ListSubsribeView.as_view(), name='list_subscribe'),
    url(r'^lists/(?P<fqdn_listname>[^/]+)/unsubscribe/(?P<email>[^/]+)$',
        ListUnsubscribeView.as_view(), name='list_unsubscribe'),
    url(r'^lists/(?P<fqdn_listname>[^/]+)/subscriptions$',
        'list_subscriptions', name='list_subscriptions'),
    url(r'^lists/(?P<fqdn_listname>[^/]+)/mass_subscribe/$',
        ListMassSubsribeView.as_view(), name='mass_subscribe'),
    url(r'^lists/(?P<fqdn_listname>[^/]+)/delete$',
        'list_delete', name='list_delete'),
    url(r'^lists/(?P<fqdn_listname>[^/]+)/held_messages/(?P<msg_id>[^/]+)/'
        'accept$', 'accept_held_message', name='accept_held_message'),
    url(r'^lists/(?P<fqdn_listname>[^/]+)/held_messages/(?P<msg_id>[^/]+)/'
        'discard$', 'discard_held_message', name='discard_held_message'),
    url(r'^lists/(?P<fqdn_listname>[^/]+)/held_messages/(?P<msg_id>[^/]+)/'
        'defer$', 'defer_held_message', name='defer_held_message'),
    url(r'^lists/(?P<fqdn_listname>[^/]+)/held_messages/(?P<msg_id>[^/]+)/'
        'reject$', 'reject_held_message', name='reject_held_message'),
    url(r'^lists/(?P<fqdn_listname>[^/]+)/held_messages$',
        'list_held_messages', name='list_held_messages'),
    url(r'^user_settings/$', 'user_settings', kwargs={"tab": "user"},
        name='user_settings'),
    url(r'^lists/(?P<fqdn_listname>[^/]+)/settings/(?P<visible_section>[^/]+)?'
        '(?:/(?P<visible_option>.*))?$', 'list_settings',
        name='list_settings'),
    # /users/
    url(r'^users/$', 'user_index', name='user_index'),
    url(r'^users/new/$', 'user_new', name='user_new'),
    url(r'^users/(?P<user_id>[^/]+)/$',
        UserSummaryView.as_view(), name='user_summary'),
    url(r'^api/lists/$', 'api_list_index', name='api_list_index'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
