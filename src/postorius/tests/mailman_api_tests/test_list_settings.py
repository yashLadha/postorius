# -*- coding: utf-8 -*-
# Copyright (C) 2016 by the Free Software Foundation, Inc.
#
# This file is part of Postorius.
#
# Postorius is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
# Postorius is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# Postorius.  If not, see <http://www.gnu.org/licenses/>.

"""Tests for ban lists"""

from __future__ import absolute_import,  print_function, unicode_literals

import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.timezone import now
from django.test import Client, TestCase
from six.moves.urllib_error import HTTPError
from six.moves.urllib_parse import quote

from postorius.views.list import SETTINGS_FORMS
from postorius.models import MailmanUser, Mailman404Error, List
from postorius.tests import MM_VCR
from postorius.tests.utils import get_flash_messages
from postorius.utils import get_client


logger = logging.getLogger(__name__)
vcr_log = logging.getLogger('vcr')
vcr_log.setLevel(logging.WARNING)


class ListSettingsTest(TestCase):
    """
    Tests for the list settings page.
    """

    @MM_VCR.use_cassette('list_settings.yaml')
    def setUp(self):
        self.domain = get_client().create_domain('example.com')
        self.foo_list = self.domain.create_list('foo')
        self.user = User.objects.create_user(
            'testuser', 'test@example.com', 'testpass')
        self.superuser = User.objects.create_superuser(
            'testsu', 'su@example.com', 'testpass')
        self.owner = User.objects.create_user(
            'testowner', 'owner@example.com', 'testpass')
        self.moderator = User.objects.create_user(
            'testmoderator', 'moderator@example.com', 'testpass')
        self.foo_list.add_owner('owner@example.com')
        self.foo_list.add_moderator('moderator@example.com')

    @MM_VCR.use_cassette('list_settings.yaml')
    def tearDown(self):
        self.foo_list.delete()
        self.user.delete()
        self.superuser.delete()
        self.owner.delete()
        self.moderator.delete()
        self.domain.delete()

    def _check_redirect_login(self, url):
        response = self.client.get(url)
        if '%40' not in url: # Django < 1.8
            url = quote(url)

        self.assertRedirects(response, '{}?next={}'.format(reverse(settings.LOGIN_URL), url))

    @MM_VCR.use_cassette('list_settings_access.yaml')
    def test_page_not_accessible_if_not_logged_in(self):
        for section_name in SETTINGS_FORMS:
            url = reverse('list_settings', args=('foo.example.com', section_name))
            self._check_redirect_login(url)

    @MM_VCR.use_cassette('list_settings_access.yaml')
    def test_page_not_accessible_for_unprivileged_users(self):
        self.client.login(username='testuser', password='testpass')
        for section_name in SETTINGS_FORMS:
            url = reverse('list_settings', args=('foo.example.com', section_name))
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403)

    @MM_VCR.use_cassette('list_settings_access.yaml')
    def test_not_accessible_for_moderator(self):
        self.client.login(username='testmoderator', password='testpass')
        for section_name in SETTINGS_FORMS:
            url = reverse('list_settings', args=('foo.example.com', section_name))
            response = self.client.get(url)
            self.assertEqual(response.status_code, 403)

    @MM_VCR.use_cassette('list_settings_access.yaml')
    def test_page_accessible_for_owner(self):
        self.client.login(username='testowner', password='testpass')
        for section_name in SETTINGS_FORMS:
            url = reverse('list_settings', args=('foo.example.com', section_name))
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    @MM_VCR.use_cassette('list_settings_access.yaml')
    def test_page_accessible_for_superuser(self):
        self.client.login(username='testsu', password='testpass')
        for section_name in SETTINGS_FORMS:
            url = reverse('list_settings', args=('foo@example.com', section_name))
            response = self.client.get(url)
            self.assertEqual(response.status_code, 200)

    @MM_VCR.use_cassette('list_settings_archiving.yaml')
    def test_archiving_policy(self):
        self.assertEqual(self.foo_list.settings['archive_policy'], 'public')
        self.client.login(username='testsu', password='testpass')
        url = reverse('list_settings', args=('foo.example.com', 'archiving'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.context["form"].initial['archive_policy'], 'public')
        response = self.client.post(url, {'archive_policy': 'private'})
        self.assertRedirects(response, url)
        msgs = get_flash_messages(response)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].level, messages.SUCCESS, msgs[0].message)
        # Get a new list object to avoid caching
        m_list = List.objects.get(fqdn_listname='foo.example.com')
        self.assertEqual(m_list.settings['archive_policy'], 'private')

    @MM_VCR.use_cassette('list_settings_archivers.yaml')
    def test_archivers(self):
        self.assertEqual(dict(self.foo_list.archivers),
            {'mhonarc': False, 'prototype': False, 'mail-archive': False})
        self.client.login(username='testsu', password='testpass')
        url = reverse('list_settings', args=('foo.example.com', 'archiving'))
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["form"].initial['archivers'], [])
        response = self.client.post(url,
            {'archive_policy': 'public', 'archivers': ['prototype']})
        self.assertRedirects(response, url)
        msgs = get_flash_messages(response)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].level, messages.SUCCESS, msgs[0].message)
        # Get a new list object to avoid caching
        m_list = List.objects.get(fqdn_listname='foo.example.com')
        self.assertEqual(dict(m_list.archivers),
            {'mhonarc': False, 'prototype': True, 'mail-archive': False})
