# -*- coding: utf-8 -*-
# Copyright (C) 1998-2012 by the Free Software Foundation, Inc.
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
"""Postorius view decorators."""


from django.core.exceptions import PermissionDenied

from postorius.models import (Domain, List, Member, MailmanUser,
                              MailmanApiError, Mailman404Error)


def list_owner_required(fn):
    """Check if the logged in user is the list owner of the given list.
    Assumes that the request object is the first arg and that fqdn_listname
    is present in kwargs.
    """
    def wrapper(*args, **kwargs):
        user = args[0].user
        fqdn_listname = kwargs['fqdn_listname']
        if not user.is_authenticated():
            raise PermissionDenied
        if user.is_superuser:
            return fn(*args, **kwargs)
        mlist = List.objects.get_or_404(fqdn_listname=fqdn_listname)
        if user.email not in mlist.owners:
            raise PermissionDenied
        else:
            user.is_list_owner = True
            return fn(*args, **kwargs)
    return wrapper


def list_moderator_required(fn):
    """Check if the logged in user is a moderator of the given list.
    Assumes that the request object is the first arg and that fqdn_listname
    is present in kwargs.
    """
    def wrapper(*args, **kwargs):
        user = args[0].user
        fqdn_listname = kwargs['fqdn_listname']
        if not user.is_authenticated():
            raise PermissionDenied
        if user.is_superuser:
            return fn(*args, **kwargs)
        mlist = List.objects.get_or_404(fqdn_listname=fqdn_listname)
        if user.email not in mlist.moderators and \
                user.email not in mlist.owners:
            raise PermissionDenied
        else:
            user.is_list_moderator = True
            return fn(*args, **kwargs)
    return wrapper
