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

from django.conf import settings
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from mailmanclient import Client


logger = logging.getLogger(__name__)


def get_client():
    return Client('{0}/3.0'.format(settings.MAILMAN_REST_API_URL),
                  settings.MAILMAN_REST_API_USER,
                  settings.MAILMAN_REST_API_PASS)


def render_api_error(request):
    """Renders an error template.
    Use if MailmanApiError is catched.
    """
    return render_to_response(
        'postorius/errors/generic.html',
        {'error': "Mailman REST API not available.  "
                  "Please start Mailman core."},
        context_instance=RequestContext(request))


def paginate(request, collection, count=20):
    # count is the number of items per page
    paginator = Paginator(collection, count)
    page = request.GET.get('page')
    try:
        results = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        results = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        results = paginator.page(paginator.num_pages)
    return results


def set_other_emails(user):
    from postorius.models import MailmanUser, MailmanApiError, Mailman404Error
    user.other_emails = []
    if not user.is_authenticated():
        return
    try:
        mm_user = MailmanUser.objects.get(address=user.email)
        user.other_emails = [str(address) for address in mm_user.addresses
                             if address.verified_on is not None]
    except (MailmanApiError, Mailman404Error, AttributeError):
        # MailmanApiError: No connection to Mailman
        # Mailman404Error: The user does not have a mailman user associated with it.
        # AttributeError: Anonymous user
        return
    if user.email in user.other_emails:
        user.other_emails.remove(user.email)
