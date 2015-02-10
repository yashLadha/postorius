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
from django.utils import unittest

from postorius.forms import UserPreferences, DomainNew


class UserPreferencesTest(unittest.TestCase):

    def test_form_fields_valid(self):
        form = UserPreferences({
            'acknowledge_posts': 'True',
            'hide_address': 'True',
            'receive_list_copy': 'False',
            'receive_own_postings': 'False',
        })
        self.assertTrue(form.is_valid())

class DomainNewTest(unittest.TestCase):

    def test_form_fields_webhost(self):
        form = DomainNew({
            'mail_host': 'mailman.most-desirable.org',
            'web_host': 'http://mailman.most-desirable.org',
            'description': 'The Most Desirable organization',
            'contact_address': 'contact@mailman.most-desirable.org',
        })
        self.assertTrue(form.is_valid())

    def test_form_fields_webhost_invalid(self):
        form = DomainNew({
            'mail_host': 'mailman.most-desirable.org',
            'web_host': 'mailman.most-desirable.org',
            'description': 'The Most Desirable organization',
            'contact_address': 'contact@mailman.most-desirable.org',
        })
        self.assertFalse(form.is_valid())
