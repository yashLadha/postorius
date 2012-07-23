# -*- coding: utf-8 -*-
# Copyright (C) 2012 by the Free Software Foundation, Inc.
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
from django.utils.translation import gettext as _
from mailman.client import Client
from urllib2 import HTTPError


logger = logging.getLogger(__name__)


def postorius(request):
    """Add template variables to context.
    """
    # extend_template (no page header/footer when requested via AJAX)
    if request.is_ajax():
        extend_template = "postorius/base_ajax.html"
    else:
        extend_template = "postorius/base.html"

    return {'MAILMAN_THEME': settings.MAILMAN_THEME,
            'extend_template': extend_template}
