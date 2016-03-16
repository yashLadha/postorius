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

from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from mock import patch
from smtplib import SMTPException

from postorius.models import AddressConfirmationProfile
from postorius.tests.utils import ViewTestCase


class TestProfile(ViewTestCase):
    """
    Tests to make sure the view is properly connected, renders the form
    correctly and starts the actual address activation process if a valid
    form is submitted.
    """

    def setUp(self):
        super(TestProfile, self).setUp()
        # We create a new user and log that user in.
        # We don't use Client().login because it triggers the browserid dance.
        self.user = User.objects.create_user(
            username='les', email='les@example.org', password='secret')
        self.client.post(reverse('user_login'),
                         {'username': 'les', 'password': 'secret'})

    def tearDown(self):
        # Log out and delete user.
        self.client.logout()
        self.user.delete()

    def test_view_contains_form(self):
        # The view context should contain a form.
        response = self.client.get(reverse('user_profile'))
        self.assertContains(response,
                            'You can add other addresses to your profile')

    def test_post_invalid_form_shows_error_msg(self):
        # Entering an invalid email address should render an error message.
        response = self.client.post(reverse('user_profile'),
                                    {'email': 'invalid_email',
                                     'user_email': self.user.email})
        self.assertContains(response, 'Enter a valid email address.')

    @patch.object(AddressConfirmationProfile, 'send_confirmation_link')
    def test_post_valid_form_shows_success_message(
            self, mock_send_confirmation_link):
        # Entering a valid email should render the activation_sent template.
        response = self.client.post(reverse('user_profile'),
                                    {'email': 'new_address@example.org',
                                     'user_email': self.user.email},
                                    follow=True)
        self.assertEqual(mock_send_confirmation_link.call_count, 1)
        self.assertContains(response, 'Please follow the instructions sent '
                                      'via email to confirm the address')

    @patch.object(AddressConfirmationProfile, 'send_confirmation_link')
    def test_post_valid_form_redirects_on_success(
            self, mock_send_confirmation_link):
        # Entering a valid email should render the activation_sent template.
        response = self.client.post(reverse('user_profile'), {
                                    'email': 'new_address@example.org',
                                    'user_email': self.user.email})
        self.assertEqual(mock_send_confirmation_link.call_count, 1)
        self.assertRedirects(response, reverse('user_profile'))

    @patch.object(AddressConfirmationProfile, 'send_confirmation_link',
                  side_effect=SMTPException())
    def test_post_form_with_smtp_exception(self, mock_send_confirmation_link):
        # If a smtp exception occurs display error
        response = self.client.post(reverse('user_profile'), {
            'email': 'new_address@example.org',
            'user_email': self.user.email}, follow=True)
        self.assertEqual(mock_send_confirmation_link.call_count, 1)
        self.assertContains(response, 'Currently emails can not be added, '
                                      'please try again later')
