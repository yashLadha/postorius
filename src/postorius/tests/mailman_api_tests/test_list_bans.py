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

import mock
import logging

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import Client, RequestFactory, TestCase
try:
    from urllib2 import HTTPError
except ImportError:
    from urllib.error import HTTPError

from postorius.tests import MM_VCR
from postorius.tests.utils import get_flash_messages
from postorius.utils import get_client


logger = logging.getLogger(__name__)
vcr_log = logging.getLogger('vcr')
vcr_log.setLevel(logging.WARNING)


class ListBansTest(TestCase):

    @MM_VCR.use_cassette('list_bans.yaml')
    def setUp(self):
        # Create domain `example.com` in Mailman
        example_com = get_client().create_domain('example.com')
        self.m_list = example_com.create_list('test_list')
        self.test_user = User.objects.create_user(
            'test_user', 'test_user@example.com', 'pwd')
        self.test_superuser = User.objects.create_superuser(
            'test_superuser', 'test_superuser@example.com', 'pwd')
        self.client.login(username="test_superuser", password='pwd')
        self.url = reverse('list_bans', args=['test_list.example.com'])

    @MM_VCR.use_cassette('list_bans.yaml')
    def tearDown(self):
        self.test_user.delete()
        self.test_superuser.delete()
        self.m_list.delete()
        get_client().delete_domain('example.com')

    @MM_VCR.use_cassette('list_bans.yaml')
    def test_login_redirect_for_anonymous(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)

    @MM_VCR.use_cassette('list_bans.yaml')
    def test_no_access_for_basic_user(self):
        self.client.logout()
        self.client.login(username="test_user", password='pwd')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 403)

    @MM_VCR.use_cassette('list_bans.yaml')
    def test_access_for_superuser(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    @MM_VCR.use_cassette('list_bans.yaml')
    def test_context_contains_create_form(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('addban_form' in response.context)
        self.assertContains(response,
            '<input class="form-control" id="id_email" name="email" '
            'type="text" />')
        self.assertContains(response,
            '<button class="btn btn-primary" type="submit" name="add">'
            'Ban email</button>')

    @MM_VCR.use_cassette('list_bans_delete_forms.yaml')
    def test_context_contains_delete_forms(self):
        banned = ["banned{}@example.com".format(i) for i in range(1,10)]
        for ban in banned:
            self.m_list.bans.add(ban)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        for ban in banned:
            self.assertContains(response,
                '<input type="hidden" name="email" value="%s" />' % ban)
        self.assertContains(response,
            '<button class="btn btn-danger btn-xs" type="submit" name="del"',
            count=9)

    @MM_VCR.use_cassette('list_bans_add_ban.yaml')
    def test_add_ban(self):
        response = self.client.post(self.url, {
            'email': 'banned@example.com',
            'add': True,
            })
        self.assertRedirects(response, self.url)
        self.assertIn('banned@example.com', self.m_list.bans)
        msgs = get_flash_messages(response)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].level, messages.SUCCESS, msgs[0].message)

    @MM_VCR.use_cassette('list_bans_del_ban.yaml')
    def test_del_ban(self):
        self.m_list.bans.add('banned@example.com')
        self.assertIn('banned@example.com', self.m_list.bans)
        response = self.client.post(self.url, {
            'email': 'banned@example.com',
            'del': True,
            })
        self.assertRedirects(response, self.url)
        self.assertNotIn('banned@example.com', self.m_list.bans)
        msgs = get_flash_messages(response)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].level, messages.SUCCESS, msgs[0].message)

    @MM_VCR.use_cassette('list_bans_del_unknown_ban.yaml')
    def test_del_unknown_ban(self):
        self.assertNotIn('banned@example.com', self.m_list.bans)
        response = self.client.post(self.url, {
            'email': 'banned@example.com',
            'del': True,
            })
        self.assertRedirects(response, self.url)
        msgs = get_flash_messages(response)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].level, messages.ERROR, msgs[0].message)
        self.assertIn('is not banned', msgs[0].message)

    @MM_VCR.use_cassette('list_bans_add_duplicate.yaml')
    def test_add_ban_duplicate(self):
        self.m_list.bans.add('banned@example.com')
        self.assertIn('banned@example.com', self.m_list.bans)
        response = self.client.post(self.url, {
            'email': 'banned@example.com',
            'add': True,
            })
        self.assertRedirects(response, self.url)
        msgs = get_flash_messages(response)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].level, messages.ERROR, msgs[0].message)
        self.assertIn('is already banned', msgs[0].message)
