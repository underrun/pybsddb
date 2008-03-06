# This module is a bridge.
#
# Code is copied from Python 2.6 (trunk) Lib/test/test_support.py that
# the bsddb test suite needs even when run standalone on a python
# version that may not have all of these.

# DO NOT ADD NEW UNIQUE CODE.  Copy code from the python trunk
# trunk test_support module into here.  If you need a place for your
# own stuff specific to bsddb tests, make a bsddb.test.foo module.

import errno
import os
import shutil
 
def unlink(filename):
    try:
        os.unlink(filename)
    except OSError:
        pass

def rmtree(path):
    try:
        shutil.rmtree(path)
    except OSError, e:
        # Unix returns ENOENT, Windows returns ESRCH.
        if e.errno not in (errno.ENOENT, errno.ESRCH):
            raise
