# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 by the Free Software Foundation, Inc.
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
import logging

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.test.utils import override_settings

from postorius.tests.mm_setup import mm_client


logger = logging.getLogger(__name__)


def setup_module():
    # Create a domain for all tests in this module.
    mm_client.create_domain(
        'example.com',
        contact_address='postmaster@example.com',
        base_url='lists.example.com')


def teardown_module():
    # Clean up.
    mm_client.delete_domain('example.com')


@override_settings(
    MAILMAN_API_URL='http://localhost:9001',
    MAILMAN_USER='restadmin',
    MAILMAN_PASS='restpass')
class ListMembersPageTest(TestCase):
    """Tests for the list members page.

    Tests permissions and creation of list owners and moderators.
    """

    def setUp(self):
        self.client = Client()
        domain = mm_client.get_domain('example.com')
        self.foo_list = domain.create_list('foo')
        self.user = User.objects.create_user('testuser', 'test@example.com',
                                             'testpass')
        self.superuser = User.objects.create_superuser('testsu',
                                                       'su@example.com',
                                                       'testpass')
        self.owner = User.objects.create_user('testowner', 'owner@example.com',
                                              'testpass')
        self.moderator = User.objects.create_user('testmoderator',
                                                  'moderator@example.com',
                                                  'testpass')
        self.foo_list.add_owner('owner@example.com')
        self.foo_list.add_moderator('moderator@example.com')

    def tearDown(self):
        self.foo_list.delete()
        self.user.delete()
        self.superuser.delete()
        self.owner.delete()
        self.moderator.delete()

    def test_page_not_accessible_if_not_logged_in(self):
        response = self.client.get(reverse('list_members',
                                           args=('foo@example.com', )))
        self.assertEqual(response.status_code, 403)

    def test_page_not_accessible_for_unprivileged_users(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('list_members',
                                           args=('foo@example.com', )))
        self.assertEqual(response.status_code, 403)

    def test_page_not_accessible_for_moderator(self):
        self.client.login(username='testmoderator', password='testpass')
        response = self.client.get(reverse('list_members',
                                           args=('foo@example.com', )))
        self.assertEqual(response.status_code, 403)

    def test_page_accessible_for_superuser(self):
        self.client.login(username='testsu', password='testpass')
        response = self.client.get(reverse('list_members',
                                           args=('foo@example.com', )))
        self.assertEqual(response.status_code, 200)

    def test_page_accessible_for_owner(self):
        self.client.login(username='testowner', password='testpass')
        response = self.client.get(reverse('list_members',
                                           args=('foo@example.com', )))
        self.assertEqual(response.status_code, 200)

    def test_add_owner(self):
        self.client.login(username='testsu', password='testpass')
        self.client.post(reverse('list_members',
                                 args=('foo@example.com', )),
                         {'owner_email': 'newowner@example.com'})
        self.assertTrue(u'newowner@example.com' in self.foo_list.owners)

    def test_add_moderator(self):
        self.client.login(username='testsu', password='testpass')
        self.client.post(reverse('list_members',
                                 args=('foo@example.com', )),
                         {'moderator_email': 'newmod@example.com'})
        self.assertTrue(u'newmod@example.com' in self.foo_list.moderators)
