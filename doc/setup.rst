Installation
============

Mailman3 - a7
-------------
 
* Check Dependecys
    .. note::
        This might differ on different systems - I was testing Ubuntu 11.04 natty and needed to install Postfix before running the installation.
* Download or branch Mailman3a7 from http://launchpad.net/mailman/3.0/3.0.0a7/+download/mailman-3.0.0a7.tar.gz and unpack it.
* Change into the unpacked DIR which might be named "mailman-3.0.0a7"
    .. note::
        Please be aware that the following steps only work if you're really in that DIR. If you consider adding a subfolder name to the commands those woun't work !
* Run the Installation from a Shell (not Python)

    .. code-block:: bash

        $ bootstrap.py
        $ bin/buildout
    
* Vertify that everything was setup correclty and your branch fullfills the version requirements by running it's own test module

    .. code-block:: bash
    
        $ bin/test
        
* Now you're able to run mailman using

    .. code-block:: bash
    
        $ bin/mailman
    
Mailman Client / REST Api
-------------------------

Next thing you need to do is installing the Plugin used for communication with non-mailman-code parts like our WebUI. Within the Client Branch we've put both, Classes to access the Core which are run as a Plugin and some Python Bindings.
The Python Bindings were used later on within our Django Application to access the Server. Failing to install the Client would result in an offline version of WebUI

Once again start by branching the code which is on Launchpad

    .. code-block:: bash
    
        $ bzr branch lp:mailman.client

.. note::
    We've successfully tested our functionality with Revision 16 - In case the Client gets updated which it surely will in future we can't guarentee that it is compatible anymore.
    
As you only want to run the Client and not modify it's code you're fine with running the install command from within the directory. At the moment this requires Sudo Priveledges as files will copied to the Python Site-Packages Directory which is available to all users.

    .. code-block:: bash
    
        $ sudo python setup.py install

.. note::
    If you want to change parts of the Client you can use the development option which will create a Symlink instead of a Hardcopy of all files:

    .. code-block:: bash
    
        $ sudo python setup.py develop

All changes will apply once you restart Mailman itself.

Django 1.3
----------
During our development we started a Django Site based on the 1.2 Version which is included into Ubuntu's repositorys. This made the installation easy but we ended up having some points which would get a much better code when using some elements introducing in 1.3.
As Mailman is supposed to be long-time stable - or however you call it - we decided that we should stick to the latest stable version right away. For this reason you're required to install Django 1.3+ which is descriped on their Website. (https://www.djangoproject.com/download/)

.. note::
    Please be Aware that it's not recommended to run both 1.2 and 1.3 at the same time
    
In Django you've got 3 different levels of data.
- Django Installation Files
- Django Site
- Django Apps
usually you don't see the Installation as it's hidden somewhere within the System and the Apps are simply included into The Site Directory.
As we wanted to have the possibility to include the App into any Django Site which might already exist we decided to keep Site and App seperated.

During GSoC we've used different branches for this:
- lp:mailmanwebgsoc2011
- lp:mailmanwebgsoc2011/django-site-0.1

Django Site Installation
------------------------

We've created this branch for quick development - everyone is free to use his own Django site, but this one already includes a couple of modifications we've made that will allow running the Development Server just a few seconds after Branching both Site and App.

As far as I know at the moment we've made the following alignments: (All of these are in the settings.py file of the Django Site)

    REST_SERVER = 'localhost:8001'
    API_USER = 'restadmin' 
    API_PASS = 'restpass'
    
    .. note::
        These are the default values used by the Mailman Client we've installed earlier. Feel free to modify the password and username if you need to.

MAILMAN_TEST_BINDIR = '/home/benste/Projects/Gsoc_mailman/mailman-3.0.0a7/bin'
#/home/florian/Development/mailman/bin'

    .. note:: Running the test modules requires to launch a special version of mailman with it's own testing DB otherwise you'd destroy you're sites content during testing. This Path needs to point to YOUR own installation of mailman.

MAILMAN_THEME = "default"

    .. note:: 
        We decided to allow simple Appearance Modifications, to use a custom CSS you could simply add a Directory within the media directory of the app and Link it's name here. All HTML Pages will use the Styles from the Directory mentioned in here

PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
MEDIA_ROOT =  os.path.join(os.path.split(PROJECT_PATH)[0], "mailman_django/media/mailman_django/")
    .. note:: 
        Absolute path to the directory that holds media.
        Example: "/home/media/media.lawrence.com/"

MEDIA_URL = '/mailman_media/'

    .. note::
        URL that handles the media served from MEDIA_ROOT. Make sure to use a trailing slash if there is a path component (optional in other cases).Examples: "http://media.lawrence.com", "http://example.com/media/"

AUTHENTICATION_BACKENDS = (
    'mailman_django.auth.restbackend.RESTBackend',
    'django.contrib.auth.backends.ModelBackend'
    )

    .. note::
        This creates a connection in between Djangos Login and Permission Decorators which we use for authentification and a custom Backend which we created in Preparation to work together with the REST API or an upcoming Middleware.
        You need to keep the Django one for testing fallback.
    
TEMPLATE_CONTEXT_PROCESSORS=(
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.csrf",
    "django.contrib.messages.context_processors.messages",
    "mailman_django.context_processors.lists_of_domain",
    "mailman_django.context_processors.render_MAILMAN_THEME",
    "mailman_django.context_processors.extend_ajax"

    .. note::
        We're using Context Processors to easily render value which we need in nearly every view.
    
ROOT_URLCONF = 'mailman_django.urls'

    .. note::
        This is where our URL Config is - if you run your own site with other Apps as well you might want to adjust this to your urls.py which includes our file.

TEMPLATE_DIRS = (
    os.path.join(PROJECT_PATH, "mailman_django/templates"),        

    .. note::
        Adds our own Templates   
    
INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.admin',
    'mailman_django',

    .. note::
        Makes sure that Django knows about our directory as an App and creates needed Tables () when running

    .. code-block:: bash
    
        $ python manage.py syncdb

Now that you know about all these you might start the development server. As usual in Django this is done by running

    .. code-block:: bash
    
        $ python manage.py runserver

within the Django Site Directory - as usual the default address is localhost:8000
Of course it will only be able to start once our app is in place as well.

Django Application
------------------
First get the files, and make sure you paste them into your Project directory and adjust it's name to the appropriate configuration you've made earlier in the Django Site. Remeber our default is mailman_django

    .. code-block:: bash
    
        $ bzr branch lp:mailmanwebgsoc2011

.. note:: 
    We've tested Revision 172
    
.. note::
    We're planning to ease up installation by creating an egg    
