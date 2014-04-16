# -*- coding: utf-8 -*-
# Copyright (C) 1998-2014 by the Free Software Foundation, Inc.
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
import os
import time
import shutil
import logging
import tempfile
import subprocess

from django.conf import settings
from mailmanclient import Client


logger = logging.getLogger(__name__)


mm_client = Client('%s/3.0' % settings.MAILMAN_TEST_API_URL,
                   settings.MAILMAN_TEST_USER,
                   settings.MAILMAN_TEST_PASS)


class Testobject:
    bindir = None
    vardir = None
    cfgfile = None


def setup_mm(testobject):
    bindir = testobject.bindir = settings.MAILMAN_TEST_BINDIR
    if bindir is None:
        raise RuntimeError("something's not quite right")
    vardir = testobject.vardir = tempfile.mkdtemp()
    cfgfile = testobject.cfgfile = os.path.join(vardir, 'client_test.cfg')
    with open(cfgfile, 'w') as fp:
        print >> fp, """\
[mailman]
layout: tmpdir
[paths.tmpdir]
var_dir: {vardir}
log_dir: /tmp/mmclient/logs
[runner.archive]
start: no
[runner.bounces]
start: no
[runner.command]
start: no
[runner.in]
start: no
[runner.lmtp]
start: no
[runner.news]
start: no
[runner.out]
start: no
[runner.pipeline]
start: no
[runner.retry]
start: no
[runner.virgin]
start: no
[runner.digest]
start: no
[webservice]
port: 9001
""".format(vardir=vardir)
    mailman = os.path.join(bindir, 'mailman')
    subprocess.call([mailman, '-C', cfgfile, 'start', '-q'])
    time.sleep(3)
    return testobject


def teardown_mm(testobject):
    bindir = testobject.bindir
    cfgfile = testobject.cfgfile
    vardir = testobject.vardir
    mailman = os.path.join(bindir, 'mailman')
    subprocess.call([mailman, '-C', cfgfile, 'stop', '-q'])
    shutil.rmtree(vardir)
