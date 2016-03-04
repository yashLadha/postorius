# -*- coding: utf-8 -*-
# Copyright (C) 2012-2016 by the Free Software Foundation, Inc.
#
# This file is part of Postorius.
#
# Postorius is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
# Postorius is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# Postorius.  If not, see <http://www.gnu.org/licenses/>.

import logging

from django import VERSION as DJANGO_VERSION
from django.conf import settings
from django.contrib import messages
from django.core.urlresolvers import reverse
from django.test import RequestFactory, TestCase
from mock import patch, MagicMock
from six.moves.urllib_parse import quote

from postorius.utils import get_client
from postorius.tests import MM_VCR


vcr_log = logging.getLogger('vcr')
vcr_log.setLevel(logging.WARNING)


def create_mock_domain(properties=None):
    """Create and return a mocked Domain.

    :param properties: A dictionary of the domain's properties.
    :type properties: dict
    :return: A MagicMock object with the properties set.
    :rtype: MagicMock
    """
    mock_object = MagicMock(name='Domain')
    mock_object.base_url = ''
    mock_object.contact_address = ''
    mock_object.description = ''
    mock_object.mail_host = ''
    mock_object.url_host = ''
    mock_object.lists = []
    if properties is not None:
        for key in properties:
            setattr(mock_object, key, properties[key])
    return mock_object


def create_mock_list(properties=None):
    """Create and return a mocked List.

    :param properties: A dictionary of the list's properties.
    :type properties: dict
    :return: A MagicMock object with the properties set.
    :rtype: MagicMock
    """
    mock_object = MagicMock(name='List')
    mock_object.members = []
    mock_object.moderators = []
    mock_object.owners = []
    # like in mock_domain, some defaults need to be added...
    if properties is not None:
        for key in properties:
            setattr(mock_object, key, properties[key])
    return mock_object


def create_mock_member(properties=None):
    """Create and return a mocked Member.

    :param properties: A dictionary of the member's properties.
    :type properties: dict
    :return: A MagicMock object with the properties set.
    :rtype: MagicMock
    """
    mock_object = MagicMock(name='Member')
    # like in mock_domain, some defaults need to be added...
    if properties is not None:
        for key in properties:
            setattr(mock_object, key, properties[key])
    return mock_object


def get_flash_messages(response, empty=True):
    if "messages" not in response.cookies:
        return []
    # A RequestFactory will not run the messages middleware, and thus will
    # not delete the messages after retrieval.
    dummy_request = RequestFactory().get("/")
    dummy_request.COOKIES["messages"] = response.cookies["messages"].value
    msgs = list(messages.storage.cookie.CookieStorage(dummy_request))
    if empty:
        del response.client.cookies["messages"]
    return msgs
get_flash_messages.__test__ = False



class ViewTestCase(TestCase):

    use_vcr = True

    def setUp(self):
        self.mm_client = get_client()
        if self.use_vcr:
            cm = MM_VCR.use_cassette('.'.join([
                #self.__class__.__module__.rpartition('.')[2],
                self.__class__.__name__, self._testMethodName, 'yaml']))
            self.cassette = cm.__enter__()
            self.addCleanup(cm.__exit__, None, None, None)

    def assertHasSuccessMessage(self, response):
        msgs = get_flash_messages(response)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].level, messages.SUCCESS, msgs[0].message)
        return msgs[0].message

    def assertHasErrorMessage(self, response):
        msgs = get_flash_messages(response)
        self.assertEqual(len(msgs), 1)
        self.assertEqual(msgs[0].level, messages.ERROR, msgs[0].message)
        return msgs[0].message

    def assertHasNoMessage(self, response):
        msgs = get_flash_messages(response)
        self.assertEqual(len(msgs), 0)

    def assertRedirectsToLogin(self, url):
        response = self.client.get(url)
        self.assertRedirects(response,
            '{}?next={}'.format(reverse(settings.LOGIN_URL), quote(url)))

