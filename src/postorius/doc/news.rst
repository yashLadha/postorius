================
News / Changelog
================

Copyright (C) 2012 by the Free Software Foundation, Inc.

The Postorius Django app provides a web user interface to
access GNU Mailman.

Postorius is free software: you can redistribute it and/or
modify it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, version 3 of the License.

Postorius is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser
General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with Postorius. If not, see <http://www.gnu.org/licenses/>.


1.0 alpha 2
===========
(2012-XX-XX)

* dev setup fix for Django 1.4 contributed by Rohan Jain
* missing csrf tokens in templates contributed by Richard Wackerbarth (LP: 996658)
* moderation: fixed typo in success message call
* installation documentation for Apache/mod_wsgi
* moved project files to separate branch
* show error message if connection to Mailman API fails
* added list members view
* added developer documentation
* added test helper utils
* all code now conform to PEP8
* themes: removed obsolete MAILMAN_THEME settings from templates, contexts, file structure; contributed by Richard Wackerbarth (LP: 1043258)
* added access control for list owners and moderators
* added a mailmanclient shell to use as a `manage.py` command (`python manage.py mmclient`)
* use "url from future" template tag in all templates. Contributed by Richard Wackerbarth.
* added "new user" form. Contributed by George Chatzisofroniou.
* added user subscription page
* added decorator to allow login via http basic auth (to allow non-browser clients to use API views)
* added api view for list index
* several changes regarding style and navigation structure
* updated to jQuery 1.8. Contributed by Richard Wackerbarth.
* added a favicon. Contributed by Richard Wackerbarth.
* renamed some menu items. Contributed by Richard Wackerbarth.
* changed static file inclusion. Contributed by Richard Wackerbarth.
* added delete domain feature.
* url conf refactoring. Contributed by Richard Wackerbarth.
* added user deletion feature. Contributed by Varun Sharma.



1.0 alpha 1 -- "Space Farm"
===========================
(2012-03-23)

Many thanks go out to Anna Senarclens de Grancy and Benedict Stein for
developing the initial versions of this Django app during the Google Summer of
Code 2010 and 2011.

* add/remove/edit mailing lists
* edit list settings
* show all mailing lists on server
* subscribe/unsubscribe/mass subscribe mailing lists
* add/remove domains
* show basic list info and metrics
* login using django user account or using BrowserID
* show basic user profile
* accept/discard/reject/defer messages
* Implementation of Django Messages contributed by Benedict Stein (LP: #920084)
* Dependency check in setup.py contributed by Daniel Mizyrycki
* Proper processing of acceptable aliases in list settings form contributed by
  Daniel Mizyrycki
