import unittest
import tempfile
import os, glob

try:
    # For Pythons w/distutils pybsddb
    from bsddb3 import db
except ImportError:
    # For Python 2.3
    from bsddb import db

from test_all import get_new_environment_path, get_new_database_path

try:
    from bsddb3 import test_support
except ImportError:
    from test import test_support

#----------------------------------------------------------------------

class pget_bugTestCase(unittest.TestCase):
    """Verify that cursor.pget works properly"""
    db_name = 'test-cursor_pget.db'

    def setUp(self):
        self.homeDir = get_new_environment_path()
        self.env = db.DBEnv()
        self.env.open(self.homeDir, db.DB_CREATE | db.DB_INIT_MPOOL)
        self.primary_db = db.DB(self.env)
        self.primary_db.open(self.db_name, 'primary', db.DB_BTREE, db.DB_CREATE)
        self.secondary_db = db.DB(self.env)
        self.secondary_db.set_flags(db.DB_DUP)
        self.secondary_db.open(self.db_name, 'secondary', db.DB_BTREE, db.DB_CREATE)
        self.primary_db.associate(self.secondary_db, lambda key, data: data)
        self.primary_db.put('salad', 'eggs')
        self.primary_db.put('spam', 'ham')
        self.primary_db.put('omelet', 'eggs')


    def tearDown(self):
        self.secondary_db.close()
        self.primary_db.close()
        self.env.close()
        del self.secondary_db
        del self.primary_db
        del self.env
        test_support.rmtree(self.homeDir)

    def test_pget(self):
        cursor = self.secondary_db.cursor()

        self.assertEquals(('eggs', 'salad', 'eggs'), cursor.pget(key='eggs', flags=db.DB_SET))
        self.assertEquals(('eggs', 'omelet', 'eggs'), cursor.pget(db.DB_NEXT_DUP))
        self.assertEquals(None, cursor.pget(db.DB_NEXT_DUP))

        self.assertEquals(('ham', 'spam', 'ham'), cursor.pget('ham', 'spam', flags=db.DB_SET))
        self.assertEquals(None, cursor.pget(db.DB_NEXT_DUP))

        cursor.close()


def test_suite():
    return unittest.makeSuite(pget_bugTestCase)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
