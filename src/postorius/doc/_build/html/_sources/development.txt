===========
Development
===========


This is a short guide to help you get started with Postorius development.


Directory layout
================

Postorius is a Django application, so if you have developed with Django before,
the file structure probably looks familiar. These are the basics:

::

    __init__.py
    auth/                   # Custom authorization code (List owners and
                            # moderators)
    context_processors.py   # Some variables available in all templates
    doc/                    # Sphinx documentation
    fieldset_forms.py       # A custom form class to build html forms with
                            # fieldsets
    forms.py                # All kinds of classes to build and validate forms
    management/             # Commands to use with Django's manage.py script
    models.py               # Code to connect to mailman.client and provide
                            # a Django-style model API for lists, mm-users and 
                            # domains
    static/                 # Static files (CSS, JS, images)
    templates/              # HTML Templates
    tests/                  # Postorius test files
    urls.py                 # URL routes
    utils.py                # Some handy utilities
    views/                  
        views.py            # View classes and functions for all views connected
                            # in urls.py
        generic.py          # Generic class-based views; Currently holds a 
                            # class for view based on a single mailing list


Authentication/Authorization
============================


Testing
=======

All test modules reside in the ``postorius/src/postorius/tests`` directory
and this is where you should put your own tests, too. To make the django test
runner find your tests, make sure to add them to the folder's ``__init__.py``:

::

    from postorius.tests import test_utils
    from postorius.tests.test_list_members import ListMembersViewTest
    from postorius.tests.test_list_settings import ListSettingsViewTest
    from postorius.tests.my_own_tests import MyOwnUnitTest
    
    __test__ = {
        "Test Utils": test_utils,
        "List Members": ListMembersViewTest,
        "List Settings": ListSettingsViewTest,
        "My Own Test": MyOwnUnitTest,
    }


Running the tests
-----------------

To run the tests go to your project folder and run ``python manage.py test postorius`` from there.


Mocking
-------

Postorius uses Michael Foord's ``mock`` library for mocking. There are some
shortcuts you can use to quickly create mock objects that behave a little bit like
objects retreived from mailman.client, like:

- Domains
- Mailing Lists
- Users
- Memberships
- Addresses


Mocking mailman.client objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. automodule:: postorius.tests.test_utils
