# -*- coding: utf-8 -*-
# Copyright (C) 1998-2012 by the Free Software Foundation, Inc.
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

import os
import time
import shutil
import tempfile
import subprocess
from django.conf import settings

class Testobject:
    bindir = None
    vardir = None
    cfgfile = None

def setup_mm(testobject):
    os.environ['MAILMAN_TEST_BINDIR'] = settings.MAILMAN_TEST_BINDIR
    bindir = testobject.bindir = os.environ.get('MAILMAN_TEST_BINDIR')
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
    time.sleep(3)
