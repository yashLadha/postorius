# -*- coding: utf-8 -*-
# Copyright (C) 1998-2015 by the Free Software Foundation, Inc.
#
# This file is part of Postorius.
#
# Postorius is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# Postorius is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# Postorius.  If not, see <http://www.gnu.org/licenses/>.


import logging


from django.forms.formsets import formset_factory
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import (login_required,
                                            user_passes_test)
from django.contrib.auth.models import User
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.generic import TemplateView
try:
    from urllib2 import HTTPError
except ImportError:
    from urllib.error import HTTPError

from postorius import utils
from postorius.models import (
    MailmanUser, MailmanConnectionError, MailmanApiError, Mailman404Error,
    AddressConfirmationProfile)
from postorius.forms import *
from postorius.auth.decorators import *
from postorius.views.generic import MailmanUserView
from smtplib import SMTPException


class UserMailmanSettingsView(MailmanUserView):
    """The logged-in user's global Mailman Preferences."""

    @method_decorator(login_required)
    def post(self, request):
        try:
            mm_user = MailmanUser.objects.get(address=request.user.email)
            global_preferences_form = UserPreferences(request.POST)
            if global_preferences_form.is_valid():
                preferences = mm_user.preferences
                for key in global_preferences_form.fields.keys():
                    preferences[
                        key] = global_preferences_form.cleaned_data[key]
                preferences.save()
                messages.success(request, _('Your preferences have been updated.'))
            else:
                messages.error(request, _('Something went wrong.'))
        except MailmanApiError:
            return utils.render_api_error(request)
        except Mailman404Error as e:
            messages.error(request, e.msg)
        return redirect("user_mailmansettings")

    @method_decorator(login_required)
    def get(self, request):
        try:
            mm_user = MailmanUser.objects.get_or_create_from_django(request.user)
        except MailmanApiError:
            return utils.render_api_error(request)
        settingsform = UserPreferences(initial=mm_user.preferences)
        return render_to_response('postorius/user/mailman_settings.html',
                                  {'mm_user': mm_user,
                                   'settingsform': settingsform},
                                  context_instance=RequestContext(request))


class UserAddressPreferencesView(MailmanUserView):
    """The logged-in user's address-based Mailman Preferences."""

    @method_decorator(login_required)
    def post(self, request):
        try:
            mm_user = MailmanUser.objects.get(address=request.user.email)
            formset_class = formset_factory(UserPreferences)
            formset = formset_class(request.POST)
            if formset.is_valid():
                for form, address in zip(formset.forms, mm_user.addresses):
                    preferences = address.preferences
                    for key in form.fields.keys():
                        preferences[key] = form.cleaned_data[key]
                    preferences.save()
                messages.success(request, _('Your preferences have been updated.'))
            else:
                messages.error(request, _('Something went wrong.'))
        except MailmanApiError:
            return utils.render_api_error(request)
        except HTTPError as e:
            messages.error(request, e.msg)
        return redirect("user_address_preferences")

    @method_decorator(login_required)
    def get(self, request):
        try:
            helperform = UserPreferences()
            mm_user = MailmanUser.objects.get(address=request.user.email)
            addresses = mm_user.addresses
            AFormset = formset_factory(UserPreferences, extra=len(addresses._addresses))
            formset = AFormset()
            zipped_data = zip(formset.forms, addresses)
            for form, address in zipped_data:
                form.initial = address.preferences
        except MailmanApiError:
            return utils.render_api_error(request)
        except Mailman404Error:
            return render_to_response(
                'postorius/user/address_preferences.html',
                {'nolists': 'true'},
                context_instance=RequestContext(request))
        return render_to_response('postorius/user/address_preferences.html',
                                  {'mm_user': mm_user,
                                   'addresses': addresses,
                                   'helperform': helperform,
                                   'formset': formset,
                                   'zipped_data': zipped_data},
                                  context_instance=RequestContext(request))


