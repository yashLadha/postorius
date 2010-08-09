# -*- coding: utf-8 -*-
"""
Test suite for the Mailman UI.
This document both acts as a test for all the functions implemented 
in the UI as well as documenting what has been done.

# To start the test, import the django test client.
>>> from django.test.client import Client

# Then instantiate a test client.
>>> c = Client()

# Go to the start page listing all lists.
>>> response = c.get('/mailman_django/',)

# Make sure the load was a success by checking the status code.
>>> response.status_code
200

# Try to create a new list. Accessing the page to create a new list 
# redirects to a login page since we need admin authority to create 
# a new list.
>>> response = c.get('/mailman_django/lists/new/')

# Check that login required was in the HTML content of what was loaded
>>> print "Login Required" in response.content
True

# Hence, we log in as an admin on the login page we get as a response 
# to our call.
>>> response = c.post('/mailman_django/lists/new/',
...                   {"address": "kevin@example.com",
...                   "password": "kevin"})

# Check the content to see that we came to the create page after 
# logging in.
>>> print "Create a new list" in response.content
True

# Now create a new list called 'new_list'.
>>> response = c.post('/mailman_django/lists/new/',
...                   {"listname": "new_list@example.com",
...                    "list_owner": "kevin@example.com",
...                    "list_type": "closed_discussion",
...                    "languages": "English (USA)"})

# We should now end up on a success page offering what to do next. 
# Let's check that this was the case.
>>> print "What would you like to do next?" in response.content
True

# Three options appear on this page. The first one is to mass subscribe
# users, the second is to go to the settings page of the list just 
# created and the third is to create another list. 
# We're still logged in so go to the page where the settings can be 
# changed (this page also requires admin authority).
>>> response = c.get('/mailman_django/settings/new_list%40example.com/',)

# Try to update the settings. Here we must provide all the settings 
# on the page to be allowed to update it.
>>> response = c.post('/mailman_django/settings/new_list%40example.com/',
...                   {'send_welcome_msg': True,
...                    'advertised': True,
...                    u'list_name': u'new_list',
...                    'unsubscribe_policy': 9,
...                    'autorespond_owner': 9,
...                    'default_member_moderation': True,
...                    'scrub_nondigest': True,
...                    'subscribe_auto_approval': 'Subscribe auto approval lorem ipsum dolor sit',
...                    u'fqdn_listname': u'new_list@example.com',
...                    'gateway_to_news': True,
...                    'encode_ascii_prefixes': True,
...                    'generic_nonmember_action': 9,
...                    'autoresponse_grace_period': 'Auto response grace period lorem ipsum dolor sit',
...                    'autoresponse_owner_text': 'Auto response owner text lorem ipsum dolor sit',
...                    'digest_is_default': True,
...                    'bounce_info_stale_after': 'Bounce info stale after lorem ipsum dolor sit',
...                    'welcome_msg': 'Welcome message lorem ipsum dolor sit',
...                    'topics_enabled': True,
...                    'digest_size_threshold': 9,
...                    'header_matches': 'Header matches lorem ipsum dolor sit',
...                    u'real_name': u'New_list',
...                    u'host_name': u'example.com',
...                    'reject_these_nonmembers': 'Reject these non members lorem ipsum dolor sit',
...                    'collapse_alternatives': True,
...                    'linked_newsgroup': 'Linked newsgroup lorem ipsum dolor sit',
...                    'send_reminders': True,
...                    'hold_these_nonmembers': 'Hold these non members lorem ipsum dolor sit',
...                    'digest_header': 'Digest header lorem ipsum dolor sit',
...                    'archive_private': True,
...                    'bounce_matching_headers': 'Bounce matching headers lorem ipsum dolor sit',
...                    'bounce_score_threshold': 9,
...                    'nondigestable': True,
...                    u'http_etag': u'"008c561be0aeaf134fea95066e5a7509a79e4842"',
...                    'bounce_notify_owner_on_removal': True,
...                    'autoresponse_request_text': 'Auto response request text lorem ipsum dolor sit',
...                    'personalize': 'Personalize lorem ipsum dolor sit',
...                    'max_num_recipients': 9,
...                    'post_id': 9,
...                    'send_goodbye_msg': True,
...                    'max_days_to_hold': 9,
...                    'pipeline': 'Pipeline lorem ipsum dolor sit',
...                    'start_chain': 'Start chain lorem ipsum dolor sit',
...                    'preferred_language': 'Preferred language lorem ipsum dolor sit',
...                    'autorespond_requests': 9,
...                    'msg_header': 'Message header lorem ipsum dolor sit',
...                    'max_message_size': 9,
...                    'bounce_you_are_disabled_warnings': 9,
...                    'private_roster': True,
...                    'require_explicit_destination': True,
...                    'gateway_to_mail': True,
...                    'digest_send_periodic': True,
...                    'digestable': True,
...                    'member_moderation_notice': 'Member moderation notice lorem ipsum dolor sit',
...                    'bounce_you_are_disabled_warnings_interval': 'Bounce you are disabled warnings lorem ipsum dolor sit',
...                    u'self_link': u'http://localhost:8001/3.0/lists/new_list@example.com',
...                    'digest_footer': 'Digest footer lorem ipsum dolor sit',
...                    'discard_these_nonmembers': 'Discard these non members lorem ipsum dolor sit',
...                    'respond_to_post_requests': True,
...                    'mime_is_default_digest': True,
...                    'subject_prefix': 'Subject prefix lorem ipsum dolor sit',
...                    'convert_html_to_plaintext': True,
...                    'autorespond_postings': 9,
...                    'msg_footer': 'Message footer lorem ipsum dolor sit',
...                    'info': 'Info lorem ipsum dolor sit',
...                    'reply_goes_to_list': 'Reply goes to list lorem ipsum dolor sit',
...                    'obscure_addresses': True,
...                    'include_list_post_header': True,
...                    'news_moderation': 'News moderation lorem ipsum dolor sit',
...                    'topics': 'Topics (BLOB format) lorem ipsum dolor sit',
...                    'bounce_notify_owner_on_disable': True,
...                    'goodbye_msg': 'Goodbye message lorem ipsum dolor sit',
...                    'topics_bodylines_limit': 9,
...                    'id': 9,
...                    'filter_content': True,
...                    'emergency': True,
...                    'member_moderation_action': True,
...                    'archive': True,
...                    'nonmember_rejection_notice': 'Non member rejection notice lorem ipsum dolor sit',
...                    'list_id': 'Some list ID lorem ipsum dolor sit',
...                    'first_strip_reply_to': True,
...                    'nntp_host': 'Nntp host lorem ipsum dolor sit',
...                    'news_prefix_subject_too': True,
...                    'bounce_processing': True,
...                    'description': 'Description lorem ipsum dolor sit',
...                    'reply_to_address': 'some_reply_to_address@lorem.ipsum',
...                    'moderator_password': 'Moderator password lorem ipsum dolor sit',
...                    'digest_volume_frequency': 'Digest volume frequency lorem ipsum dolor sit',
...                    'include_rfc2369_headers': True,
...                    'forward_auto_discards': True,
...                    'ban_list': 'Ban list lorem ipsum dolor sit',
...                    'new_member_options': 9,
...                    'subscribe_policy': 9,
...                    'bounce_unrecognized_goes_to_list_owner': True,
...                    'autoresponse_postings_text': 'Auto response postings text lorem ipsum dolor sit'})

# If the post was successful, a positive response should appear in 
# the HTML content.
>>> print "The list has been updated." in response.content
True

# Now we want to mass subscribe a few users to the list. Therefore, 
# go to the mass subscription page.
>>> url = '/mailman_django/settings/new_list%40example.com/mass_subscribe/'
>>> response = c.get(url)

# Check that everything went well by making sure the status code 
# was correct.
>>> response.status_code
200

# Try mass subscribing the users 'liza@example.com' and 
# 'george@example.com'. Each address should be provided on a separate 
# line so add '\\n' between the names to indicate that this was done 
# (we're on a Linux machine which is why the letter 'n' was used and 
# the double '\\' instead of a single one is to escape the string 
# parsing of Python).
>>> url = '/mailman_django/settings/new_list%40example.com/mass_subscribe/'
>>> response = c.post(url,
...                   {"emails": "liza@example.com\\ngeorge@example.com"})

# If everything was successful, we shall get a positive response from 
# the page. We'll check that this was the case.
>>> print "The mass subscription was successful." in response.content
True

# Done with the admin stuff. Now let's log out.
>>> response = c.get('/mailman_django/lists/logout/',)

# If the request was successful we should end up on the list info page.
# Now make sure that we got redirected there.
>>> print "All mailing lists" in response.content
True

# Apart from just viewing a list of all the available lists we can 
# view the information about one particular list on a list info page. 
# On this page we can also subscribe or unsubscribe an email address 
# to the list. Let's try to subscribe to the list in the "normal" way 
# (i.e. not using mass subscription). First we go to the page.
>>> response = c.get('/mailman_django/lists/new_list%40example.com/',)

# Then we check that everything went well.
>>> response.status_code
200

# And finally we try to subscribe a user named 'Meg'.
>>> response = c.post('/mailman_django/lists/new_list%40example.com/',
...                   {"email": "meg@example.com",
...                   "real_name": "Meg",
...                   "name": "subscribe",
...                   "listname": "new_list@example.com"})

# This page contains a redirect so we check the status code for this.
>>> response.status_code
302

# Then we check that the redirect gives the correct status code.
>>> response = c.get("http://testserver/mailman_django/lists/")
>>> response.status_code
200

# We'll now try unsubscribing the address we just subscribed.
>>> response = c.post('/mailman_django/lists/new_list%40example.com/',
...                   {"email": "meg@example.com",
...                   "real_name": "Meg",
...                   "name": "unsubscribe",
...                   "listname": "new_list@example.com"})

# If everything went well, we'll get a positive response saying so.
>>> print "You have now been unsubscribed from new_list@example.com." in \
 response.content
True

# Finally, let's delete the list.
# We start by checking that the list is really there (for reference).
>>> response = c.get('/mailman_django/lists/')
>>> print "new_list@example.com" in response.content
True

# Then we delete the list...
>>> response = c.post('/mailman_django/delete_list/new_list%40example.com/',)

# ...and check that it's been deleted.
>>> print "new_list@example.com" in response.content
False

# So far this is what you can do in the UI. More tests can be added 
# here later.
"""
