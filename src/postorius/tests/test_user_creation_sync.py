# -*- coding: utf-8 -*-
# Copyright (C) 2012 by the Free Software Foundation, Inc.
#
# This file is part of Postorius.
#
# Postorius is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
# Postorius is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# Postorius.  If not, see <http://www.gnu.org/licenses/>.

from django.contrib.auth.models import AnonymousUser, User
from django.core.exceptions import PermissionDenied
from django.test.client import RequestFactory
from postorius.tests.utils import create_mock_list
from django.utils import unittest
from mock import patch

from postorius.auth.decorators import (list_owner_required,
                                       list_moderator_required)
from postorius.models import (Domain, List, Member, MailmanUser,
                              MailmanApiError, Mailman404Error)
from mailmanclient import Client


class UserCreationSyncTest(unittest.TestCase):
    """Tests if a newly saved db user is synced to the mailman core.
    """
    pass
