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

import logging

from django.conf import settings
from django.db import models
from django.http import Http404
from mailman.client import Client
from urllib2 import HTTPError


logger = logging.getLogger(__name__)


class MailmanApiError(Exception):
    """Raised if the API is not available.
    """
    pass

class Mailman404Error(Exception):
    """Proxy exception. Raised if the API returns 404."""
    pass


class MailmanRestManager(object):
    """Manager class to give a model class CRUD access to the API.
    Returns objects (or lists of objects) retrived from the API.
    """
    
    def __init__(self, resource_name, resource_name_plural, cls_name=None):
        self.client = Client('%s/3.0' % settings.REST_SERVER,
                             settings.API_USER, settings.API_PASS)
        self.resource_name = resource_name
        self.resource_name_plural = resource_name_plural

    def all(self):
        try:
            return getattr(self.client, self.resource_name_plural)
        except AttributeError:
            raise MailmanApiError

    def get(self, **kwargs):
        try:
            method = getattr(self.client, 'get_' + self.resource_name)
            return method(**kwargs)
        except AttributeError, e:
            raise MailmanApiError(e)
        except HTTPError, e:
            if e.code == 404:
                raise Mailman404Error
            else:
                raise

    def get_or_404(self, **kwargs):
        """Similar to `self.get` but raises standard Django 404 error.
        """
        try:
            return self.get(**kwargs)
        except Mailman404Error:
            raise Http404

    def create(self, **kwargs):
        try:
            method = getattr(self.client, 'create_' + self.resource_name)
            return method(**kwargs)
        except AttributeError, e:
            raise MailmanApiError(e)
        except HTTPError, e:
            if e.code == 409:
                raise MailmanApiError
            else:
                raise

    def delete(self):
        """Not implemented since the objects returned from the API
        have a `delete` method of their own.
        """
        pass


class MailmanListManager(MailmanRestManager):

    def __init__(self):
        super(MailmanListManager, self).__init__('list', 'lists')

    def all(self, only_public=False):
        try:
            objects = getattr(self.client, self.resource_name_plural)
        except AttributeError:
            raise MailmanApiError
        if only_public:
            public = []
            for obj in objects:
                if obj.settings.get('advertised', False):
                    public.append(obj)
            return public
        else:
            return objects

    def by_mail_host(self, mail_host, only_public=False):
        objects = self.all(only_public)
        host_objects = []
        for obj in objects:
            if obj.mail_host == mail_host:
                host_objects.append(obj)
        return host_objects


class MailmanRestModel(object):
    """Simple REST Model class to make REST API calls Django style.
    """
    MailmanApiError = MailmanApiError
    DoesNotExist = Mailman404Error

    def __init__(self, **kwargs):
        self.kwargs = kwargs

    def save(self):
        """Proxy function for `objects.create`. 
        (REST API uses `create`, while Django uses `save`.)
        """
        self.objects.create(**self.kwargs)


class Domain(MailmanRestModel):
    """Domain model class.
    """
    objects = MailmanRestManager('domain', 'domains')


class List(MailmanRestModel):
    """List model class.
    """
    objects = MailmanListManager()


class MailmanUser(MailmanRestModel):
    """MailmanUser model class.
    """
    objects = MailmanRestManager('user', 'users')


class Member(MailmanRestModel):
    """Member model class.
    """
    objects = MailmanRestManager('member', 'members')
