import os
import time
import shutil
import tempfile
import subprocess

class Testobject:
    bindir = None
    vardir = None
    cfgfile = None

def setup_mm(testobject):
    os.environ['MAILMAN_TEST_BINDIR'] = '/home/florian/Development/mailman/bin'
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
[qrunner.archive]
start: no
[qrunner.bounces]
start: no
[qrunner.command]
start: no
[qrunner.in]
start: no
[qrunner.lmtp]
start: no
[qrunner.news]
start: no
[qrunner.out]
start: no
[qrunner.pipeline]
start: no
[qrunner.retry]
start: no
[qrunner.virgin]
start: no
[qrunner.digest]
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
