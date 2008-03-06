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
        self.filename = self.__class__.__name__ + '.db'
        homeDir = os.path.join(os.path.dirname(sys.argv[0]), 'db_home')
        self.homeDir = homeDir
        try: os.mkdir(homeDir)
        except os.error: pass

    def tearDown(self):
        try:   os.remove(self.filename)
        except os.error: pass
        import glob
        files = glob.glob(os.path.join(self.homeDir, '*'))
        for file in files:
            os.remove(file)



    def test01_badpointer(self):
        dbs = dbshelve.open(self.filename)
        dbs.close()
        self.assertRaises(db.DBError, dbs.get, "foo")


    def test02_db_home(self):
        env = db.DBEnv()
        # check for crash fixed when db_home is used before open()
        assert env.db_home is None
        env.open(self.homeDir, db.DB_CREATE)
        assert self.homeDir == env.db_home

#----------------------------------------------------------------------


def test_suite():
    return unittest.makeSuite(MiscTestCase)


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
