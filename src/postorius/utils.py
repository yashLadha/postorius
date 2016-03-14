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
from django.shortcuts import render
from django.template import RequestContext
from mailmanclient import Client
from django.utils.translation import gettext as _


logger = logging.getLogger(__name__)


def get_client():
    return Client('{0}/3.0'.format(settings.MAILMAN_REST_API_URL),
                  settings.MAILMAN_REST_API_USER,
                  settings.MAILMAN_REST_API_PASS)


def render_api_error(request):
    """Renders an error template.
    Use if MailmanApiError is catched.
    """
    return render(request, 'postorius/errors/generic.html',
                  {'error': _('Mailman REST API not available. '
                              'Please start Mailman core.')})


class MailmanPaginator(Paginator):
    """
    Subclass of Django's Paginator that works with MailmanClient's 'get_*_page'
    functions. Use the function reference as the first argument::

        MailmanPaginator(get_member_page, 25)

    """

    def __init__(self, function, per_page, **kwargs):
        self.function = function
        super(MailmanPaginator, self).__init__(None, per_page, **kwargs)

    def page(self, number):
        """
        Returns a Page object for the given 1-based page number.
        """
        number = self.validate_number(number)
        result = self.function(count=self.per_page, page=number)
        if self._count is None:
            self._count = result.total_size
        return self._get_page(result, number, self)

    def _get_count(self):
        """
        Returns the total number of objects, across all pages.
        """
        if self._count is None:
            # For now we need to get the first page to have the total_size.
            # Mitigate the price of this call by using count=1.
            result = self.function(count=1, page=1)
            self._count = result.total_size
        return self._count
    count = property(_get_count)



def paginate(request, collection, count=20, paginator_class=Paginator):
    # count is the number of items per page
    paginator = paginator_class(collection, count)
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
    if hasattr(user, 'other_emails'):
        return
    user.other_emails = []
    if not user.is_authenticated():
        return
    try:
        mm_user = MailmanUser.objects.get(address=user.email)
        user.other_emails = [str(address) for address in mm_user.addresses
                             if address.verified_on is not None]
    except (MailmanApiError, Mailman404Error, AttributeError) as e:
        # MailmanApiError: No connection to Mailman
        # Mailman404Error: The user does not have a mailman user associated
        # AttributeError: Anonymous user
        logger.warning("Mailman error while setting other emails for %s: %r",
                       user.email, e)
        return
    if user.email in user.other_emails:
        user.other_emails.remove(user.email)
