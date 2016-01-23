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
import time
import logging

from django.conf import settings
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.shortcuts import resolve_url
from django.test import Client, TestCase

try:
    from urllib2 import HTTPError
except ImportError:
    from urllib.error import HTTPError

from postorius.utils import get_client
from postorius.tests import MM_VCR


logger = logging.getLogger(__name__)
vcr_log = logging.getLogger('vcr')
vcr_log.setLevel(logging.WARNING)


class DomainCreationTest(TestCase):
    """Tests for the new list page."""

    @MM_VCR.use_cassette('test_domain_creation.yaml')
    def setUp(self):
        self.user = User.objects.create_user('user', 'user@example.com', 'pwd')
        self.superuser = User.objects.create_superuser('su', 'su@example.com',
                                                       'pwd')

    @MM_VCR.use_cassette('test_list_creation.yaml')
    def tearDown(self):
        self.user.delete()
        self.superuser.delete()
        try:
            get_client().delete_domain('example.com')
        except HTTPError:
            pass

    def test_permission_denied(self):
        self.client.login(username='user', password='pwd')
        response = self.client.get(reverse('domain_new'))
        self.assertRedirects(response, '{}?next={}'.format(resolve_url(settings.LOGIN_URL),
            reverse('domain_new')))

    @MM_VCR.use_cassette('test_list_creation.yaml')
    def test_new_domain_created_with_owner(self):
        self.client.login(username='su', password='pwd')
        post_data = {'mail_host': 'example.com',
                     'web_host': 'http://example.com',
                     'description': 'A new Domain.'}
        response = self.client.post(reverse('domain_new'), post_data, follow=True)
        
        self.assertContains(response, 'New Domain registered')
        self.assertRedirects(response, reverse('domain_index'))

        a_new_domain  = get_client().get_domain('example.com')
        self.assertEqual(a_new_domain.mail_host, u'example.com')
        self.assertEqual(a_new_domain.base_url, u'http://example.com')
        self.assertEqual(a_new_domain.owners[0]['user_id'],
                get_client().get_user('su@example.com').user_id)
        a_new_domain.delete()
