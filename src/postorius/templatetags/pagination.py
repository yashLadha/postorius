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

from django import template
from django.utils.html import conditional_escape


register = template.Library()


@register.simple_tag(takes_context=True)
def add_to_query_string(context, *args, **kwargs):
    """Adds or replaces parameters in the query string"""
    qs = context["request"].GET.copy()
    # create a dict from every args couple
    new_qs_elements = dict(zip(args[::2], args[1::2]))
    new_qs_elements.update(kwargs)
    # don't use the .update() method, it appends instead of overwriting.
    for key, value in new_qs_elements.iteritems():
        qs[key] = value
    return conditional_escape(qs.urlencode())
