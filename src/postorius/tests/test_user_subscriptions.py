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

from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.test import TestCase


class UserSubscriptionViewTest(TestCase):

    def setUp(self):
        User.objects.create_user('testuser', 'test@example.com', 'testpass')

    def tearDown(self):
        User.objects.all().delete()

    def test_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('user_subscriptions'))
        self.assertEquals(response.status_code, 302)

    def accessible_if_logged_in(self):
        self.client.login('testuser')
        response = self.client.get(reverse('user_subscriptions'))
        self.assertEquals(response.status_code, 200)
