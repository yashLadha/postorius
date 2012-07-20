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


``postorius.*`` imports in test modules
---------------------------------------

When writing unittests make sure that any ``postorius.*`` imports are made
at the test method level and not at the module level. Here's why:

The Postorius documentation (the one you are reading right now) imports some
doctest modules from the test package using Sphinx's autodoc extension. This is
a very nice feature, but in this scenario it has the nasty side effect of
breaking the build process if application code is imported as well (it will
fail to find an environment variable that Django needs to run). This can be
easily prevented by avoiding module level imports of postorius code in the test
modules.

Good:

::

    from django.utils import unittest
    from mock import patch


    class SomeTest(unittest.TestCase):

        def test_some_method(self):
            from postorius.views import SomeViewClass
            foo = 'bar'

Bad:

::

    from django.utils import unittest
    from mock import patch
    from postorius.views import SomeViewClass


    class SomeTest(unittest.TestCase):

        def test_some_method(self):
            foo = 'bar'



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
