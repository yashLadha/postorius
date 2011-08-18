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

"""
==============================
Test suite for the Mailman UI.
==============================

This document both acts as a test for all the functions implemented
in the UI as well as documenting what has been done.

    >>> from setup import setup_mm, Testobject, teardown_mm
    >>> testobject = setup_mm(Testobject())

Import Translation Module to check success messages
    >>> from django.utils.translation import gettext as _


Getting Started
===============

To start the test, import the django test client.

    >>> from django.test.client import Client

Then instantiate a test client.

    >>> c = Client()

Go to the start page listing all lists.

    >>> response = c.get('/',)

Make sure the load was a success by checking the status code.

    >>> response.status_code
    200

Check that login is required for a couple of pages
==================================================
Try to access some of the admin Pages. Accessing these pages
redirects to a login page since we need admin authority to view and use them
#TODO - ACL tests will be implemented for each site at a central place at later stages of development.
Please be aware that this test only checks for authentification ONCE.

    >>> response = c.get('/domains/')

Check that Http Redirect to the login is returned #TODO check url

    >>> from django.http import HttpResponseRedirect
    >>> print type(response) == HttpResponseRedirect
    True

User + Login
============
For authentification we do need to setup a test user into the system.
This including the login will be with our own Auth Backend. Additional information on how to expand the Auth Backend with e.g. user perms could be found on a well documented Django Help page:
https://docs.djangoproject.com/en/dev/topics/auth/
    
    >>> #c.... adduser() #TODO add user

    Check our own login form, which should redirect the user to a usable page after every successful login
    Login was successful if we get a return object to either the list index or a specified url
    >>> response = c.post('/accounts/login/',
    ...                   {"user": "james@example.com",
    ...                   "password": "james"})
    >>> print type(response) == HttpResponseRedirect
    True
    
    Check user login directly via our own Auth Framework which will save the Login Cookie which is needed for further testing
    >>> c.login(username='katie@example.com', password='katie')
    True
    
Permissions
===========
Check that only James does have the permission to get the domains administration
#TODO - ACL is hardcoded in auth backend : permission domain_admin → == james@...
    
    >>> response = c.get('/domains/')
    >>> print type(response) == HttpResponseRedirect
    True
    
    >>> c.logout() #katie

    >>> c.login(username='james@example.com', password='james') #now Domains should work - see tests below
    True

Create a New Domain
===================
Check the content to see that we came to the create page after 
logging in.

    >>> response = c.get('/domains/')
    
Then we check that everything went well.
    >>> response.status_code
    200
    >>> print "Domain Index" in response.content #TODO - change heading
    True
    
Check the button which should allow creation of a new domains
    >>> '<li class="mm_new_domain"><a href="/domains/new/">New Domain</a></li>' in response.content
    True

Now go to the Domains creation page
    >>> response = c.get('/domains/new/')

Then we check that everything went well.

    >>> response.status_code
    200
    >>> print "Add a new Domain" in response.content #TODO - change heading
    True

    
and create a new Domain called 'mail.example.com'.    
Check that the new Domain exists in the list of existing domains which is above new_domain form
    >>> response = c.post('/domains/new/',
    ...                   {"mail_host": "mail.example.com",
    ...                    "web_host": "example.com",
    ...                    "description": "doctest testing domain"})  
    >>> response = c.get('/domains/')
        
Then we check that everything went well.
    >>> response.status_code
    200
    >>> print "doctest testing domain" in response.content
    True

Create a New List
=================

Try to access the list index
    >>> response = c.get('/lists/')
    
Then we check that everything went well.
    >>> response.status_code
    200
    
    >>> "All available Lists" in response.content
    True

Try to create a new list. 
And check the content to see that we came to the create page after 
logging in.

    >>> response = c.get('/lists/new/')
    
Then we check that everything went well.
    >>> response.status_code
    200
    
    >>> print "Create a new List on" in response.content
    True

Now create a new list called 'new_list'.
We should end up on a redirect
    >>> response = c.post('/lists/new/',
    ...                   {"listname": "new_list1",
    ...                    "mail_host": "mail.example.com",
    ...                    "list_owner": "james@example.com",
    ...                    "description": "doctest testing list",
    ...                    "advertised": "True",    
    ...                    "languages": "English (USA)"})    
    >>> print type(response) == HttpResponseRedirect
    True
    
List index page should now include the realname of the list

    >>> response = c.get('/lists/',HTTP_HOST='example.com')

Then we check that everything went well.
    >>> response.status_code
    200
    >>> "New_list1" in response.content
    True

List Summary
============

Four options appear on this page. The first one is to subscribe, 
2. to view archives
3. to edit the list settings #at least if you do have permission to do so
4. to unsubscribe

    >>> response = c.get('/lists/new_list1%40mail.example.com/',)    

Then we check that everything went well.
    >>> response.status_code
    200
    >>> "Subscribe" in response.content
    True
    >>> "Archives" in response.content
    True
    >>> "Edit Options" in response.content
    True
    >>> "Unsubscribe" in response.content
    True
    
Subscriptions   
=============

Get the Subscriptions Page and check that the form was prefilled with the users E-Mail
    >>> url = '/subscriptions/new_list1%40mail.example.com/subscribe'
    >>> response = c.get(url)

Then we check that everything went well.
    >>> response.status_code
    200
    >>> "james@example.com" in response.content
    True
    
Now subscribe James and Katie and check that you get redirected to List Summary which should now have an additional Button allowing to modify your user options.
    
    >>> response = c.post(url,
    ...                   {"email": "james@example.com",
    ...                   "real_name": "James Watt",
    ...                   "name": "subscribe",
    ...                   "fqdn_listname": "new_list1@mail.example.com"})
    >>> response = c.post(url,
    ...                   {"email": "katie@example.com",
    ...                   "real_name": "Katie Doe",
    ...                   "name": "subscribe",
    ...                   "fqdn_listname": "new_list1@mail.example.com"})   
    >>> print (_('Subscribed')+' katie@example.com') in response.content
    True
    
The logged in user (james@example.com) can now modify his own membership using a button which is displayed in list_summary   
    >>> response = c.get('/lists/new_list1%40mail.example.com/')
    >>> "mm_membership" in response.content
    True
    
Using the same subscription page we can unsubscribe as well.    
    >>> response = c.post('/subscriptions/new_list1%40mail.example.com/unsubscribe',
    ...                   {"email": "katie@example.com",
    ...                   "name": "unsubscribe",
    ...                   "fqdn_listname": "new_list1@mail.example.com"})
    >>> print (_('Unsubscribed')+' katie@example.com') in response.content
    True
    
Mass Subscribe Users (within settings)
======================================

Now we want to mass subscribe a few users to the list. Therefore, 
go to the mass subscription page.

    >>> url = '/subscriptions/new_list1%40mail.example.com/mass_subscribe/'
    >>> response = c.get(url)

Check that everything went well by making sure the status code 
was correct.

    >>> response.status_code
    200

Try mass subscribing the users 'liza@example.com' and 
'george@example.com'. Each address should be provided on a separate 
line so add '\\n' between the names to indicate that this was done 
(we're on a Linux machine which is why the letter 'n' was used and 
the double '\\' instead of a single one is to escape the string 
parsing of Python).

    >>> url = '/subscriptions/new_list1%40mail.example.com/mass_subscribe/'
    >>> response = c.post(url,
    ...                   {"emails": "liza@example.com\\ngeorge@example.com"})

If everything was successful, we shall get a positive response from 
the page. We'll check that this was the case.
    
    >>> print _("The mass subscription was successful.") in response.content
    True
    
Change the Memebership Settings
===============================

Now let's go to the membership settings page. Once we go there we 
should get a list of all the available lists.

    >>> response = c.get('/membership_settings/new_list1%40mail.example.com/')

Check that we came to the right place...

    >>> print "Membership Settings" in response.content
    True

...and select the list 'test-one@example.com'.

    >>> response = c.get('/membership_settings/new_list1%40mail.example.com/')

Lets make sure we got to the right page.

    >>> print ("Membership Settings" in response.content) and ("for new_list1@mail.example.com" in response.content)
    True
    
Delete the List
===============

Finally, let's delete the list.
We start by checking that the list is really there (for reference).

    >>> response = c.get('/lists/',HTTP_HOST='example.com')
    >>> print "New_list1" in response.content
    True

Trying to delete the List we have to confirm this action
    >>> response = c.get('/delete_list/new_list1%40mail.example.com/',)
    >>> print "Please confirm" in response.content
    True

Confirmed by pressing the button which requests the same page using POST
    >>> response = c.post('/delete_list/new_list1%40mail.example.com/',)

...and check that it's been deleted.
    >>> response = c.get('/lists/',HTTP_HOST='example.com')
    >>> print "new_list1%40example.com" in response.content
    False

So far this is what you can do in the UI. More tests can be added 
here later.    
    
Finishing Test
==============

    >>> teardown_mm(testobject)    
"""
