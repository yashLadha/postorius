# -*- coding: utf-8 -*-
# Copyright (C) 2012-2014 by the Free Software Foundation, Inc.
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

from mailmanclient.tests.utils import FakeMailmanClient

from mock import patch
from django.test import TestCase


def setup_module():
    FakeMailmanClient.setUp()

def teardown_module():
    FakeMailmanClient.tearDown()


class MMTestCase(TestCase):

    def _pre_setup(self):
        super(MMTestCase, self)._pre_setup()
        self.mm_client = FakeMailmanClient(
            'http://localhost:8001/3.0', "restadmin", "restpass")
        self.mm_client_patcher = patch('postorius.utils.Client', lambda *a, **kw: self.mm_client)
        self.mm_client_patcher.start()
        self.mm_client.create_domain(
            'example.com',
            contact_address='postmaster@example.com',
            base_url='lists.example.com')

    def _post_teardown(self):
        self.mm_client_patcher.stop()
        self.mm_client.delete_domain('example.com')
        super(MMTestCase, self)._post_teardown()
