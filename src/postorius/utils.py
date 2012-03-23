# -*- coding: utf-8 -*-
# Copyright (C) 1998-2010 by the Free Software Foundation, Inc.
#
# This file is part of GNU Mailman.
#
# GNU Mailman is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# GNU Mailman is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# GNU Mailman.  If not, see <http://www.gnu.org/licenses/>.

from django.shortcuts import render_to_response, redirect
from django.template import RequestContext


def get_domain_name(request):
    """Extracts a domain name from the request object.
    """ 
    if "HTTP_HOST" in request.META.keys():
        return request.META["HTTP_HOST"].split(":")[0]
    return None

def render_api_error(request):
    """Renders an error template.
    Use if MailmanApiError is catched.
    """
    return render_to_response('postorius/errors/generic.html', 
          {'error': "REST API not found / Offline"},
          context_instance=RequestContext(request))

