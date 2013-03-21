# -*- coding: utf-8 -*-
# Copyright (C) 1998-2013 by the Free Software Foundation, Inc.
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


import re
import sys
import json
import logging


from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.decorators import (login_required,
                                            permission_required,
                                            user_passes_test)
from django.contrib.auth.forms import (AuthenticationForm, PasswordResetForm,
                                       SetPasswordForm, PasswordChangeForm)
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, redirect
from django.template import Context, loader, RequestContext
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from urllib2 import HTTPError

from mailmanclient import Client
from postorius import utils
from postorius.models import (Domain, List, Member, MailmanUser,
                              MailmanApiError, Mailman404Error)
from postorius.forms import *
from postorius.auth.decorators import *
from postorius.views.generic import MailingListView, MailmanUserView


logger = logging.getLogger(__name__)


@login_required
def user_settings(request, tab="membership",
                  template='postorius/user_settings.html',
                  fqdn_listname=None):
    """
    Change the user or the membership settings.
    The user must be logged in to be allowed to change any settings.
    TODO: * add CSS to display tabs ??
          * add missing functionality in REST server and client and
            change to the correct calls here
    """
    member = request.user.username
    message = ''
    form = None
    the_list = None
    membership_lists = []

    try:
        c = Client('%s/3.0' % settings.REST_SERVER, settings.API_USER,
                   settings.API_PASS)
        if tab == "membership":
            if fqdn_listname:
                the_list = List.objects.get(fqdn_listname=fqdn_listname)
                user_object = the_list.get_member(member)
            else:
                message = ("")
                for mlist in List.objects.all():
                    try:
                        mlist.get_member(member)
                        membership_lists.append(mlist)
                    except:
                        pass
        else:
            # address_choices for the 'address' field must be a list of
            # tuples of length 2
            raise Exception("")
            address_choices = [[addr, addr] for addr in user_object.address]
    except AttributeError, e:
        return render_to_response(
            'postorius/errors/generic.html',
            {'error': str(e) + "REST API not found / Offline"},
            context_instance=RequestContext(request))
    except ValueError, e:
        return render_to_response('postorius/errors/generic.html',
                                  {'error': e},
                                  context_instance=RequestContext(request))
    except HTTPError, e:
        return render_to_response(
            'postorius/errors/generic.html',
            {'error': _("List ") + fqdn_listname + _(" does not exist")},
            context_instance=RequestContext(request))
    #-----------------------------------------------------------------
    if request.method == 'POST':
        # The form enables both user and member settings. As a result
        # we must find out which was the case.
        raise Exception("Please fix bug prior submitting the form")
        if tab == "membership":
            form = MembershipSettings(request.POST)
            if form.is_valid():
                member_object = c.get_member(member, request.GET["list"])
                member_object.update(request.POST)
                message = "The membership settings have been updated."
        else:
            # the post request came from the user tab
            # the 'address' field need choices as a tuple of length 2
            addr_choices = [[request.POST["address"], request.POST["address"]]]
            form = UserSettings(addr_choices, request.POST)
            if form.is_valid():
                user_object.update(request.POST)
                # to get the full list of addresses we need to
                # reinstantiate the form with all the addresses
                # TODO: should return the correct settings from the DB,
                # not just the address_choices (add mock data to _User
                # class and make the call with 'user_object.info')
                form = UserSettings(address_choices)
                message = "The user settings have been updated."

    else:
        if tab == "membership" and fqdn_listname:
            if fqdn_listname:
                # TODO : fix LP:821069 in mailman.client
                the_list = List.objects.get(fqdn_listname=fqdn_listname)
                member_object = the_list.get_member(member)
                # TODO: add delivery_mode and deliver_status from a
                # list of tuples at one point, currently we hard code
                # them in forms.py
                # instantiate the form with the correct member info
                """
                acknowledge_posts
                hide_address
                receive_list_copy
                receive_own_postings
                delivery_mode
                delivery_status
                """
                data = {}
                form = MembershipSettings(data)
        elif tab == "user":
            # TODO: should return the correct settings from the DB,
            # not just the address_choices (add mock data to _User
            # class and make the call with 'user_object._info') The 'language'
            # field must also be added as a list of tuples with correct
            # values (is currently hard coded in forms.py).
            data = {}  # Todo https://bugs.launchpad.net/mailman/+bug/821438
            form = UserSettings(data)

    return render_to_response(template,
                              {'form': form,
                               'tab': tab,
                               'list': the_list,
                               'membership_lists': membership_lists,
                               'message': message,
                               'member': member},
                              context_instance=RequestContext(request))


