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
from django.test import Client, TestCase
from django.test.utils import override_settings
from urllib2 import HTTPError

from postorius.tests import MM_VCR
from postorius.utils import get_client


logger = logging.getLogger(__name__)
vcr_log = logging.getLogger('vcr')
vcr_log.setLevel(logging.WARNING)


API_CREDENTIALS = {'MAILMAN_API_URL': 'http://localhost:9001',
                   'MAILMAN_USER': 'restadmin',
                   'MAILMAN_PASS': 'restpass'}


@override_settings(**API_CREDENTIALS)
class TestSubscriptionPolicyOpen(TestCase):
    """Tests for the list members page.

    Tests permissions and creation of list owners and moderators.
    """

    @MM_VCR.use_cassette('list_subscription.yaml')
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
        # Set subscription policy to open
        settings = self.foo_list.settings
        settings['subscription_policy'] = 'open'
        settings.save()
        self.user = User.objects.create_user(
            'testuser', 'test@example.com', 'testpass')

    @MM_VCR.use_cassette('list_subscription.yaml')
    def tearDown(self):
        self.foo_list.delete()
        self.user.delete()

    @MM_VCR.use_cassette('list_subscription.yaml')
    def test_subscribing_adds_member(self):
        print(self.foo_list.settings['subscription_policy'])
        response = self.client.post(
            reverse('list_subscribe', args=('foo.example.com', )),
            {'email': 'fritz@example.org'})
        print(response.status_code)
        print(self.foo_list.members)
        self.assertEqual(2, len(self.foo_list.members))
