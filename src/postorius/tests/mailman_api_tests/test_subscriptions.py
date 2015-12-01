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

from django.contrib import messages
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import Client, TestCase
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


class TestSubscription(TestCase):
    """Tests subscription to lists"""

    @MM_VCR.use_cassette('test_list_subscription.yaml')
    def setUp(self):
        mm_client = get_client()
        try:
            self.domain = mm_client.create_domain('example.com')
        except HTTPError:
            self.domain = mm_client.get_domain('example.com')
        self.open_list = self.domain.create_list('open_list')
        # Set subscription policy to open
        settings = self.open_list.settings
        settings['subscription_policy'] = 'open'
        settings.save()
        self.mod_list = self.domain.create_list('moderate_subs')
        # Set subscription policy to moderate
        settings = self.mod_list.settings
        settings['subscription_policy'] = 'moderate'
        settings.save()
        # Create django user.
        self.user = User.objects.create_user(
            'testuser', 'test@example.com', 'pwd')
        # Create Mailman user
        self.mm_user = get_client().create_user('test@example.com', '')
        self.mm_user.add_address('fritz@example.org').verify()

    @MM_VCR.use_cassette('test_list_subscription.yaml')
    def tearDown(self):
        # Delete all subscription requests
        for req in self.open_list.requests:
            self.open_list.moderate_request(req['token'], 'discard')
        for req in self.mod_list.requests:
            self.mod_list.moderate_request(req['token'], 'discard')
        self.open_list.delete()
        self.mod_list.delete()
        self.mm_user.delete()

    @MM_VCR.use_cassette('test_list_subscription_open_primary.yaml')
    def test_subscribe_open(self):
        # The subscription goes straight through.
        self.client.login(username='testuser', password='pwd')
        response = self.client.post(
            reverse('list_subscribe', args=('open_list.example.com', )),
            {'email': 'test@example.com'})
        self.assertEqual(len(self.open_list.members), 1)
        self.assertEqual(len(self.open_list.requests), 0)
        self.assertRedirects(response,
            reverse('list_summary', args=('open_list.example.com', )))
        msgs = get_flash_messages(response)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].level, messages.SUCCESS, msgs[0].message)

    @MM_VCR.use_cassette('test_list_subscription_open_secondary.yaml')
    def test_secondary_open(self):
        # Subscribe with a secondary email address
        self.client.login(username='testuser', password='pwd')
        response = self.client.post(
            reverse('list_subscribe', args=('open_list.example.com', )),
            {'email': 'fritz@example.org'})
        self.assertEqual(len(self.open_list.members), 1)
        self.assertEqual(len(self.open_list.requests), 0)
        self.assertRedirects(response,
            reverse('list_summary', args=('open_list.example.com', )))
        msgs = get_flash_messages(response)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].level, messages.SUCCESS, msgs[0].message)

    @MM_VCR.use_cassette('test_list_subscription_unknown.yaml')
    def test_unknown_address(self):
        # Impossible to register with an unknown address
        self.client.login(username='testuser', password='pwd')
        response = self.client.post(
            reverse('list_subscribe', args=('open_list.example.com', )),
            {'email': 'unknown@example.org'})
        self.assertEqual(len(self.open_list.members), 0)
        self.assertEqual(len(self.open_list.requests), 0)
        self.assertRedirects(response,
            reverse('list_summary', args=('open_list.example.com', )))
        msgs = get_flash_messages(response)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].level, messages.ERROR, msgs[0].message)

    @MM_VCR.use_cassette('test_list_subscription_mod_primary.yaml')
    def test_subscribe_mod(self):
        # The subscription is held for approval.
        self.client.login(username='testuser', password='pwd')
        response = self.client.post(
            reverse('list_subscribe', args=('moderate_subs.example.com', )),
            {'email': 'test@example.com'})
        self.assertEqual(len(self.mod_list.members), 0)
        self.assertEqual(len(self.mod_list.requests), 1)
        self.assertRedirects(response,
            reverse('list_summary', args=('moderate_subs.example.com', )))
        msgs = get_flash_messages(response)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].level, messages.SUCCESS, msgs[0].message)

    @MM_VCR.use_cassette('test_list_subscription_mod_secondary.yaml')
    def test_secondary_mod(self):
        # Subscribe with a secondary email address
        self.client.login(username='testuser', password='pwd')
        response = self.client.post(
            reverse('list_subscribe', args=('moderate_subs.example.com', )),
            {'email': 'fritz@example.org'})
        self.assertEqual(len(self.mod_list.members), 0)
        self.assertEqual(len(self.mod_list.requests), 1)
        self.assertRedirects(response,
            reverse('list_summary', args=('moderate_subs.example.com', )))
        msgs = get_flash_messages(response)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].level, messages.SUCCESS, msgs[0].message)
