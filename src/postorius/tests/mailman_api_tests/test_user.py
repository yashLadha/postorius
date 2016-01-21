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
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase
from six.moves.urllib_parse import quote

from postorius.models import MailmanUser
from postorius.tests import MM_VCR
from postorius.utils import get_client


logger = logging.getLogger(__name__)
vcr_log = logging.getLogger('vcr')
vcr_log.setLevel(logging.WARNING)


class MailmanUserTest(TestCase):
    """
    Tests for the mailman user preferences settings page.
    """

    @MM_VCR.use_cassette('mailman_user.yaml')
    def setUp(self):
        self.domain = get_client().create_domain('example.com')
        self.foo_list = self.domain.create_list('foo')
        self.user = User.objects.create_user(
            'user', 'user@example.com', 'testpass')
        self.mm_user = MailmanUser.objects.create_from_django(self.user)

    @MM_VCR.use_cassette('mailman_user.yaml')
    def tearDown(self):
        self.foo_list.delete()
        self.mm_user.delete()
        self.user.delete()
        self.domain.delete()

    def _check_redirect_login(self, url):
        response = self.client.get(url)
        if '%40' not in url: # Django < 1.8
            url = quote(url)
        expected_redirect = 'http://testserver%s?next=%s' % (
            reverse(settings.LOGIN_URL), url)
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['location'], expected_redirect)

    @MM_VCR.use_cassette('mailman_user_access.yaml')
    def test_page_not_accessible_if_not_logged_in(self):
        self._check_redirect_login(reverse('user_address_preferences'))

    @MM_VCR.use_cassette('mailman_user_address_prefs.yaml')
    def test_address_based_preferences(self):
        self.client.login(username='user', password='testpass')
        self.mm_user.add_address('user2@example.com')
        self.mm_user.add_address('user3@example.com')
        response = self.client.get(reverse('user_address_preferences'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["formset"]), 3)
        self.assertEqual(len(response.context["zipped_data"]), 3)
        #self.assertEqual(
        #    response.context["formset"].initial['archive_policy'], 'public')
