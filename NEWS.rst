==================================
Postorius - web ui for GNU Mailman
==================================

Copyright (C) 1998-2012 by the Free Software Foundation, Inc.

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
