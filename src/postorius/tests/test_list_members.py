# -*- coding: utf-8 -*-
# Copyright (C) 2012 by the Free Software Foundation, Inc.
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

from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import PermissionDenied
from django.utils import unittest
from mock import patch


class ListMembersViewTest(unittest.TestCase):
    """Tests for the ListMembersView."""

    def setUp(self):
        from django.test.client import RequestFactory
        from postorius.tests.utils import create_mock_list, create_mock_member
        self.request_factory = RequestFactory()
        # create a mock list with members
        list_name = 'foolist@example.org'
        self.mock_list = create_mock_list(dict(
            fqdn_listname=list_name,
            members=[
                create_mock_member(dict(
                    fqdn_listname=list_name,
                    address='les@example.org')),
                create_mock_member(dict(
                    fqdn_listname=list_name,
                    address='ler@example.com')),
            ]))

    def test_get_list(self):
        """Test if list members are retreived correctly."""
        from postorius.views import ListMembersView
        # test get_list
        view = ListMembersView()
        with patch('mailmanclient.Client.get_list') as mock:
            mock.return_value = self.mock_list
            the_list = view._get_list('foolist@example.org')
            self.assertEqual(the_list.members[0].address, 'les@example.org')
            self.assertEqual(the_list.members[1].address, 'ler@example.com')

    def test_dispatch(self):
        """Test if list members are retreived correctly."""
        from postorius.views import ListMembersView
        # test get_list
        view = ListMembersView()
        with patch('mailmanclient.Client.get_list') as mock:
            mock.return_value = self.mock_list
            the_list = view._get_list('foolist@example.org')
            request = self.request_factory.get(
                '/lists/foolist@example.org/members/')
            request.user = User.objects.create_superuser('sux', 'su@sodo.org',
                                                         'pwd')
            view.dispatch(request, fqdn_listname='foolist@example.org')
            self.assertEqual(self.mock_list, view.mailing_list)

    def test_return_code_by_user(self):
        """Test response status code by user status.
        """
        from postorius.views import ListMembersView
        with patch('mailmanclient.Client.get_list') as mock:
            mock.return_value = self.mock_list
            request = self.request_factory.get(
                '/lists/foolist@example.org/members/')
            # anonymous users should be redirected
            request.user = AnonymousUser()
            self.assertRaises(PermissionDenied, ListMembersView.as_view(),
                              request, fqdn_listname='foolist@example.org')
            # logged in users should be redirected
            request.user = User.objects.create_user('les', 'les@primus.org',
                                                    'pwd')
            self.assertRaises(PermissionDenied, ListMembersView.as_view(),
                              request, fqdn_listname='foolist@example.org')
            # superusers should get the page
            request.user = User.objects.create_superuser('su', 'su@sodo.org',
                                                         'pwd')
            response = ListMembersView.as_view()(
                request,
                fqdn_listname='foolist@example.org')
            self.assertEqual(response.status_code, 200)

    def tearDown(self):
        pass
