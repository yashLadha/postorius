# -*- coding: utf-8 -*-
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
from operator import itemgetter
from urllib import urlencode
from urllib2 import HTTPError


def check_http_method(cls):
    class MockedHttp:
        def __init__(self, path, data, method):
            if method.upper() == 'PUT':
                return 200
            elif method.upper() == 'PATCH':
                return 200
            else:
                return _http_request(self, path, data, method)

def add_mock_data(cls):
    class _MockedList:
        def __init__(self, *args):
            self.mocked = cls(*args)
            self.mocked.info['id'] = 9
            self.mocked.info['list_name'] = 'List name lorem ipsum dolor sit'
            self.mocked.info['host_name'] = 'Host name lorem ipsum dolor sit'
            self.mocked.info['list_id'] = 'Some list ID lorem ipsum dolor sit'
            self.mocked.info['include_list_post_header'] = True
            self.mocked.info['include_rfc2369_headers'] = True
            self.mocked.info['autorespond_owner'] = 9
            self.mocked.info['autoresponse_owner_text'] = 'Auto response owner text lorem ipsum dolor sit'
            self.mocked.info['autorespond_postings'] = 9
            self.mocked.info['autoresponse_postings_text'] = 'Auto response postings text lorem ipsum dolor sit'
            self.mocked.info['autorespond_requests'] = 9
            self.mocked.info['autoresponse_request_text'] = 'Auto response request text lorem ipsum dolor sit'
            self.mocked.info['autoresponse_grace_period'] = 'Auto response grace period lorem ipsum dolor sit'
            self.mocked.info['ban_list'] = 'Ban list (BLOB format) lorem ipsum dolor sit'
            self.mocked.info['bounce_info_stale_after'] = 'Bounce info stale after lorem ipsum dolor sit'
            self.mocked.info['bounce_matching_headers'] = 'Bounce matching headers lorem ipsum dolor sit'
            self.mocked.info['bounce_notify_owner_on_disable'] = True
            self.mocked.info['bounce_notify_owner_on_removal'] = True
            self.mocked.info['bounce_processing'] = True
            self.mocked.info['bounce_score_threshold'] = 9
            self.mocked.info['bounce_unrecognized_goes_to_list_owner'] = True
            self.mocked.info['bounce_you_are_disabled_warnings'] = 9
            self.mocked.info['bounce_you_are_disabled_warnings_interval'] = 'Bounce you are disabled warnings lorem ipsum dolor sit'
            self.mocked.info['filter_content'] = True
            self.mocked.info['collapse_alternatives'] = True
            self.mocked.info['convert_html_to_plaintext'] = True
            self.mocked.info['default_member_moderation'] = True
            self.mocked.info['description'] = 'Description lorem ipsum dolor sit'
            self.mocked.info['digest_footer'] = 'Digest footer lorem ipsum dolor sit'
            self.mocked.info['digest_header'] = 'Digest header lorem ipsum dolor sit'
            self.mocked.info['digest_is_default'] = True
            self.mocked.info['digest_send_periodic'] = True
            self.mocked.info['digest_size_threshold'] = 9
            self.mocked.info['digest_volume_frequency'] = 'Digest volume frequency lorem ipsum dolor sit'
            self.mocked.info['digestable'] = True
            self.mocked.info['discard_these_nonmembers'] = 'Discard these non members (BLOB format) lorem ipsum dolor sit'
            self.mocked.info['emergency'] = True
            self.mocked.info['encode_ascii_prefixes'] = True
            self.mocked.info['first_strip_reply_to'] = True
            self.mocked.info['forward_auto_discards'] = True
            self.mocked.info['gateway_to_mail'] = True
            self.mocked.info['gateway_to_news'] = True
            self.mocked.info['generic_nonmember_action'] = 9
            self.mocked.info['goodbye_msg'] = 'Goodbye message lorem ipsum dolor sit'
            self.mocked.info['header_matches'] = 'Header matches (BLOB format) lorem ipsum dolor sit'
            self.mocked.info['hold_these_nonmembers'] = 'Hold these non members (BLOB format) lorem ipsum dolor sit'
            self.mocked.info['info'] = 'Info lorem ipsum dolor sit'
            self.mocked.info['linked_newsgroup'] = 'Linked newsgroup lorem ipsum dolor sit'
            self.mocked.info['max_days_to_hold'] = 9
            self.mocked.info['max_message_size'] = 9
            self.mocked.info['max_num_recipients'] = 9
            self.mocked.info['member_moderation_action'] = True
            self.mocked.info['member_moderation_notice'] = 'Member moderation notice lorem ipsum dolor sit'
            self.mocked.info['mime_is_default_digest'] = True
            self.mocked.info['moderator_password'] = 'Moderator password lorem ipsum dolor sit'
            self.mocked.info['msg_footer'] = 'Message footer lorem ipsum dolor sit'
            self.mocked.info['msg_header'] = 'Message header lorem ipsum dolor sit'
            self.mocked.info['new_member_options'] = 9
            self.mocked.info['news_moderation'] = 'News moderation lorem ipsum dolor sit'
            self.mocked.info['news_prefix_subject_too'] = True
            self.mocked.info['nntp_host'] = 'Nntp host lorem ipsum dolor sit'
            self.mocked.info['nondigestable'] = True
            self.mocked.info['nonmember_rejection_notice'] = 'Non member rejection notice lorem ipsum dolor sit'
            self.mocked.info['obscure_addresses'] = True
            self.mocked.info['personalize'] = 'Personalize lorem ipsum dolor sit'
            self.mocked.info['pipeline'] = 'Pipeline lorem ipsum dolor sit'
            self.mocked.info['post_id'] = 9
            self.mocked.info['preferred_language'] = 'Preferred language lorem ipsum dolor sit'
            self.mocked.info['private_roster'] = True
            self.mocked.info['real_name'] = 'Real name lorem ipsum dolor sit'
            self.mocked.info['reject_these_nonmembers'] = 'Reject these non members (BLOB format) lorem ipsum dolor sit'
            self.mocked.info['reply_goes_to_list'] = 'Reply goes to list lorem ipsum dolor sit'
            self.mocked.info['reply_to_address'] = 'Reply to address lorem ipsum dolor sit'
            self.mocked.info['require_explicit_destination'] = True
            self.mocked.info['respond_to_post_requests'] = True
            self.mocked.info['scrub_nondigest'] = True
            self.mocked.info['send_goodbye_msg'] = True
            self.mocked.info['send_reminders'] = True
            self.mocked.info['send_welcome_msg'] = True
            self.mocked.info['start_chain'] = 'Start chain lorem ipsum dolor sit'
            self.mocked.info['subject_prefix'] = 'Subject prefix lorem ipsum dolor sit'
            self.mocked.info['subscribe_auto_approval'] = 'Subscribe auto approval (BLOB format) lorem ipsum dolor sit'
            self.mocked.info['subscribe_policy'] = 9
            self.mocked.info['topics'] = 'Topics (BLOB format) lorem ipsum dolor sit'
            self.mocked.info['topics_bodylines_limit'] = 9
            self.mocked.info['topics_enabled'] = True
            self.mocked.info['unsubscribe_policy'] = 9
            self.mocked.info['welcome_msg'] = 'Welcome message lorem ipsum dolor sit'

        def __getattr__(self, name):
            return getattr(self.mocked, name)
    return _MockedList



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

    @check_http_method
    def _http_request(self, path, data=None, method=None):
        """Send an HTTP request.
        
        :param path: the path to send the request to
        :type path: string
        :param data: POST oder PUT data to send
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
            data = urlencode(data)
        if method is None:
            if data is None:
                method = 'GET'
            else:
                method = 'POST'
        method = method.upper()
        if method == 'POST':
            headers['Content-type'] = "application/x-www-form-urlencoded"
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

@add_mock_data
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
    
