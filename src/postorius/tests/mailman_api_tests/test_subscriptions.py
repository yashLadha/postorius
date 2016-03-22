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

from __future__ import absolute_import, print_function, unicode_literals

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse

from postorius.tests.utils import ViewTestCase


class TestSubscription(ViewTestCase):
    """Tests subscription to lists"""

    def setUp(self):
        super(TestSubscription, self).setUp()
        self.domain = self.mm_client.create_domain('example.com')
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
        self.mm_user = self.mm_client.create_user('test@example.com', '')
        self.mm_user.add_address('fritz@example.org').verify()

    def tearDown(self):
        # Delete all subscription requests
        for req in self.open_list.requests:
            self.open_list.moderate_request(req['token'], 'discard')
        for req in self.mod_list.requests:
            self.mod_list.moderate_request(req['token'], 'discard')
        self.open_list.delete()
        self.mod_list.delete()
        self.mm_user.delete()
        self.domain.delete()
        User.objects.all().delete()

    def test_subscribe_open(self):
        # The subscription goes straight through.
        self.client.login(username='testuser', password='pwd')
        response = self.client.post(
            reverse('list_subscribe', args=('open_list.example.com', )),
            {'email': 'test@example.com'})
        self.assertEqual(len(self.open_list.members), 1)
        self.assertEqual(len(self.open_list.requests), 0)
        self.assertRedirects(
                response, reverse('list_summary',
                                  args=('open_list.example.com', )))
        self.assertHasSuccessMessage(response)

    def test_secondary_open(self):
        # Subscribe with a secondary email address
        self.client.login(username='testuser', password='pwd')
        response = self.client.post(
            reverse('list_subscribe', args=('open_list.example.com', )),
            {'email': 'fritz@example.org'})
        self.assertEqual(len(self.open_list.members), 1)
        self.assertEqual(len(self.open_list.requests), 0)
        self.assertRedirects(
                response, reverse('list_summary',
                                  args=('open_list.example.com', )))
        self.assertHasSuccessMessage(response)

    def test_unknown_address(self):
        # Impossible to register with an unknown address
        self.client.login(username='testuser', password='pwd')
        response = self.client.post(
            reverse('list_subscribe', args=('open_list.example.com', )),
            {'email': 'unknown@example.org'})
        self.assertEqual(len(self.open_list.members), 0)
        self.assertEqual(len(self.open_list.requests), 0)
        self.assertRedirects(
                response, reverse('list_summary',
                                  args=('open_list.example.com', )))
        self.assertHasErrorMessage(response)

    def test_subscribe_mod(self):
        # The subscription is held for approval.
        self.client.login(username='testuser', password='pwd')
        response = self.client.post(
            reverse('list_subscribe', args=('moderate_subs.example.com', )),
            {'email': 'test@example.com'})
        self.assertEqual(len(self.mod_list.members), 0)
        self.assertEqual(len(self.mod_list.requests), 1)
        self.assertRedirects(
                response, reverse('list_summary',
                                  args=('moderate_subs.example.com', )))
        self.assertHasSuccessMessage(response)

    def test_secondary_mod(self):
        # Subscribe with a secondary email address
        self.client.login(username='testuser', password='pwd')
        response = self.client.post(
            reverse('list_subscribe', args=('moderate_subs.example.com', )),
            {'email': 'fritz@example.org'})
        self.assertEqual(len(self.mod_list.members), 0)
        self.assertEqual(len(self.mod_list.requests), 1)
        self.assertRedirects(
                response, reverse('list_summary',
                                  args=('moderate_subs.example.com', )))
        self.assertHasSuccessMessage(response)

    def test_subscribe_mod_then_open(self):
        # The list is moderated when the subscription is requested, then the
        # list is switched to open.
        self.client.login(username='testuser', password='pwd')
        response = self.client.post(
            reverse('list_subscribe', args=('moderate_subs.example.com', )),
            {'email': 'test@example.com'})
        self.assertEqual(len(self.mod_list.members), 0)
        self.assertEqual(len(self.mod_list.requests), 1)
        self.assertHasSuccessMessage(response)
        # Switch the list to 'open'
        self.mod_list.settings['subscription_policy'] = 'open'
        self.mod_list.settings.save()
        self.assertEqual(self.mod_list.settings['subscription_policy'], 'open')
        # Subscribe the user (they are now allowed to self-subscribe)
        self.mod_list.subscribe('test@example.com')
        # Login as the owner to accept the subscription
        User.objects.create_user('testowner', 'owner@example.com', 'pwd')
        self.mod_list.add_owner('owner@example.com')
        self.client.logout()
        self.client.login(username='testowner', password='pwd')
        accept_url = reverse(
                'handle_subscription_request',
                args=['moderate_subs.example.com',
                      self.mod_list.requests[0]['token'], 'accept'])
        response = self.client.get(accept_url)
        self.assertRedirects(response,
                             reverse('list_subscription_requests',
                                     args=['moderate_subs.example.com']))
        message = self.assertHasSuccessMessage(response)
        self.assertIn('Already subscribed', message)

    def test_mass_subscribe(self):
        # Perform mass subscription
        User.objects.create_user('testowner', 'owner@example.com', 'pwd')
        self.open_list.add_owner('owner@example.com')
        self.client.login(username='testowner', password='pwd')
        email_list = 'fritz@example.org\nkane@example.org\nabel@example.org\n'
        response = self.client.post(
            reverse('mass_subscribe', args=('open_list.example.com',)),
            {'emails': email_list})
        self.assertEqual(len(self.open_list.members), 3)
