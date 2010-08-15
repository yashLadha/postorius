# -*- coding: utf-8 -*-
# Copyright (C) 1998-2010 by the Free Software Foundation, Inc.
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

def check_http_method(fn):
    """
    Decorator function to return a mock response if the requested 
    method was PUT or PATCH. Will be removed once this functionality 
    is implemented in the REST server.
    """
    def http_req(*args, **kwargs):
        if 'method' in kwargs:
            # If one of the not implemented methods gets called, return
            # a response saying everything went well (204).
            if kwargs['method'].upper() == 'PUT':
                return 204
            elif kwargs['method'].upper() == 'PATCH':
                return 204
        else:
            # otherwise we return the function to let it perform its 
            # usual job
            return fn(*args, **kwargs)
    return http_req


def add_list_mock_data(cls):
    """
    Decorator function to add mock data from the database to a list.
    Once the functionality exists in the REST server this function can 
    be removed.
    """
    cls.__orig__init__ = cls.__init__
    def __init__(self, *args, **kwargs):
        """
        Initiate the list with the missing information and call the 
        usual init function to get the real data already available.
        """
        cls.__orig__init__(self, *args, **kwargs)
        self.info['id'] = 9
        #self.info['list_name'] = 'List name lorem ipsum dolor sit'
        #self.info['host_name'] = 'Host name lorem ipsum dolor sit'
        self.info['list_id'] = 'Some list ID lorem ipsum dolor sit'
        self.info['include_list_post_header'] = True
        self.info['include_rfc2369_headers'] = True
        self.info['autorespond_owner'] = 9
        self.info['autoresponse_owner_text'] = 'Auto response owner text lorem ipsum dolor sit'
        self.info['autorespond_postings'] = 9
        self.info['autoresponse_postings_text'] = 'Auto response postings text lorem ipsum dolor sit'
        self.info['autorespond_requests'] = 9
        self.info['autoresponse_request_text'] = 'Auto response request text lorem ipsum dolor sit'
        self.info['autoresponse_grace_period'] = 'Auto response grace period lorem ipsum dolor sit'
        self.info['ban_list'] = 'Ban list (BLOB format) lorem ipsum dolor sit'
        self.info['bounce_info_stale_after'] = 'Bounce info stale after lorem ipsum dolor sit'
        self.info['bounce_matching_headers'] = 'Bounce matching headers lorem ipsum dolor sit'
        self.info['bounce_notify_owner_on_disable'] = True
        self.info['bounce_notify_owner_on_removal'] = True
        self.info['bounce_processing'] = True
        self.info['bounce_score_threshold'] = 9
        self.info['bounce_unrecognized_goes_to_list_owner'] = True
        self.info['bounce_you_are_disabled_warnings'] = 9
        self.info['bounce_you_are_disabled_warnings_interval'] = 'Bounce you are disabled warnings lorem ipsum dolor sit'
        self.info['filter_content'] = True
        self.info['collapse_alternatives'] = True
        self.info['convert_html_to_plaintext'] = True
        self.info['default_member_moderation'] = True
        self.info['description'] = 'Description lorem ipsum dolor sit'
        self.info['digest_footer'] = 'Digest footer lorem ipsum dolor sit'
        self.info['digest_header'] = 'Digest header lorem ipsum dolor sit'
        self.info['digest_is_default'] = True
        self.info['digest_send_periodic'] = True
        self.info['digest_size_threshold'] = 9
        self.info['digest_volume_frequency'] = 'Digest volume frequency lorem ipsum dolor sit'
        self.info['digestable'] = True
        self.info['discard_these_nonmembers'] = 'Discard these non members (BLOB format) lorem ipsum dolor sit'
        self.info['emergency'] = True
        self.info['encode_ascii_prefixes'] = True
        self.info['first_strip_reply_to'] = True
        self.info['forward_auto_discards'] = True
        self.info['gateway_to_mail'] = True
        self.info['gateway_to_news'] = True
        self.info['generic_nonmember_action'] = 9
        self.info['goodbye_msg'] = 'Goodbye message lorem ipsum dolor sit'
        self.info['header_matches'] = 'Header matches (BLOB format) lorem ipsum dolor sit'
        self.info['hold_these_nonmembers'] = 'Hold these non members (BLOB format) lorem ipsum dolor sit'
        self.info['info'] = 'Info lorem ipsum dolor sit'
        self.info['linked_newsgroup'] = 'Linked newsgroup lorem ipsum dolor sit'
        self.info['max_days_to_hold'] = 9
        self.info['max_message_size'] = 9
        self.info['max_num_recipients'] = 9
        self.info['member_moderation_action'] = True
        self.info['member_moderation_notice'] = 'Member moderation notice lorem ipsum dolor sit'
        self.info['mime_is_default_digest'] = True
        self.info['moderator_password'] = 'Moderator password lorem ipsum dolor sit'
        self.info['msg_footer'] = 'Message footer lorem ipsum dolor sit'
        self.info['msg_header'] = 'Message header lorem ipsum dolor sit'
        self.info['new_member_options'] = 9
        self.info['news_moderation'] = 'News moderation lorem ipsum dolor sit'
        self.info['news_prefix_subject_too'] = True
        self.info['nntp_host'] = 'Nntp host lorem ipsum dolor sit'
        self.info['nondigestable'] = True
        self.info['nonmember_rejection_notice'] = 'Non member rejection notice lorem ipsum dolor sit'
        self.info['obscure_addresses'] = True
        self.info['personalize'] = 'Personalize lorem ipsum dolor sit'
        self.info['pipeline'] = 'Pipeline lorem ipsum dolor sit'
        self.info['post_id'] = 9
        self.info['preferred_language'] = 'Preferred language lorem ipsum dolor sit'
        self.info['private_roster'] = True
        #self.info['real_name'] = 'Real name lorem ipsum dolor sit'
        self.info['reject_these_nonmembers'] = 'Reject these non members (BLOB format) lorem ipsum dolor sit'
        self.info['reply_goes_to_list'] = 'Reply goes to list lorem ipsum dolor sit'
        self.info['reply_to_address'] = 'some_reply_to_address@lorem.ipsum'
        self.info['require_explicit_destination'] = True
        self.info['respond_to_post_requests'] = True
        self.info['scrub_nondigest'] = True
        self.info['send_goodbye_msg'] = True
        self.info['send_reminders'] = True
        self.info['send_welcome_msg'] = True
        self.info['start_chain'] = 'Start chain lorem ipsum dolor sit'
        self.info['subject_prefix'] = 'Subject prefix lorem ipsum dolor sit'
        self.info['subscribe_auto_approval'] = 'Subscribe auto approval (BLOB format) lorem ipsum dolor sit'
        self.info['subscribe_policy'] = 9
        self.info['topics'] = 'Topics (BLOB format) lorem ipsum dolor sit'
        self.info['topics_bodylines_limit'] = 9
        self.info['topics_enabled'] = True
        self.info['unsubscribe_policy'] = 9
        self.info['welcome_msg'] = 'Welcome message lorem ipsum dolor sit'
        self.info['advertised'] = True
        self.info['archive'] = True
        self.info['archive_private'] = True
    cls.__init__ = __init__

    return cls


