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

import time

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import resolve_url

try:
    from urllib2 import HTTPError
except ImportError:
    from urllib.error import HTTPError

from postorius.tests.utils import ViewTestCase


class DomainCreationTest(ViewTestCase):
    """Tests for the new list page."""

    def setUp(self):
        super(DomainCreationTest, self).setUp()
        self.user = User.objects.create_user('user', 'user@example.com', 'pwd')
        self.superuser = User.objects.create_superuser('su', 'su@example.com',
                                                       'pwd')

    def tearDown(self):
        self.user.delete()
        self.superuser.delete()
        try:
            self.mm_client.delete_domain('example.com')
        except HTTPError:
            pass

    def test_permission_denied(self):
        self.client.login(username='user', password='pwd')
        self.assertRedirectsToLogin(reverse('domain_new'))

    def test_new_domain_created_with_owner(self):
        self.client.login(username='su', password='pwd')
        post_data = {'mail_host': 'example.com',
                     'web_host': 'http://example.com',
                     'description': 'A new Domain.'}
        response = self.client.post(reverse('domain_new'), post_data,
                                    follow=True)

        self.assertContains(response, 'New Domain registered')
        self.assertRedirects(response, reverse('domain_index'))

        a_new_domain = self.mm_client.get_domain('example.com')
        self.assertEqual(a_new_domain.mail_host, u'example.com')
        self.assertEqual(a_new_domain.base_url, u'http://example.com')
        self.assertEqual(a_new_domain.owners[0]['user_id'],
                         self.mm_client.get_user('su@example.com').user_id)
        a_new_domain.delete()
