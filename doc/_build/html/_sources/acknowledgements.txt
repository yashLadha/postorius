Acknowledgements
================

Test Server
-----------

We're proud to provide you a development server which is sponsered by XXX #Todo
Feel free to change anything you like, we can simply rest the DB from Time to Time.

Missing Functionality
---------------------

* Delete Domain
    * missing in REST
    * implemented in mailman3 a8

* Show a List of all subscribed users

ACL
---

* Middleware

    We don't have the Middleware which is required to work with users and it's permissions yet. For this reason we had to tweak some functions to be a hardcoded Demo object.

    * Login Check
        At the moment we're using a hardcoded List of allowed usernames and Passwords which are all stored in Plain within the AuthBackends Source File.
    * has_perm Decorator
        As we don't have a middleware to check for users and it's permissions we do only use one permission at the moment. The permission site domain_admin is hardcoded to user.username == "james@example.com"



Ideas
-----

* ContactPage
* 
