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


from django.conf.urls import include, url

from django.contrib import admin
admin.autodiscover()

from postorius import views

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url('', include('django_browserid.urls')),
    url(r'^$', views.list.list_index),
    url(r'^postorius/', include('postorius.urls')),
]
