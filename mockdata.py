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

def add_mock_data(fn):
    """Decorator function to add mock data from the database to a list.
    """
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
        return __init__(*args)

    def __getattr__(self, name):
        return getattr(self.mocked, name)
    return fn
