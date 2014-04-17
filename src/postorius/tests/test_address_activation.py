from __future__ import (absolute_import, division, print_function,
                        unicode_literals)


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
        form = AddressActivationForm({'email': 'les@example.org'})
        self.assertTrue(form.is_valid())
    
    def test_invalid_email_is_not_valid(self):
        form = AddressActivationForm({'email': 'les@example'})
        self.assertFalse(form.is_valid())


class TestAddressActivationView(unittest.TestCase):

    def test_view_is_connected(self):
        # The view should be connected in the url configuration.
        response = Client().get(reverse('address_activation'))
        self.assertEqual(response.status_code, 200)

    def test_view_contains_form(self):
        # The view context should contain a form.
        response = Client().get(reverse('address_activation'))
        self.assertTrue('form' in response.context)

    def test_view_renders_correct_template(self):
        # The view should render the user_address_activation template. 
        response = Client().get(reverse('address_activation'))
        self.assertTrue('postorius/user_address_activation.html' 
                        in [t.name for t in response.templates])

    def test_post_invalid_form_shows_error_msg(self):
        # Entering an invalid email address should render an error message.
        response = Client().post(reverse('address_activation'),
                                 {'email': 'invalid_email'})
        self.assertTrue('Enter a valid email address.' in 
                        response.content)

    @patch.object(AddressActivationView, '_handle_address')
    def test_post_valid_form_renders_success_template(self, handle_address_mock):
        # Entering a valid email should render the activation_sent template.
        response = Client().post(reverse('address_activation'),
                                 {'email': 'new_address@example.org'})
        self.assertTrue('postorius/user_address_activation_sent.html' 
                        in [t.name for t in response.templates])

    @patch.object(AddressActivationView, '_handle_address')
    def test_post_valid_form_calls_handle_address_method(self, handle_address_mock):
        # Entering a valid email should render the activation_sent template.
        response = Client().post(reverse('address_activation'),
                                 {'email': 'new_address@example.org'})
        self.assertEqual(handle_address_mock.call_count, 1)
        args, kwargs = handle_address_mock.call_args
        self.assertTrue('new_address@example.org' in args)
