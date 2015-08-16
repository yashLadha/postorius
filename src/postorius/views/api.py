# -*- coding: utf-8 -*-
# Copyright (C) 1998-2015 by the Free Software Foundation, Inc.
#
# This file is part of Postorius.
#
# Postorius is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# Postorius is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along with
# Postorius.  If not, see <http://www.gnu.org/licenses/>.


import json
import logging



from django.http import HttpResponse

from postorius import utils
from postorius.auth.decorators import *


logger = logging.getLogger(__name__)


@basic_auth_login
@loggedin_or_403
def api_list_index(request):
    client = utils.get_client()
    res, content = client._connection.call('lists')
    return HttpResponse(json.dumps(content['entries']),
                        content_type="application/json")