class UserSubscriptionPreferencesView(MailmanUserView):
    """The logged-in user's subscription-based Mailman Preferences."""

    @method_decorator(login_required)
    def post(self, request):
        try:
            subscriptions = self._get_memberships()
            formset_class = formset_factory(UserPreferences)
            formset = formset_class(request.POST)
            if formset.is_valid():
                for form, subscription in zip(formset.forms, subscriptions):
                    preferences = subscription.preferences
                    for key in form.cleaned_data.keys():
                        preferences[key] = form.cleaned_data[key]
                    preferences.save()
                messages.success(request, _('Your preferences have been updated.'))
            else:
                messages.error(request, _('Something went wrong.'))
        except MailmanApiError:
            return utils.render_api_error(request)
        except HTTPError as e:
            messages.error(request, e.msg)
        return redirect("user_subscription_preferences")

    @method_decorator(login_required)
    def get(self, request):
        try:
            subscriptions = self._get_memberships()
            Mformset = formset_factory(
                UserPreferences, extra=len(subscriptions))
            formset = Mformset()
            zipped_data = zip(formset.forms, subscriptions)
            for form, subscription in zipped_data:
                form.initial = subscription.preferences
        except MailmanApiError:
            return utils.render_api_error(request)
        except Mailman404Error:
            return render_to_response(
                'postorius/user/subscription_preferences.html',
                {'nolists': 'true'},
                context_instance=RequestContext(request))
        return render_to_response(
            'postorius/user/subscription_preferences.html',
            {'zipped_data': zipped_data,
             'formset': formset},
            context_instance=RequestContext(request))


class UserSubscriptionsView(MailmanUserView):

    """Shows the subscriptions of a user.
    """

    def get(self, request):
        memberships = self._get_memberships()
        return render_to_response('postorius/user/subscriptions.html',
                                  {'memberships': memberships},
                                  context_instance=RequestContext(request))


class AddressActivationView(TemplateView):
    """
    Starts the process of adding additional email addresses to a mailman user
    record. Forms are processes and email notifications are sent accordingly.
    """

    @method_decorator(login_required)
    def get(self, request):
        form = AddressActivationForm(initial={'user_email': request.user.email})
        return render_to_response('postorius/user/address_activation.html',
                                  {'form': form},
                                  context_instance=RequestContext(request))

    @method_decorator(login_required)
    def post(self, request):
        form = AddressActivationForm(request.POST)
        if form.is_valid():
            profile = AddressConfirmationProfile.objects.create_profile(
                email=form.cleaned_data['email'], user=request.user)
            try:
                profile.send_confirmation_link(request)
            except SMTPException:
                messages.error(request, _('The email confirmation message could not be sent. %s')
                               % profile.activation_key)
            return render_to_response('postorius/user/address_activation_sent.html',
                                      context_instance=RequestContext(request))
        return render_to_response('postorius/user/address_activation.html',
                                  {'form': form},
                                  context_instance=RequestContext(request))


@login_required()
def user_profile(request, user_email=None):
    utils.set_other_emails(request.user)
    try:
        mm_user = MailmanUser.objects.get_or_create_from_django(request.user)
    except MailmanApiError:
        return utils.render_api_error(request)
    return render_to_response('postorius/user/profile.html',
                              {'mm_user': mm_user},
                              context_instance=RequestContext(request))


def _add_address(request, user_email, address):
    # Add an address to a user record in mailman.
    try:
        try:
            mailman_user = MailmanUser.objects.get(address=user_email)
        except Mailman404Error:
            mailman_user = MailmanUser.objects.create(user_email, '')
        mailman_user.add_address(address)
    except (MailmanApiError, MailmanConnectionError):
        messages.error(request, _('The address could not be added.'))


def address_activation_link(request, activation_key):
    """
    Checks the given activation_key. If it is valid, the saved address will be
    added to mailman. Also, the corresponding profile record will be removed.
    If the key is not valid, it will be ignored.
    """
    try:
        profile = AddressConfirmationProfile.objects.get(
            activation_key=activation_key)
        if not profile.is_expired:
            _add_address(request, profile.user.email, profile.email)
            profile.delete()
            messages.success(request, _('The email address has been activated!'))
        else:
            profile.delete()
            messages.error(request, _('The activation link has expired, please add the email again!'))
            return redirect('address_activation')
    except AddressConfirmationProfile.DoesNotExist:
        messages.error(request, _('The activation link is invalid'))
    return redirect('list_index')
