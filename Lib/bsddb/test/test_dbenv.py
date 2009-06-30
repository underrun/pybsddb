import unittest
import os, glob

from test_all import db, test_support, get_new_environment_path, \
        get_new_database_path

#----------------------------------------------------------------------

class DBEnv(unittest.TestCase):
    def setUp(self):
        self.homeDir = get_new_environment_path()
        self.env = db.DBEnv()

    def tearDown(self):
        del self.env
        test_support.rmtree(self.homeDir)

    if db.version() >= (4, 4) :
        def test_mutex_set_max(self):
            v = self.env.mutex_get_max()
            v2 = v*2+1

            self.env.mutex_set_max(v2)
            self.assertEqual(v2, self.env.mutex_get_max())

            self.env.mutex_set_max(v)
            self.assertEqual(v, self.env.mutex_get_max())

            # You can not change configuration after opening
            # the environment.
            self.env.open(self.homeDir, db.DB_CREATE)
            self.assertRaises(db.DBInvalidArgError,
                    self.env.mutex_set_max, v2)


def test_suite():
    return unittest.makeSuite(DBEnv)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
