# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 by the Free Software Foundation, Inc.
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

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.utils.timezone import now
from django.test import Client, TestCase
from django.test.utils import override_settings
from six.moves.urllib_error import HTTPError
from six.moves.urllib_parse import quote

from postorius.models import MailmanUser, Mailman404Error
from postorius.tests import MM_VCR, API_CREDENTIALS
from postorius.tests.utils import get_flash_messages
from postorius.utils import get_client


logger = logging.getLogger(__name__)
vcr_log = logging.getLogger('vcr')
vcr_log.setLevel(logging.WARNING)


@override_settings(**API_CREDENTIALS)
class ListMembersAccessTest(TestCase):
    """Tests for the list members page.

    Tests permissions and creation of list owners and moderators.
    """

    @MM_VCR.use_cassette('list_members_access.yaml')
    def setUp(self):
        self.client = Client()
        try:
            self.domain = get_client().create_domain('example.com')
        except HTTPError:
            self.domain = get_client().get_domain('example.com')
        try:
            self.foo_list = self.domain.create_list('foo')
        except HTTPError:
            self.foo_list = get_client().get_list('foo.example.com')
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

    @MM_VCR.use_cassette('list_members_access.yaml')
    def tearDown(self):
        self.foo_list.delete()
        self.user.delete()
        self.superuser.delete()
        self.owner.delete()
        self.moderator.delete()

    @MM_VCR.use_cassette('list_members_access.yaml')
    def test_page_not_accessible_if_not_logged_in(self):
        url = reverse('list_members', args=('foo@example.com', ))
        response = self.client.get(url)
        if "%40" not in url: # Django < 1.8
            url = quote(url)
        expected_redirect = "http://testserver%s?next=%s" % (
            reverse(settings.LOGIN_URL), url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["location"], expected_redirect)

    @MM_VCR.use_cassette('list_members_access.yaml')
    def test_page_not_accessible_for_unprivileged_users(self):
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('list_members',
                                           args=('foo@example.com', )))
        self.assertEqual(response.status_code, 403)

    @MM_VCR.use_cassette('list_members_page.yaml')
    def test_not_accessible_for_moderator(self):
        self.client.login(username='testmoderator', password='testpass')
        response = self.client.get(reverse('list_members',
                                           args=('foo@example.com', )))
        self.assertEqual(response.status_code, 403)

    @MM_VCR.use_cassette('list_members_page.yaml')
    def test_page_accessible_for_superuser(self):
        self.client.login(username='testsu', password='testpass')
        response = self.client.get(reverse('list_members',
                                           args=('foo@example.com', )))
        self.assertEqual(response.status_code, 200)

    @MM_VCR.use_cassette('list_members_page.yaml')
    def test_page_accessible_for_owner(self):
        self.client.login(username='testowner', password='testpass')
        response = self.client.get(reverse('list_members',
                                           args=('foo@example.com', )))
        self.assertEqual(response.status_code, 200)


