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
from __future__ import (
    absolute_import, division, print_function, unicode_literals)


import uuid
import logging

from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ImproperlyConfigured
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.core.urlresolvers import reverse
from django.dispatch import receiver
from django.db import models
from django.http import Http404
from django.template.loader import render_to_string
from mailmanclient import MailmanConnectionError
from postorius.utils import get_client
try:
    from urllib2 import HTTPError
except ImportError:
    from urllib.error import HTTPError

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_mailman_user(sender, **kwargs):
    if kwargs.get('created'):
        autocreate = False
        try:
            autocreate = settings.AUTOCREATE_MAILMAN_USER
        except AttributeError:
            pass
        if autocreate:
            user = kwargs.get('instance')
            try:
                MailmanUser.objects.create_from_django(user)
            except (MailmanApiError, HTTPError):
                pass


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
        self.resource_name = resource_name
        self.resource_name_plural = resource_name_plural

    def all(self):
        try:
            return getattr(get_client(), self.resource_name_plural)
        except AttributeError:
            raise MailmanApiError
        except MailmanConnectionError as e:
            raise MailmanApiError(e)

    def get(self, *args, **kwargs):
        try:
            method = getattr(get_client(), 'get_' + self.resource_name)
            return method(*args, **kwargs)
        except AttributeError as e:
            raise MailmanApiError(e)
        except HTTPError as e:
            if e.code == 404:
                raise Mailman404Error('Mailman resource could not be found.')
            else:
                raise
        except MailmanConnectionError as e:
            raise MailmanApiError(e)

    def get_or_404(self, *args, **kwargs):
        """Similar to `self.get` but raises standard Django 404 error.
        """
        try:
            return self.get(*args, **kwargs)
        except Mailman404Error:
            raise Http404
        except MailmanConnectionError as e:
            raise MailmanApiError(e)

    def create(self, *args, **kwargs):
        try:
            method = getattr(get_client(), 'create_' + self.resource_name)
            return method(*args, **kwargs)
        except AttributeError as e:
            raise MailmanApiError(e)
        except HTTPError as e:
            if e.code == 409:
                raise MailmanApiError
            else:
                raise
        except MailmanConnectionError:
            raise MailmanApiError

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
            objects = getattr(get_client(), self.resource_name_plural)
        except AttributeError:
            raise MailmanApiError
        except MailmanConnectionError as e:
            raise MailmanApiError(e)
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


class MailmanUserManager(MailmanRestManager):

    def __init__(self):
        super(MailmanUserManager, self).__init__('user', 'users')

    def create_from_django(self, user):
        return self.create(user.email, user.get_full_name())

    def get_or_create_from_django(self, user):
        try:
            return self.get(address=user.email)
        except Mailman404Error:
            return self.create_from_django(user)


class MailmanRestModel(object):
    """Simple REST Model class to make REST API calls Django style.
    """
    MailmanApiError = MailmanApiError
    DoesNotExist = Mailman404Error

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def save(self):
        """Proxy function for `objects.create`.
        (REST API uses `create`, while Django uses `save`.)
        """
        self.objects.create(*self.args, **self.kwargs)


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
    objects = MailmanUserManager()


class Member(MailmanRestModel):
    """Member model class.
    """
    objects = MailmanRestManager('member', 'members')


class AddressConfirmationProfile(models.Model):
    """
    Profile model for temporarily storing an activation key to register
    an email address.
    """
    email = models.EmailField(unique=True)
    activation_key = models.CharField(max_length=32, unique=True)
    created = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(User)

    def save(self, *args, **kwargs):
        self.activation_key = uuid.uuid4().hex
        super(AddressConfirmationProfile, self).save(*args, **kwargs)

    def __unicode__(self):
        return u'Address Confirmation Profile for {0}'.format(self.email)

    @property
    def is_expired(self):
        """
        a profile expires after 1 day by default.
        This can be configured in the settings.

            >>> EMAIL_CONFIRMATION_EXPIRATION_DELTA = timedelta(days=2)

        """
        expiration_delta = getattr(
            settings, 'EMAIL_CONFIRMATION_EXPIRATION_DELTA', timedelta(days=1))
        age = datetime.now().replace(tzinfo=None) - \
            self.created.replace(tzinfo=None)
        return age > expiration_delta

    def send_confirmation_link(self, request, template_context=None,
                               template_path=None):
        """
        Send out a message containing a link to activate the given address.

        The following settings are recognized:

            >>> EMAIL_CONFIRMATION_TEMPLATE = \
                    'postorius/user/address_confirmation_message.txt'
            >>> EMAIL_CONFIRMATION_FROM = 'postmaster@list.org'
            >>> EMAIL_CONFIRMATION_SUBJECT = 'Confirmation needed'

        :param request: The HTTP request object.
        :type request: HTTPRequest
        :param template_context: The context used when rendering the template.
            Falls back to host url and activation link.
        :type template_context: django.template.Context
        """
        # Get the url string from url conf.
        url = reverse('address_activation_link',
                      kwargs={'activation_key': self.activation_key})
        activation_link = request.build_absolute_uri(url)
        # Detect the right template path, either from the param,
        # the setting or the default
        if not template_path:
            template_path = getattr(
                settings, 'EMAIL_CONFIRMATION_TEMPLATE',
                'postorius/user/address_confirmation_message.txt')
        # Create a template context (if there is none) containing
        # the activation_link and the host_url.
        if not template_context:
            template_context = {'activation_link': activation_link,
                                'host_url': request.build_absolute_uri("/")}
        email_subject = getattr(
            settings, 'EMAIL_CONFIRMATION_SUBJECT', u'Confirmation needed')
        try:
            sender_address = getattr(settings, 'EMAIL_CONFIRMATION_FROM')
        except AttributeError:
            # settings.EMAIL_CONFIRMATION_FROM is not defined, fallback
            # settings.DEFAULT_EMAIL_FROM as mentioned in the django
            # docs. If that also fails, raise a `ImproperlyConfigured` Error.
            try:
                sender_address = getattr(settings, 'DEFAULT_FROM_EMAIL')
            except AttributeError:
                raise ImproperlyConfigured

        send_mail(email_subject,
                  render_to_string(template_path, template_context),
                  sender_address,
                  [self.email])
