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
=================
Try to access some of the admin Pages. Accessing these pages
redirects to a login page since we need admin authority to view and use them
#TODO - ACL tests will be implemented for each site at a central place at later stages of development.
Please be aware that this test only checks for authentification ONCE.

    >>> response = c.get('/domains/')

Check that login required was in the HTML content of what was loaded

    >>> print "Login Required" in response.content
    True

Hence, we log in as an admin on the login page we get as a response 
to our call.    

    >>> response = c.post('/domains/',
    ...                   {"addr": "kevin@example.com",
    ...                   "psw": "kevin"})

    >>> print "Add a new Domain" in response.content
    True
    
Create a New Domain
=================
Check the content to see that we came to the create page after 
logging in.

    >>> response = c.post('/domains/')

    >>> print "Add a new Domain" in response.content
    True

Now create a new Domain called 'mail.example.com'.

    >>> response = c.post('/domains/',
    ...                   {"mail_host": "mail.example.com",
    ...                    "web_host": "example.com",
    ...                    "description": "doctest testing domain"})  

Check that the new Domain exists in the list of existing domains which is above new_domain form

    >>> print "doctest testing domain" in response.content
    True
      

Create a New List
=================

Try to create a new list. 

    >>> response = c.post('/lists/new/')

Check the content to see that we came to the create page after 
logging in.

    >>> print "Create a new list" in response.content
    True
    
Now create a new list called 'new_list'.

    >>> response = c.post('/lists/new/',
    ...                   {"listname": "new_list",
    ...                    "mail_host": "mail.example.com",
    ...                    "list_owner": "kevin@example.com",
    ...                    "list_type": "closed_discussion",
    ...                    "description": "doctest testing domain",
    ...                    "languages": "English (USA)"})    

We should now end up on a success page offering what to do next. 
Let's check that this was the case.

    >>> print "What would you like to do next?" in response.content
    True #TODO:Duplication Bug needs test DB

Three options appear on this page. The first one is to mass subscribe
users, the second is to go to the settings page of the list just 
created and the third is to create another list. 
We're still logged in so go to the page where the settings can be 
changed (this page also requires admin authority).

    >>> response = c.get('/settings/new_list%40mail.example.com/',)    
    
    

Mass Subscribe Users
====================

Now we want to mass subscribe a few users to the list. Therefore, 
go to the mass subscription page.

    >>> url = '/settings/new_list%40mail.example.com/mass_subscribe/'

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

    >>> url = '/settings/new_list%40mail.example.com/mass_subscribe/'

    >>> response = c.post(url,
    ...                   {"emails": "liza@example.com\\ngeorge@example.com"})

If everything was successful, we shall get a positive response from 
the page. We'll check that this was the case.
    
    >>> print ("The mass subscription was successful." in response.content) or ("HTTP Error 409: Member already subscribed" in response.content) #TODO - doubled data after multiple tests
    True

Done with the admin stuff. Now let's log out.

    >>> response = c.get('/lists/logout/',)

If the request was successful we should end up on the list info page.
Now make sure that we got redirected there.

    >>> print "All mailing lists" in response.content
    True
    
TODO: Delete Domains    
"""