@override_settings(**API_CREDENTIALS)
class AddRemoveOwnerTest(TestCase):
    """Tests for the list members page.

    Tests creation of list owners.
    """

    @MM_VCR.use_cassette('test_list_members_owner.yaml')
    def setUp(self):
        self.client = Client()
        self.mm_client = get_client()
        try:
            self.domain = self.mm_client.create_domain('example.com')
        except HTTPError:
            self.domain = self.mm_client.get_domain('example.com')
        self.foo_list = self.domain.create_list('foo')
        self.su = User.objects.create_superuser(
            'su', 'su@example.com', 'pwd')
        self.client.login(username='su', password='pwd')
        self.mm_client.get_list('foo@example.com').add_owner('su@example.com')

    @MM_VCR.use_cassette('test_list_members_owner.yaml')
    def tearDown(self):
        self.foo_list.delete()
        self.su.delete()

    @MM_VCR.use_cassette('test_list_members_owner_add_remove.yaml')
    def test_add_remove_owner(self):
        self.client.post(
            reverse('list_members', args=('foo@example.com', )),
            {'owner_email': 'newowner@example.com'})
        self.assertTrue('newowner@example.com' in self.foo_list.owners)
        self.client.post(
            reverse('remove_role', args=('foo@example.com', 'owner',
                                         'newowner@example.com')))
        self.assertFalse('newowner@example.com' in self.foo_list.owners)

    @MM_VCR.use_cassette('test_list_members_owner_by_owner.yaml')
    def test_remove_owner_by_owner(self):
        self.assertTrue('su@example.com' in self.foo_list.owners)
        # Make the logged in user a simple list owner
        self.su.is_superuser = False
        self.su.save()
        # It must still be allowed to create and remove owners
        self.client.post(
            reverse('list_members', args=('foo@example.com', )),
            {'owner_email': 'newowner@example.com'})
        self.assertTrue('newowner@example.com' in self.foo_list.owners)
        response = self.client.post(
            reverse('remove_role', args=('foo@example.com', 'owner',
                                         'newowner@example.com')))
        self.assertFalse('newowner@example.com' in self.foo_list.owners)
        msgs = get_flash_messages(response)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].level, messages.SUCCESS, msgs[0].message)

    @MM_VCR.use_cassette('test_list_members_owner_self_last.yaml')
    def test_remove_owner_as_owner_self_last(self):
        # It is allowed to remove itself, but only if there's another owner
        # left.
        mm_list = self.mm_client.get_list('foo@example.com')
        mm_list.add_owner('otherowner@example.com')
        self.assertTrue('su@example.com' in self.foo_list.owners)
        self.assertTrue('otherowner@example.com' in self.foo_list.owners)
        response = self.client.post(
            reverse('remove_role', args=('foo@example.com', 'owner',
                                         'su@example.com')))
        self.assertFalse('su@example.com' in self.foo_list.owners)
        self.assertEqual(response.status_code, 302)
        msgs = get_flash_messages(response)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].level, messages.SUCCESS, msgs[0].message)
        # But not to remove the last owner
        mm_list.add_owner('su@example.com')
        mm_list.remove_owner('otherowner@example.com')
        self.assertTrue('su@example.com' in self.foo_list.owners)
        self.assertFalse('otherowner@example.com' in self.foo_list.owners)
        response = self.client.post(
            reverse('remove_role', args=('foo@example.com', 'owner',
                                         'su@example.com')))
        self.assertTrue('su@example.com' in self.foo_list.owners)
        self.assertEqual(response.status_code, 302)
        msgs = get_flash_messages(response)
        self.assertEqual(len(msgs), 2)
        self.assertEqual(msgs[1].level, messages.ERROR, msgs[1].message)



@override_settings(**API_CREDENTIALS)
class AddModeratorTest(TestCase):
    """Tests for the list members page.

    Tests creation of moderators.
    """

    @MM_VCR.use_cassette('test_list_members_add_moderator.yaml')
    def setUp(self):
        self.client = Client()
        try:
            self.domain = get_client().create_domain('example.com')
        except HTTPError:
            self.domain = get_client().get_domain('example.com')
        self.foo_list = self.domain.create_list('foo')
        self.su = User.objects.create_superuser(
            'su', 'su@example.com', 'pwd')
        # login and post new moderator data to url
        self.client.login(username='su', password='pwd')
        self.client.post(
            reverse('list_members', args=('foo@example.com', )),
            {'moderator_email': 'newmod@example.com'})
        moderators = self.foo_list.moderators

    @MM_VCR.use_cassette('test_list_members_add_moderator.yaml')
    def tearDown(self):
        self.foo_list.delete()
        self.su.delete()

    @MM_VCR.use_cassette('test_list_members_new_moderator_added.yaml')
    def test_new_moderator_added(self):
        self.assertTrue(u'newmod@example.com' in self.foo_list.moderators)
