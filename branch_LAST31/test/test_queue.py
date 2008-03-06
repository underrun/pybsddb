"""
TestCases for exercising a Queue DB.
"""

import sys, os, string
import tempfile
from pprint import pprint
import unittest

from bsddb3 import db

from test_all import verbose


#----------------------------------------------------------------------

class SimpleQueueTestCase(unittest.TestCase):
    def setUp(self):
        self.filename = tempfile.mktemp()

    def tearDown(self):
        try:
            os.remove(self.filename)
        except os.error:
            pass


    def test01_basic(self):
        d = db.DB()
        d.set_re_len(40)  # Queues must be fixed length
        d.open(self.filename, db.DB_QUEUE, db.DB_CREATE)

        if verbose:
            print "before appends" + '-' * 30
            pprint(d.stat())

        for x in string.letters:
            d.append(x * 40)

        assert len(d) == 52

        d.put(100, "some more data")
        d.put(101, "and some more ")
        d.put(75,  "out of order")
        d.put(1,   "replacement data")

        assert len(d) == 55

        if verbose:
            print "before close" + '-' * 30
            pprint(d.stat())

        d.close()
        del d
        d = db.DB()
        d.open(self.filename)

        if verbose:
            print "after open" + '-' * 30
            pprint(d.stat())

        d.append("one more")
        c = d.cursor()

        if verbose:
            print "after append" + '-' * 30
            pprint(d.stat())

        rec = c.consume()
        while rec:
            if verbose:
                print rec
            rec = c.consume()
        c.close()

        if verbose:
            print "after consume loop" + '-' * 30
            pprint(d.stat())

        assert len(d) == 0, \
               "if you see this message then you need to rebuild BerkeleyDB 3.1.17 "\
               "with the patch in patches/qam_stat.diff"

        d.close()

#----------------------------------------------------------------------

def suite():
    return unittest.makeSuite(SimpleQueueTestCase, 'test')


if __name__ == '__main__':
    if not unittest.TextTestRunner().run(suite()).wasSuccessful():
        sys.exit(1)