def add_user_mock_data(cls):
    """Decorator function to add mock data to a user object."""

    cls.__orig__init__ = cls.__init__
    def __init__(self, *args, **kwargs):
        """Initiate a user and add mockdata."""
        cls.__orig__init__(self, *args, **kwargs)
        self.info[u'real_name'] = u'Jack'

    def get_lists(self):
        response = [{u'email_address': u'jack@example.com',
                     u'fqdn_listname': u'test-one@example.com',
                     u'real_name': u'Test-one'},
                    {u'email_address': u'jack@example.com',
                     u'fqdn_listname': u'test-two@example.com',
                     u'real_name': u'Test-two'}]
        return response

    def get_email_addresses(self):
        response = [u'jack@example.com']
        return response

    cls.__init__ = __init__
    cls.get_lists = get_lists
    cls.get_email_addresses = get_email_addresses

    return cls


def add_member_mock_data(cls):
    """
    Decorator function to add mock data from the database to a member.
    Once the functionality exists in the REST server this function can 
    be removed.
    """
    cls.__orig__init__ = cls.__init__
    def __init__(self, *args, **kwargs):
        """
        Initiate the member with the missing information and call the 
        usual init function to get the real data already available.
        """
        cls.__orig__init__(self, *args, **kwargs)
        self.info['id'] = 9
        self.info['acknowledge_posts'] = True
        self.info['hide_address'] = True
        self.info['preferred_language'] = 'Preferred language lorem ipsum dolor sit'
        self.info['receive_list_copy'] = True
        self.info['receive_own_postings'] = True
        #self.info['delivery_mode'] = 'Delivery mode lorem ipsum dolor sit'
        #self.info['delivery_status'] = 'Delivery status lorem ipsum dolor sit'
        self.info['real_name'] = 'Real name lorem ipsum dolor sit'
        self.info['password'] = 'Password lorem ipsum dolor sit'
        self.info['preferences_id'] = 9
        self.info['role'] = 'Role lorem ipsum dolor sit'
        self.info['mailing_list'] = 'Mailing list lorem ipsum dolor sit'
        self.info['is_moderated'] = True
        self.info['address_id'] = 9
        self.info['address'] = 'Address lorem ipsum dolor sit'
        self.info['_original'] = 'Original lorem ipsum dolor sit'
        self.info['verified_on'] = '2000-01-01 00:00:00'
        self.info['registered_on'] = '2000-01-01 00:00:00'
        self.info['user_id'] = 9
    cls.__init__ = __init__

    return cls
