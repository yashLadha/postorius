from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse
from django.test.client import Client, RequestFactory
from django.test.utils import override_settings
from django.utils import unittest
from mock import patch

from postorius.forms import AddressActivationForm
from postorius.views.user import AddressActivationView


class TestAddressActivationForm(unittest.TestCase):
    
    def test_valid_email_is_valid(self):
        data = {
            'email': 'les@example.org',
            'user_email': 'me@example.org',
        }
        form = AddressActivationForm(data)
        self.assertTrue(form.is_valid())
    
    def test_identical_emails_are_invalid(self):
        data = {
            'email': 'les@example.org',
            'user_email': 'les@example.org',
        }
        form = AddressActivationForm(data)
        self.assertFalse(form.is_valid())
    
    def test_invalid_email_is_not_valid(self):
        data = {
            'email': 'les@example',
            'user_email': 'me@example.org',
        }
        form = AddressActivationForm(data)
        self.assertFalse(form.is_valid())


class TestAddressActivationView(unittest.TestCase):
    """
    Tests to make sure the view is properly connected, renders the form
    correctly and starts the actual address activation process if a valid
    form is submitted. 
    """

    def setUp(self):
        # We create a new user and log that user in.
        # We don't use Client().login because it triggers the browserid dance.
        self.user = User.objects.create_user(
            username='les', email='les@example.org', password='secret')
        self.client = Client() 
        self.client.post(reverse('user_login'),
                         {'username': 'les', 'password': 'secret'})

    def tearDown(self):
        # Log out and delete user.
        self.client.logout()
        self.user.delete()

    def test_view_is_connected(self):
        # The view should be connected in the url configuration.
        response = self.client.get(reverse('address_activation'))
        self.assertEqual(response.status_code, 200)

    def test_view_contains_form(self):
        # The view context should contain a form.
        response = self.client.get(reverse('address_activation'))
        self.assertTrue('form' in response.context)

    def test_view_renders_correct_template(self):
        # The view should render the user_address_activation template. 
        response = self.client.get(reverse('address_activation'))
        self.assertTrue('postorius/user_address_activation.html' 
                        in [t.name for t in response.templates])

    def test_post_invalid_form_shows_error_msg(self):
        # Entering an invalid email address should render an error message.
        response = self.client.post(reverse('address_activation'),
                                    {
                                        'email': 'invalid_email',
                                        'user_email': self.user.email,
                                    })
        self.assertTrue('Enter a valid email address.' in 
                        response.content)

    @patch.object(AddressActivationView, '_handle_address')
    def test_post_valid_form_renders_success_template(self, handle_address_mock):
        # Entering a valid email should render the activation_sent template.
        response = self.client.post(reverse('address_activation'),
                                    {
                                        'email': 'new_address@example.org',
                                        'user_email': self.user.email,
                                    })
        self.assertTrue('postorius/user_address_activation_sent.html' 
                        in [t.name for t in response.templates])

    @patch.object(AddressActivationView, '_handle_address')
    def test_post_valid_form_calls_handle_address_method(self,
                                                         handle_address_mock):
        # Entering a valid email should call _handle_address with the request's
        # user instance as well as the email address to activate.
        response = self.client.post(reverse('address_activation'),
                                    {
                                        'email': 'new_address@example.org',
                                        'user_email': self.user.email,
                                    })
        self.assertEqual(handle_address_mock.call_count, 1)
        args, kwargs = handle_address_mock.call_args
        self.assertTrue(isinstance(args[0], User))
        self.assertEqual(args[1], 'new_address@example.org')


class TestAddressActivationStart(unittest.TestCase):
    """
    Tests the initiation of the address activation (sending the appropriate 
    emails, generating the token etc.).
    """

    def setUp(self):
        self.foo_user = User.objects.create_user(
            'foo', email='foo@example.org', password='pass')
        self.bar_user = User.objects.create_user(
            'bar', email='bar@example.org', password='pass')

    def tearDown(self):
        self.foo_user.delete()
        self.bar_user.delete()

    @patch.object(AddressActivationView, '_start_confirmation')
    @patch.object(AddressActivationView, '_notify_existing_user')
    def test_existing_user_detected(
            self, notify_existing_user_mock, start_confirmation_mock):
        # Using the email address of an existing user should hit the
        # _notify_existing_user method.
        AddressActivationView._handle_address(self.foo_user, 'bar@example.org')
        self.assertEqual(notify_existing_user_mock.call_count, 1)
        self.assertEqual(start_confirmation_mock.call_count, 0)

    @patch.object(AddressActivationView, '_start_confirmation')
    @patch.object(AddressActivationView, '_notify_existing_user')
    def test_confirmation_start(
            self, notify_existing_user_mock, start_confirmation_mock):
        # Using the email address of an existing user should hit the
        # _notify_existing_user method.
        AddressActivationView._handle_address(self.foo_user, 'new@address.org')
        self.assertEqual(notify_existing_user_mock.call_count, 0)
        self.assertEqual(start_confirmation_mock.call_count, 1)


class TestAddressActivationConfirmation(unittest.TestCase):
    """
    Tests the confirmation of an email address activation (validating token, 
    expiration, Mailman API calls etc.).
    """
    pass
