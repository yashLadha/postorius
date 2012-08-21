===========
Development
===========


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
