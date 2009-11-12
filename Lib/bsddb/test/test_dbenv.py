import unittest
import os, glob

from test_all import db, test_support, get_new_environment_path, \
        get_new_database_path

#----------------------------------------------------------------------

class DBEnv(unittest.TestCase):
    import sys
    if sys.version_info[:3] < (2, 4, 0):
        def assertTrue(self, expr, msg=None):
            self.failUnless(expr,msg=msg)

    def setUp(self):
        self.homeDir = get_new_environment_path()
        self.env = db.DBEnv()

    def tearDown(self):
        self.env.close()
        del self.env
        test_support.rmtree(self.homeDir)

class DBEnv_general(DBEnv) :
    if db.version() >= (4, 4) :
        def test_lg_filemode(self) :
            for i in [0600, 0660, 0666] :
                self.env.set_lg_filemode(i)
                self.assertEqual(i, self.env.get_lg_filemode())

    if db.version() >= (4, 2) :
        def test_lk_max_lockers(self) :
            for i in [1000, 2000, 3000] :
                self.env.set_lk_max_lockers(i)
                self.assertEqual(i, self.env.get_lk_max_lockers())

        def test_lg_regionmax(self) :
            for i in [128, 256, 1024] :
                i = i*1024*1024
                self.env.set_lg_regionmax(i)
                j = self.env.get_lg_regionmax()
                self.assertTrue(i <= j)
                self.assertTrue(2*i > j)

        def test_lk_detect(self) :
            for i in [db.DB_LOCK_DEFAULT, db.DB_LOCK_EXPIRE,
                    db.DB_LOCK_MAXLOCKS, db.DB_LOCK_MAXWRITE,
                    db.DB_LOCK_MINLOCKS, db.DB_LOCK_MINWRITE,
                    db.DB_LOCK_OLDEST, db.DB_LOCK_RANDOM, db.DB_LOCK_YOUNGEST]:
                self.env.set_lk_detect(i)
                self.assertEqual(i, self.env.get_lk_detect())

        def test_lg_dir(self) :
            for i in ["a", "bb", "ccc", "dddd"] :
                self.env.set_lg_dir(i)
                self.assertEqual(i, self.env.get_lg_dir())

        def test_lg_bsize(self) :
            log_size = 70*1024
            self.env.set_lg_bsize(log_size)
            self.assertTrue(self.env.get_lg_bsize() >= log_size)
            self.assertTrue(self.env.get_lg_bsize() < 4*log_size)
            self.env.set_lg_bsize(4*log_size)
            self.assertTrue(self.env.get_lg_bsize() >= 4*log_size)

        def test_setget_data_dirs(self) :
            dirs = ("a", "b", "c", "d")
            for i in dirs :
                self.env.set_data_dir(i)
            self.assertEqual(dirs, self.env.get_data_dirs())

        def test_setget_cachesize(self) :
            cachesize = (0, 512*1024*1024, 3)
            self.env.set_cachesize(*cachesize)
            self.assertEqual(cachesize, self.env.get_cachesize())

            cachesize = (0, 1*1024*1024, 5)
            self.env.set_cachesize(*cachesize)
            cachesize2 = self.env.get_cachesize()
            self.assertEqual(cachesize[0], cachesize2[0])
            self.assertEqual(cachesize[2], cachesize2[2])
            # Berkeley DB expands the cache 25% accounting overhead,
            # if the cache is small.
            self.assertEqual(125, int(100.0*cachesize2[1]/cachesize[1]))

            # You can not change configuration after opening
            # the environment.
            self.env.open(self.homeDir, db.DB_CREATE | db.DB_INIT_MPOOL)
            cachesize = (0, 2*1024*1024, 1)
            self.assertRaises(db.DBInvalidArgError,
                self.env.set_cachesize, *cachesize)
            self.assertEqual(cachesize2, self.env.get_cachesize())

        def test_set_cachesize_dbenv_db(self) :
            # You can not configure the cachesize using
            # the database handle, if you are using an environment.
            d = db.DB(self.env)
            self.assertRaises(db.DBInvalidArgError,
                d.set_cachesize, 0, 1024*1024, 1)

        def test_setget_shm_key(self) :
            shm_key=137
            self.env.set_shm_key(shm_key)
            self.assertEqual(shm_key, self.env.get_shm_key())
            self.env.set_shm_key(shm_key+1)
            self.assertEqual(shm_key+1, self.env.get_shm_key())

            # You can not change configuration after opening
            # the environment.
            self.env.open(self.homeDir, db.DB_CREATE | db.DB_INIT_MPOOL)
            # If we try to reconfigure cache after opening the
            # environment, core dump.
            self.assertRaises(db.DBInvalidArgError,
                self.env.set_shm_key, shm_key)
            self.assertEqual(shm_key+1, self.env.get_shm_key())

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


class DBEnv_memp(DBEnv):
    def setUp(self):
        DBEnv.setUp(self)
        self.env.open(self.homeDir, db.DB_CREATE | db.DB_INIT_MPOOL | db.DB_INIT_LOG )
        self.db = db.DB(self.env)
        self.db.open("test", db.DB_HASH, db.DB_CREATE, 0660)

    def tearDown(self):
        self.db.close()
        del self.db
        DBEnv.tearDown(self)

    def test_memp_trickle(self) :
        self.db.put("hi", "bye")
        self.assertTrue(self.env.memp_trickle(100) > 0)

def test_suite():
    suite = unittest.TestSuite()

    suite.addTest(unittest.makeSuite(DBEnv_general))
    suite.addTest(unittest.makeSuite(DBEnv_memp))

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
