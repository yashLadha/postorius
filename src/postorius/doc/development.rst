===========
Development
===========

This is a short guide to help you get started with Postorius development.


Development Workflow
====================

The source code is hosted on Launchpad_, which means that we are using
Bazaar for version control.

.. _Launchpad: https://launchpad.net/postorius

Changes are usually not made directly in the project's trunk branch, but in 
feature-related personal branches, which get reviewed and then merged into
the trunk. 

The ideal workflow would be like this:

1. File a bug to suggest a new feature or report a bug (or just pick one of 
   the existing bugs).
2. Create a new branch with your code changes.
3. Make a "merge proposal" to get your code reviewed and merged. 

Launchpad has a nice tour_ which describes all this in detail. 

.. _tour: https://launchpad.net/+tour/index


Testing
=======


After a fresh checkout of Postorius you can run the test from
Postorius' root directory using ``tox``:

::

    $ tox

All test modules reside in the ``postorius/src/postorius/tests``
directory.


Mocking calls to Mailman's REST API
-----------------------------------

A lot of Postorius' code involves calls to Mailman's REST API (through
the mailman.client library). Running these tests against a real instance
of Mailman would be bad practice and slow, so ``vcrpy`` fixtures are
used instead. See the `vcrpy Documentation`_ for details.

.. _`vcrpy Documentation`: https://github.com/kevin1024/vcrpy

If you write new tests, it's advisable to add a separate fixture file
for each test case, so the cached responses don't interfere with other
tests.


View Auth
=========

Three of Django's default User roles are relvant for Postorius:

- Superuser: Can do everything.
- AnonymousUser: Can view list index and info pages.
- Authenticated users: Can view list index and info pages. Can (un)subscribe
  from lists. 

Apart from these default roles, there are two others relevant in Postorius: 

- List owners: Can change list settings, moderate messages and delete their
  lists. 
- List moderators: Can moderate messages.

There are a number of decorators to protect views from unauthorized users.

- ``@user_passes_test(lambda u: u.is_superuser)`` (redirects to login form)
- ``@login_required`` (redirects to login form)
- ``@list_owner_required`` (returns 403 if logged-in user isn't the
  list's owner)
- ``@list_moderator_required`` (returns 403 if logged-in user isn't the
  list's moderator)


Accessing the Mailman API
=========================

Postorius uses mailman.client to connect to Mailman's REST API. In order to 
directly use the client, ``cd`` to your project folder and execute 
``python manage.py mmclient``. This will open a python shell (IPython, if
that's available) and provide you with a client object connected to to your
local Mailman API server (it uses the credentials from your settings.py).

A quick example:

::

    $ python manage.py mmclient

    >>> client
    <Client (user:pwd) http://localhost:8001/3.0/>

    >>> print client.system['mailman_version']
    GNU Mailman 3.0.0b2+ (Here Again)

    >>> mailman_dev = client.get_list('mailman-developers@python.org')
    >>> print mailman_dev settings
    {u'description': u'Mailman development', 
     u'default_nonmember_action': u'hold', ...}

For detailed information how to use mailman.client, check out its documentation_.

.. _documentation: http://bazaar.launchpad.net/~mailman-coders/mailman.client/trunk/view/head:/src/mailmanclient/docs/using.txt
