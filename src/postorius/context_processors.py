# -*- coding: utf-8 -*-
# Copyright (C) 2012-2015 by the Free Software Foundation, Inc.
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

import logging

from django.conf import settings
from django.core.urlresolvers import reverse, NoReverseMatch
from django.shortcuts import resolve_url

logger = logging.getLogger(__name__)


def postorius(request):
    """Add template variables to context.
    """
    # Use a template so that the page header/footer is suppressed when
    # requested via AJAX

    if request.is_ajax():
        template_to_extend = "postorius/base_ajax.html"
    else:
        template_to_extend = "postorius/base.html"

    return {
        'postorius_base_template': template_to_extend,
    }
