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

from django.shortcuts import render
from django.utils.translation import gettext as _


logger = logging.getLogger(__name__)


def render_api_error(request):
    """Renders an error template.
    Use if MailmanApiError is catched.
    """
    return render(request, 'postorius/errors/generic.html',
                  {'error': _('Mailman REST API not available. '
                              'Please start Mailman core.')})


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
