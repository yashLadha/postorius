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

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db import IntegrityError
from django.test import Client, SimpleTestCase
from django.test.utils import override_settings
try:
    from urllib2 import HTTPError
except ImportError:
    from urllib.error import HTTPError

from postorius.utils import get_client
from postorius.tests import MM_VCR, API_CREDENTIALS


logger = logging.getLogger(__name__)
vcr_log = logging.getLogger('vcr')
vcr_log.setLevel(logging.WARNING)


@override_settings(**API_CREDENTIALS)
class ListSummaryPageTest(SimpleTestCase):
    """Tests for the list summary page.

    Tests accessiblity and existince of the submit form depending on
    login status.
    """

    @MM_VCR.use_cassette('test_list_summary.yaml')
    def setUp(self):
        self.mmclient = get_client()
        try:
            domain = self.mmclient.create_domain('example.com')
        except HTTPError:
            domain = self.mmclient.get_domain('example.com')
        self.foo_list = domain.create_list('foo')
        try:
            User.objects.create_user('testuser', 'test@example.com', 'testpass')
        except IntegrityError:
            pass

    @MM_VCR.use_cassette('test_list_summary.yaml')
    def tearDown(self):
        for mlist in self.mmclient.lists:
            mlist.delete()
        for user in self.mmclient.users:
            user.delete()
        User.objects.all().delete()

    @MM_VCR.use_cassette('test_list_summary.yaml')
    def test_list_summary_logged_out(self):
        # Response must contain list obj but not the form.
        response = self.client.get(reverse('list_summary',
                                   args=('foo@example.com', )))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['list'].fqdn_listname,
                         'foo@example.com')
        self.assertTrue('<h1>' in response.content)
        self.assertTrue('<form ' not in response.content)

    @MM_VCR.use_cassette('test_list_summary.yaml')
    def test_list_summary_logged_in(self):
        # Response must contain list obj and the form.
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('list_summary',
                                   args=('foo@example.com', )))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('<form ' in response.content)
        self.assertTrue('Subscribe' in response.content)

    @MM_VCR.use_cassette('test_change_subscription-2.yaml')
    def test_list_summary_shows_all_addresses(self):
        mlist = self.mmclient.get_list('foo@example.com')
        mlist.subscribe('test@example.com')
        user = self.mmclient.get_user('test@example.com')
        address = user.add_address('anotheremail@example.com')
        address.verify()
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('list_summary',
                                           args=('foo@example.com', )))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('anotheremail@example.com' in response.content)

    @MM_VCR.use_cassette('test_change_subscription.yaml')
    def test_change_subscription(self):
        mlist = self.mmclient.get_list('foo@example.com')
        mlist.subscribe('test@example.com',
                        pre_verified=True,
                        pre_confirmed=True)
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('list_summary',
                                           args=('foo@example.com', )))
        self.assertEqual(response.status_code, 200)
        self.assertTrue('Change Subscription' in response.content)
        self.assertTrue('Unsubscribe' in response.content)

    @MM_VCR.use_cassette('test_list_summary_owner.yaml')
    def test_list_summary_owner(self):
        # Response must contain the administration menu
        user = self.mmclient.create_user('test@example.com', None)
        mlist = self.mmclient.get_list('foo@example.com')
        mlist.add_owner('test@example.com')
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('list_summary',
                                   args=('foo@example.com', )))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<li class="mm_nav_item">', count=9)

    @MM_VCR.use_cassette('test_list_summary_moderator.yaml')
    def test_list_summary_moderator(self):
        # Response must contain the administration menu
        user = self.mmclient.create_user('test@example.com', None)
        mlist = self.mmclient.get_list('foo@example.com')
        mlist.add_moderator('test@example.com')
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('list_summary',
                                   args=('foo@example.com', )))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<li class="mm_nav_item">', count=3)

    @MM_VCR.use_cassette('test_list_summary_secondary_owner.yaml')
    def test_list_summary_is_admin_secondary_owner(self):
        # Response must contain the administration menu
        user = self.mmclient.create_user('test@example.com', None)
        address = user.add_address('anotheremail@example.com')
        address.verify()
        mlist = self.mmclient.get_list('foo@example.com')
        mlist.add_owner('anotheremail@example.com')
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('list_summary',
                                   args=('foo@example.com', )))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<li class="mm_nav_item">', count=9)

    @MM_VCR.use_cassette('test_list_summary_secondary_moderator.yaml')
    def test_list_summary_is_admin_secondary_moderator(self):
        # Response must contain the administration menu
        user = self.mmclient.create_user('test@example.com', None)
        address = user.add_address('anotheremail@example.com')
        address.verify()
        mlist = self.mmclient.get_list('foo@example.com')
        mlist.add_moderator('anotheremail@example.com')
        self.client.login(username='testuser', password='testpass')
        response = self.client.get(reverse('list_summary',
                                   args=('foo@example.com', )))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '<li class="mm_nav_item">', count=3)