class UserSummaryView(MailmanUserView):
    """Shows a summary of a user.
    """

    @method_decorator(user_passes_test(lambda u: u.is_superuser))
    def get(self, request, user_id):
        settingsform = MembershipSettings()
        memberships = self._get_memberships()
        return render_to_response('postorius/users/summary.html',
                                  {'mm_user': self.mm_user,
                                   'settingsform': settingsform,
                                   'memberships': memberships},
                                  context_instance=RequestContext(request))


class UserSubscriptionsView(MailmanUserView):
    """Shows the subscriptions of a user.
    """

    def get(self, request):
        memberships = self._get_memberships()
        return render_to_response('postorius/user_subscriptions.html',
                                  {'memberships': memberships},
                                  context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def user_index(request, template='postorius/users/index.html'):
    """Show a table of all users.
    """
    error = None
    try:
        mm_users = MailmanUser.objects.all()
    except MailmanApiError:
        return utils.render_api_error(request)
    return render_to_response(template,
                              {'error': error,
                               'mm_users': mm_users},
                              context_instance=RequestContext(request))


@user_passes_test(lambda u: u.is_superuser)
def user_new(request):
    message = None
    if request.method == 'POST':
        form = UserNew(request.POST)
        if form.is_valid():
            user = MailmanUser(display_name=form.cleaned_data['display_name'],
                               email=form.cleaned_data['email'],
                               password=form.cleaned_data['password'])
            try:
                user.save()
            except MailmanApiError:
                return utils.render_api_error(request)
            except HTTPError, e:
                messages.error(request, e)
            else:
                messages.success(request, _("New User registered"))
            return redirect("user_index")
    else:
        form = UserNew()
    return render_to_response('postorius/users/new.html',
                              {'form': form, 'message': message},
                              context_instance=RequestContext(request))


def user_logout(request):
    logout(request)
    return redirect('user_login')


def user_login(request, template='postorius/login.html'):
    if request.method == 'POST':
        form = AuthenticationForm(request.POST)
        user = authenticate(username=request.POST.get('username'),
                            password=request.POST.get('password'))
        if user is not None:
            logger.debug(user)
            if user.is_active:
                login(request, user)
                return redirect(request.GET.get('next', 'list_index'))
    else:
        form = AuthenticationForm()
    return render_to_response(template, {'form': form},
                              context_instance=RequestContext(request))


@login_required()
def user_profile(request, user_email=None):
    if not request.user.is_authenticated():
        return redirect('user_login')
    #try:
    #    the_user = User.objects.get(email=user_email)
    #except MailmanApiError:
    #    return utils.render_api_error(request)
    return render_to_response('postorius/user_profile.html',
                              # {'mm_user': the_user},
                              context_instance=RequestContext(request))


@login_required
def user_tasks(request):
    return render_to_response('postorius/user_tasks.html',
                              context_instance=RequestContext(request))

@login_required
def more_info_tab(request, formid=None, helpid=None, template='postorius/more_info_display.html'):
    """Displays more_info in new tab.
    """
    
    if(formid == 'list_settings'):
        form = ListSettings(visible_section='List Identity', visible_option='None', data=request.POST)
    
    for field in form:
        if field.name == helpid:
            help_text = field.help_text
    
    return render_to_response(template,
                              {'help_text':help_text,
                               'helpid':helpid},
                              context_instance=RequestContext(request))
    
