# -*- coding: utf-8 -*-
# Copyright (C) 1998-2010 by the Free Software Foundation, Inc.
#
# This file is part of GNU Mailman.
#
# GNU Mailman is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# GNU Mailman is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# GNU Mailman.  If not, see <http://www.gnu.org/licenses/>.

# https://docs.djangoproject.com/en/dev/topics/auth/

from django.contrib.auth.models import User, check_password

class RESTBackend:
    """
    Authenticate against the settings the REST Middleware
    checking permissions ...

    Development uses hardcoded users atm.

    """

    supports_object_permissions = False
    supports_anonymous_user = False
    supports_inactive_user = False

    def authenticate(self, **credentials):
        """
        This authenticate function will check with the REST Middleware  
        wheteher the user exists and did provide a valid password.
        
        DEV: TODO - needs Middleware connection
        """
        # make_password is used to create sha1 strings
        valid_users = {"james@example.com": "james", #workaround until middleware exists
                       "katie@example.com": "katie",
                       "kevin@example.com": "kevin"}
        login_valid = credentials["username"] in valid_users.keys()
        try:
            pwd_valid = (credentials["password"] == valid_users[credentials["username"]])
        except KeyError:
            pwd_valid = False
        if login_valid and pwd_valid:
            try:
                user = User.objects.get(username=credentials["username"])
            except User.DoesNotExist:
                # Create a new user. Note that we can set password
                # to anything, because it won't be checked; the password
                # from settings.py will.
                user = User(username=credentials["username"], password='doesnt matter')
                user.is_staff = False
                user.is_superuser = False
                user.save()
            return user
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
            
    def has_perm(self, user_obj, perm):
        if user_obj.username == "james@example.com":
            return True
        else:
            return False
