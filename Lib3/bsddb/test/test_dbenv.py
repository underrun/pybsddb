import unittest
import os, glob

from .test_all import db, test_support, get_new_environment_path, \
        get_new_database_path

#----------------------------------------------------------------------

class DBEnv(unittest.TestCase):
    def setUp(self):
        self.homeDir = get_new_environment_path()
        self.env = db.DBEnv()

    def tearDown(self):
        del self.env
        test_support.rmtree(self.homeDir)

    if db.version() >= (4, 2) :
        def test_get_data_dirs(self) :
            dirs = ("a", "b", "c", "d")
            for i in dirs :
                self.env.set_data_dir(i)
            self.assertEqual(dirs, self.env.get_data_dirs())

    if db.version() >= (4, 4) :
        def test_mutex_setget_max(self) :
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

        def test_mutex_setget_increment(self) :
            v = self.env.mutex_get_increment()
            v2 = 127

            self.env.mutex_set_increment(v2)
            self.assertEqual(v2, self.env.mutex_get_increment())

            self.env.mutex_set_increment(v)
            self.assertEqual(v, self.env.mutex_get_increment())

            # You can not change configuration after opening
            # the environment.
            self.env.open(self.homeDir, db.DB_CREATE)
            self.assertRaises(db.DBInvalidArgError,
                    self.env.mutex_set_increment, v2)

        def test_mutex_setget_tas_spins(self) :
            self.env.mutex_set_tas_spins(0)  # Default = BDB decides
            v = self.env.mutex_get_tas_spins()
            v2 = v*2+1

            self.env.mutex_set_tas_spins(v2)
            self.assertEqual(v2, self.env.mutex_get_tas_spins())

            self.env.mutex_set_tas_spins(v)
            self.assertEqual(v, self.env.mutex_get_tas_spins())

            # In this case, you can change configuration
            # after opening the environment.
            self.env.open(self.homeDir, db.DB_CREATE)
            self.env.mutex_set_tas_spins(v2)

        def test_mutex_setget_align(self) :
            v = self.env.mutex_get_align()
            v2 = 64
            if v == 64 :
                v2 = 128

            self.env.mutex_set_align(v2)
            self.assertEqual(v2, self.env.mutex_get_align())

            # Requires a nonzero power of two
            self.assertRaises(db.DBInvalidArgError,
                    self.env.mutex_set_align, 0)
            self.assertRaises(db.DBInvalidArgError,
                    self.env.mutex_set_align, 17)

            self.env.mutex_set_align(2*v2)
            self.assertEqual(2*v2, self.env.mutex_get_align())

            # You can not change configuration after opening
            # the environment.
            self.env.open(self.homeDir, db.DB_CREATE)
            self.assertRaises(db.DBInvalidArgError,
                    self.env.mutex_set_align, v2)


def test_suite():
    return unittest.makeSuite(DBEnv)

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')