# -*- coding: utf-8 -*-
# Copyright (C) 1998-2016 by the Free Software Foundation, Inc.
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


from __future__ import absolute_import, unicode_literals

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.utils.translation import gettext as _
from django_mailman3.lib.mailman import get_mailman_client
try:
    from urllib2 import HTTPError
except ImportError:
    from urllib.error import HTTPError
from postorius import utils
from postorius.auth.decorators import superuser_required
from postorius.models import Domain, MailmanApiError
from postorius.forms import DomainNew


@login_required
@superuser_required
def domain_index(request):
    try:
        existing_domains = Domain.objects.all()
    except MailmanApiError:
        return utils.render_api_error(request)
    return render(request, 'postorius/domain/index.html',
                  {'domains': existing_domains})


@login_required
@superuser_required
def domain_new(request):
    if request.method == 'POST':
        form = DomainNew(request.POST)
        if form.is_valid():
            domain = Domain(mail_host=form.cleaned_data['mail_host'],
                            description=form.cleaned_data['description'],
                            owner=request.user.email)
            try:
                domain.save()
            except MailmanApiError:
                return utils.render_api_error(request)
            except HTTPError as e:
                messages.error(request, e)
            else:
                messages.success(request, _("New Domain registered"))
            return redirect("domain_index")
        else:
            messages.error(request, _('Please check the errors below'))
    else:
        form = DomainNew()
    return render(request, 'postorius/domain/new.html', {'form': form})


@login_required
@superuser_required
def domain_delete(request, domain):
    """Deletes a domain but asks for confirmation first.
    """
    if request.method == 'POST':
        try:
            client = get_mailman_client()
            client.delete_domain(domain)
            messages.success(request,
                             _('The domain %s has been deleted.' % domain))
            return redirect("domain_index")
        except HTTPError as e:
            messages.error(request,
                           _('The domain could not be deleted: %s' % e.msg))
            return redirect("domain_index")
    return render(request, 'postorius/domain/confirm_delete.html',
                  {'domain': domain})
