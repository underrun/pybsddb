"""TestCases for checking that it does not segfault when a DBEnv object
is closed before its DB objects.
"""

import os
import tempfile
import unittest

try:
    # For Pythons w/distutils pybsddb
    from bsddb3 import db
except ImportError:
    # For Python 2.3
    from bsddb import db

try:
    from bsddb3 import test_support
except ImportError:
    from test import test_support

from test_all import verbose

# We're going to get warnings in this module about trying to close the db when
# its env is already closed.  Let's just ignore those.
try:
    import warnings
except ImportError:
    pass
else:
    warnings.filterwarnings('ignore',
                            message='DB could not be closed in',
                            category=RuntimeWarning)


#----------------------------------------------------------------------

class DBEnvClosedEarlyCrash(unittest.TestCase):
    def setUp(self):
        self.homeDir = os.path.join(tempfile.gettempdir(), 'db_home%d'%os.getpid())
        try: os.mkdir(self.homeDir)
        except os.error: pass
        tempfile.tempdir = self.homeDir
        self.filename = os.path.split(tempfile.mktemp())[1]
        tempfile.tempdir = None

    def tearDown(self):
        test_support.rmtree(self.homeDir)

    def test01_close_dbenv_before_db(self):
        dbenv = db.DBEnv()
        dbenv.open(self.homeDir,
                   db.DB_INIT_CDB| db.DB_CREATE |db.DB_THREAD|db.DB_INIT_MPOOL,
                   0666)

        d = db.DB(dbenv)
        d2 = db.DB(dbenv)
        d.open(self.filename, db.DB_BTREE, db.DB_CREATE | db.DB_THREAD, 0666)
        try :
          d2.open(self.filename+"2", db.DB_BTREE, db.DB_THREAD, 0666)
        except :
          pass  # Must give an error
        else :
          assert 0, "Where is my exception?"

        d.put("test","this is a test")
        assert d.get("test")=="this is a test", "put!=get"
        dbenv.close()  # This "close" should close the child db handle also
        try :
          d.get("test")
        except db.DBError :
          return
        assert 0, "Where is my exception?"

    def test02_close_dbenv_before_dbcursor(self):
        dbenv = db.DBEnv()
        dbenv.open(self.homeDir,
                   db.DB_INIT_CDB| db.DB_CREATE |db.DB_THREAD|db.DB_INIT_MPOOL,
                   0666)

        d = db.DB(dbenv)
        d.open(self.filename, db.DB_BTREE, db.DB_CREATE | db.DB_THREAD, 0666)

        d.put("test","this is a test")
        d.put("test2","another test")
        d.put("test3","another one")
        assert d.get("test")=="this is a test", "put!=get"
        c=d.cursor()
        c.first()
        c.next()
        d.close()  # This "close" should close the child db handle also
        ok=False
        try :
          c.next()
        except db.DBError :
          ok=True
        assert ok, "db.close doesn't close the child cursor"

        d = db.DB(dbenv)
        d.open(self.filename, db.DB_BTREE, db.DB_CREATE | db.DB_THREAD, 0666)
        c=d.cursor()
        c.first()
        c.next()
        dbenv.close()  # This "close" should close the child db handle also, with cursors
        ok=False
        try :
          c.next()
        except db.DBError :
          ok=True
        assert ok, "dbenv.close doesn't close the child cursor"

    def test03_close_db_before_dbcursor_without_env(self):
        d = db.DB()
        d.open(self.filename, db.DB_BTREE, db.DB_CREATE | db.DB_THREAD, 0666)

        d.put("test","this is a test")
        d.put("test2","another test")
        d.put("test3","another one")
        assert d.get("test")=="this is a test", "put!=get"
        c=d.cursor()
        c.first()
        c.next()
        d.close()  # This "close" should close the child db handle also
        ok=False
        try :
          c.next()
        except db.DBError :
          ok=True
        assert ok, "db.close doesn't close the child cursor"

    def test04_close_massive(self):
        dbenv = db.DBEnv()
        dbenv.open(self.homeDir,
                   db.DB_INIT_CDB| db.DB_CREATE |db.DB_THREAD|db.DB_INIT_MPOOL,
                   0666)

        dbs=[db.DB(dbenv) for i in xrange(16)]
        cursors=[]
        for i in dbs :
          i.open(self.filename, db.DB_BTREE, db.DB_CREATE | db.DB_THREAD, 0666)

        dbs[10].put("test","this is a test")
        dbs[10].put("test2","another test")
        dbs[10].put("test3","another one")
        assert dbs[4].get("test")=="this is a test", "put!=get"

        for i in dbs :
          cursors.extend([i.cursor() for j in xrange(32)])

        for i in dbs[::3] :
          i.close()
        for i in cursors[::3] :
          i.close()

        ok=False
        try :
          dbs[9].get("test")
        except db.DBError :
          ok=True
        assert ok, "Missing exception in DB! (after DB close)"

        ok=False
        try :
          cursors[101].first()
        except db.DBError :
          ok=True
        assert ok, "Missing exception in DBCursor! (after DB close)"

        cursors[80].first()
        cursors[80].next()
        dbenv.close()  # This "close" should close the child db handle also
        ok=False
        try :
          cursors[80].next()
        except db.DBError :
          ok=True
        assert ok, "Missing exception! (after DBEnv close)"

    def test05_close_dbenv_delete_db_success(self):
        dbenv = db.DBEnv()
        dbenv.open(self.homeDir,
                   db.DB_INIT_CDB| db.DB_CREATE |db.DB_THREAD|db.DB_INIT_MPOOL,
                   0666)

        d = db.DB(dbenv)
        d.open(self.filename, db.DB_BTREE, db.DB_CREATE | db.DB_THREAD, 0666)

        dbenv.close()  # This "close" should close the child db handle also

        del d
        try:
            import gc
        except ImportError:
            gc = None
        if gc:
            # force d.__del__ [DB_dealloc] to be called
            gc.collect()


#----------------------------------------------------------------------

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(DBEnvClosedEarlyCrash))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
