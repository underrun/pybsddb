import unittest
import os, glob

from .test_all import db, test_support, get_new_environment_path, \
        get_new_database_path

#----------------------------------------------------------------------

class DB(unittest.TestCase):
    import sys
    if sys.version_info[:3] < (2, 4, 0):
        def assertTrue(self, expr, msg=None):
            self.failUnless(expr,msg=msg)

    def setUp(self):
        self.path = get_new_database_path()
        self.db = db.DB()

    def tearDown(self):
        self.db.close()
        del self.db
        test_support.rmtree(self.path)

class DB_hash(DB) :
    if db.version() >= (4, 2) :
        def test_h_ffactor(self) :
            for ffactor in [4, 16, 256] :
                self.db.set_h_ffactor(ffactor)
                self.assertEqual(ffactor, self.db.get_h_ffactor())


def test_suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(DB_hash))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
