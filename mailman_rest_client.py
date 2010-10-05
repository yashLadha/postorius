# Copyright (C) 2010 by the Free Software Foundation, Inc.
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

"""A client library for the Mailman REST API."""


from __future__ import absolute_import, unicode_literals

__metaclass__ = type
__all__ = [
    'MailmanRESTClient',
    'MailmanRESTClientError',
    ]


import re
import json

from httplib2 import Http
from mailman_django import mockdata
from operator import itemgetter
from urllib import urlencode
from urllib2 import HTTPError


class MailmanRESTClientError(Exception):
    """An exception thrown by the Mailman REST API client."""


class MailmanRESTClient():
    """A wrapper for the Mailman REST API."""
    
    def __init__(self, host):
        """Check and modify the host name.

        :param host: the host name of the REST API 
        :type host: string
        :return: a MailmanRESTClient object
        :rtype: objectFirst line should
        """
        self.host = host
        # If there is a trailing slash remove it
        if self.host[-1] == '/':
            self.host = self.host[:-1]
        # If there is no protocol, fall back to http://
        if self.host[0:4] != 'http':
            self.host = 'http://' + self.host

    def __repr__(self):
        return '<MailmanRESTClient: %s>' % self.host

    def _http_request(self, path, data=None, method=None):
        """Send an HTTP request.
        
        :param path: the path to send the request to
        :type path: string
        :param data: POST or PUT data to send
        :type data: dict
        :param method: the HTTP method; defaults to GET or POST (if
            data is not None)
        :type method: string
        :return: the request content or a status code, depending on the
            method and if the request was successful
        :rtype: int, list or dict
        """
        url = self.host + path
        # Include general header information
        headers = {
            'User-Agent': 'MailmanRESTClient',
            'Accept': 'text/plain', 
            }
        if data is not None:
            data = urlencode(data, doseq=True)
            headers['Content-type'] = "application/x-www-form-urlencoded"
        if method is None:
            if data is None:
                method = 'GET'
            else:
                method = 'POST'
        method = method.upper()
        response, content = Http().request(url, method, data, headers)
        if method == 'GET':
            if response.status // 100 != 2:
                return response.status
            else:
                return json.loads(content)
        else:
            return response.status

    def create_domain(self, email_host):
        """Create a domain and return a domain object.
        
        :param email_host: The host domain to create
        :type email_host: string
        :return: A domain object or a status code (if the create
            request failed)
        :rtype int or object
        """
        data = {
            'email_host': email_host,
            }
        response = self._http_request('/3.0/domains', data, 'POST')
        if response == 201:
            return _Domain(self.host, email_host)
        else:
            return response

    def get_domain(self, email_host):
        """Return a domain object.
        
        :param email_host: host domain
        :type email_host: string
        :rtype object
        """
        return _Domain(self.host, email_host)

    def get_lists(self):
        """Get a list of all mailing list.

        :return: a list of dicts with all mailing lists
        :rtype: list
        """
        response = self._http_request('/3.0/lists')
        if 'entries' not in response:
            return []
        else:
            # Return a dict with entries sorted by fqdn_listname
            return sorted(response['entries'],
                key=itemgetter('fqdn_listname'))

    def get_list(self, fqdn_listname):
        """Find and return a list object.

        :param fqdn_listname: the mailing list address
        :type fqdn_listname: string
        :rtype: object
        """
        return _List(self.host, fqdn_listname)

    def get_members(self):
        """Get a list of all list members.

        :return: a list of dicts with the members of all lists
        :rtype: list
        """
        response = self._http_request('/3.0/members')
        if 'entries' not in response:
            return []
        else:
            return sorted(response['entries'],
                key=itemgetter('self_link'))


class _Domain(MailmanRESTClient):
    """A domain wrapper for the MailmanRESTClient."""

    def __init__(self, host, email_host):
        """Connect to host and get list information.

        :param host: the host name of the REST API 
        :type host: string
        :param email_host: host domain
        :type email_host: string
        :rtype: object
        """
        super(_Domain, self).__init__(host)
        self.info = self._http_request('/3.0/domains/' + email_host)

    def create_list(self, list_name):
        """Create a mailing list and return a list object.
        
        :param list_name: the name of the list to be created
        :type list_name: string
        :rtype: object
        """
        fqdn_listname = list_name + '@' + self.info['email_host']
        data = {
            'fqdn_listname': fqdn_listname
            }
        response = self._http_request('/3.0/lists', data, 'POST')
        return _List(self.host, fqdn_listname)

    def delete_list(self, list_name):
        fqdn_listname = list_name + '@' + self.info['email_host']
        return self._http_request('/3.0/lists/' + fqdn_listname, None, 'DELETE')

@mockdata.add_list_mock_data
class _List(MailmanRESTClient):
    """A mailing list wrapper for the MailmanRESTClient."""

    def __init__(self, host, fqdn_listname):
        """Connect to host and get list information.

        :param host: the host name of the REST API 
        :type host: string
        :param fqdn_listname: the mailing list address
        :type fqdn_listname: string
        :rtype: object
        """
        super(_List, self).__init__(host)
        self.info = self._http_request('/3.0/lists/' + fqdn_listname)
        self.config = self._http_request('/3.0/lists/%s/config' % fqdn_listname)

    def subscribe(self, address, real_name=None):
        """Add an address to a list.

        :param address: email address to add to the list.
        :type address: string
        :param real_name: the real name of the new member
        :type real_name: string
        """
        data = {
            'fqdn_listname': self.info['fqdn_listname'],
            'address': address,
            'real_name': real_name
            }
        return self._http_request('/3.0/members', data, 'POST')

    def unsubscribe(self, address):
        """Unsubscribe an address to a list.

        :param address: email address to add to the list.
        :type address: string
        :param real_name: the real name of the new member
        :type real_name: string
        """
        return self._http_request('/3.0/lists/' +
                             self.info['fqdn_listname'] +
                             '/member/' +
                             address,
                             None, 
                             'DELETE')

    def get_members(self):
        """Get a list of all list members.

        :return: a list of dicts with all members
        :rtype: list
        """
        response = self._http_request('/3.0/lists/' +
                                 self.info['fqdn_listname'] +
                                 '/roster/members')
        if 'entries' not in response:
            return []
        else:
            return sorted(response['entries'],
                key=itemgetter('self_link'))
    
    def update_config(self, data):
        """Update the list configuration.

        :param data: A dict with the config attributes to be updated.
        :type data: dict
        :return: the return code of the http request
        :rtype: integer
        """
        url = '/3.0/lists/%s/config' % self.info['fqdn_listname']
        status = self._http_request(url, data, 'PATCH')
        if status == 200:
            for key in data:
                self.config[key] = data[key]
        return status
