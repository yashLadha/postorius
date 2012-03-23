Using the Django App - Developers Resource
==========================================

.. warning::
    This user guide is outdated and needs to be updated.

.. automodule:: tests.tests

Running the tests explained above.
----------------------------------
We've added our own test-suite to the Django App which will be executed together with the Django Test. Last thing you should do is running these tests. If they fail you did something wrong, if they succeed you can enjoy the site.

Run the following in the Site Directory

    .. code-block:: bash
    
        $ python manage.py test

.. note::
    Please be aware that we want to run a development instance of mailman you need to stop the stable one first and the tests will open it's own mailman temporily.

Accessing the REST Client for Testing
-------------------------------------

If you want to access the Functions, which we use in the views, directly feel free to run the following block of code within a Shell which does have it's current Directory within the Django Site Directory.

    .. code-block:: python
    
        from settings import API_USER, API_PASS
        from mailman.client import Client
        c = Client('http://localhost:8001/3.0', API_USER, API_PASS)
        #DEBUG: Python Session
