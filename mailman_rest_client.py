# -*- coding: utf-8 -*-
import json
from httplib import HTTPConnection, HTTPException
from urllib import urlencode

class MailmanRESTClientError(Exception):
    """An exception thrown by the Mailman REST API client."""
    pass

class MailmanRESTClient(object):
    """A thin client wrapper for the Mailman REST API."""

    def __init__(self, host):
        self.host = host
        if self.host[-1] == '/':
            self.host = self.host[:-1]

        # general header information
        self.headers = {
            "User-Agent": "MailmanRESTClient",
            "Accept": "text/plain", 
        }

        try:
            self.c = HTTPConnection(self.host)
        except:
            raise MailmanRESTClientError('Could not connect to server')

    def __repr__(self):
        return '<MailmanRESTClient: %s>' % self.host

    def _get_url(self, path):
        try:
            self.c.request('GET', path, None, self.headers)
        except:
            raise MailmanRESTClientError('Error sending request')
        
        try:
            r = self.c.getresponse()
            raw_data = r.read()
            if len(raw_data) == 0:
                raise None
            data = json.loads(raw_data)
        except:
			raise MailmanRESTClientError('Error sending request')
        finally:
            self.c.close()
        
        return data

    def _post_url(self, path, data):
        self.headers['Content-type'] = "application/x-www-form-urlencoded"
        try:
            self.c.request('POST', path, urlencode(data), self.headers)
        except:
            raise MailmanRESTClientError('Could not send request')
            
        try:
            r = self.c.getresponse()
            if r.status == 201:
                return True
            else:
                return r.status
        finally:
            self.c.close()

    def _delete_url(self, path):
        try:
            self.c.request('DELETE', path, None, self.headers)
        except:
            raise MailmanRESTClientError('Could not send request')
        
    def _put_url(self, path):
        pass
        
    def get_lists(self):
        """Get a list of mail lists.

        returns a list of dicts
        """
        try:
            r = self._get_url('/3.0/lists')
        except:
            raise MailmanRESTClientError('Could not send request')
        
        if 'entries' not in r:
            raise MailmanRESTClientError('No mailing lists found')

        return r['entries']

    def read_list(self, list_name):
        """Get information about list.

        :param list_name: name of the list to get information about
        :type list_name: string
        :rtype: dict
        """
        try:
            r = self._get_url('/3.0/lists/' + list_name)
        except:
            raise MailmanRESTClientError('Unable to get info about list')

        return r

    def create_list(self, fqdn_listname, **kwargs):
        """Create a new list.

        :param fqdn_listname: the name of the list including the @ and the domain name.  eg.  test@example.com
        :type fqdn_listname: string
        :rtype: None
        """
        data = {
                'fqdn_listname': fqdn_listname
        }
        data.update(**kwargs)
        try:
            return self._post_url('/3.0/lists', data)
        except MailmanRESTClientError, e:
            raise MailmanRESTClientError(e)
            

    def subscribe_list(self, fqdn_listname, address, real_name, **kwargs):
        """Add an address to a list.

        :param fqdn_listname: the name of the list .
        :type fqdn_listname: string
        :param address: email address to add to the list.
        :type address: string
        :param real_name: the "real" name for the address to be addded
        :type real_name: string
        """

        data = {
                'fqdn_listname': fqdn_listname,
                'address': address,
                'real_name': real_name
        }
        data.update(**kwargs)
        try:
            r = self._post_url('/3.0/members', data)
        except:
            raise MailmanRESTClientError('unable to join list')

        return r

    def leave_list(self, fqdn_listname, address):
        """Remove an address from a list.

        :param fqdn_listname: the name of the list.
        :type fqdn_listname: string
        :param address: email address that is leaving the list
        :type address: string
        :rtype: None
        """
        try:
            r = self._delete_url('/3.0/lists/' + fqdn_listname + '/member/' + address )
        except:
            raise MailmanRESTClientError('unable to leave list')

        return True

    def get_members(self, fqdn_listname = None):
        """Get a list of all members for all lists.

        :rtype: list of dicts
        :type fqdn_listname: string
        """

        if fqdn_listname != None:
            url = '/3.0/lists/' + fqdn_listname + '/members'
        else:
            url = '/3.0/members'
        try:
            r = self._get_url(url)
        except:
            raise MailmanRESTClientError('Could not complete request')

        if 'entries' not in r:
            raise MailmanRESTClientError('Could not find any members')

        return r['entries']

    def get_domains(self):
        """Get a list of domains.

        :rtype: list of dicts
        """
        try:
            r = self._get_url('/3.0/domains')
        except:
            raise MailmanRESTClientError('Could not complete request')
        if 'entries' not in r:
            raise MailmanRESTClientError('Could not find any domains')

        return r['entries']

    def read_domain(self, domain_name):
        """Get information about a specific domain.

        :param domain_name: the name of the domain.
        :rtype: dict
        """
        
        try:
            r = self._get_url('/3.0/domains/' + domain_name)
        except:
            raise MailmanRESTClientError('Unable to read domain')

        return r

    def create_domain(self, email_host, **kwargs):
        """Create a new domain name.

        :param email_host: domain name to create
        :type email_host: string
        :rtype: None
        """
        data = {
            'email_host': email_host,
        }
        data.update(**kwargs)
        try:
            r = self._post_url('/3.0/domains', data)
        except:
            raise MailmanRESTClientError('Unable to create domain')

        return r

