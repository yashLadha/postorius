# -*- coding: utf-8 -*-

def check_http_method(fn):
    """Decorator function to return a mock response if the requested method was
    PUT or PATCH.
    """
    def http_req(*kwargs):
        if 'method' in kwargs:
            if method.upper() == 'PUT':
                return 200
            elif method.upper() == 'PATCH':
                return 200
        else:
            return fn(*kwargs)

    return http_req


def add_mock_data(cls):
    """Decorator function to add mock data from the database to a list.
    """
    cls.__orig__init__ = cls.__init__
    def __init__(self, *args, **kwargs):
        cls.__orig__init__(self, *args, **kwargs)
        self.info['id'] = 9
        self.info['list_name'] = 'List name lorem ipsum dolor sit'
        self.info['host_name'] = 'Host name lorem ipsum dolor sit'
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
        self.info['real_name'] = 'Real name lorem ipsum dolor sit'
        self.info['reject_these_nonmembers'] = 'Reject these non members (BLOB format) lorem ipsum dolor sit'
        self.info['reply_goes_to_list'] = 'Reply goes to list lorem ipsum dolor sit'
        self.info['reply_to_address'] = 'Reply to address lorem ipsum dolor sit'
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
    cls.__init__ = __init__

    return cls

