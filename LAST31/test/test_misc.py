"""
Misc TestCases
"""

import sys, os, string
import tempfile
from pprint import pprint
import unittest

from bsddb3 import db
from bsddb3 import dbshelve

from test_all import verbose

#----------------------------------------------------------------------

class MiscTestCase(unittest.TestCase):
    def setUp(self):
        self.filename = tempfile.mktemp()

    def tearDown(self):
        try:
            os.remove(self.filename)
        except os.error:
            pass



    def test01_badpointer(self):
        dbs = dbshelve.open(self.filename)
        dbs.close()
        self.assertRaises(db.DBError, dbs.get, "foo")



#----------------------------------------------------------------------


def suite():
    return unittest.makeSuite(MiscTestCase, 'test')


if __name__ == '__main__':
    if not unittest.TextTestRunner().run(suite()).wasSuccessful():
        sys.exit(1)


