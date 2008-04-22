"""TestCases for distributed transactions.
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

from test_all import get_new_environment_path, get_new_database_path

try:
    from bsddb3 import test_support
except ImportError:
    from test import test_support

from test_all import verbose

#----------------------------------------------------------------------

class DBReplicationManager(unittest.TestCase):
    def setUp(self) :
        self.homeDirMaster = get_new_environment_path()
        self.homeDirClient = get_new_environment_path()

        self.dbenvMaster = db.DBEnv()
        self.dbenvClient = db.DBEnv()

        self.dbenvMaster.open(self.homeDirMaster, db.DB_CREATE | db.DB_INIT_TXN
                | db.DB_INIT_LOG | db.DB_INIT_MPOOL | db.DB_INIT_LOCK |
                db.DB_INIT_REP, 0666)
        self.dbenvClient.open(self.homeDirClient, db.DB_CREATE | db.DB_INIT_TXN
                | db.DB_INIT_LOG | db.DB_INIT_MPOOL | db.DB_INIT_LOCK |
                db.DB_INIT_REP, 0666)

        self.dbenvMaster.repmgr_set_local_site("127.0.0.1",46117)
        self.dbenvClient.repmgr_set_local_site("127.0.0.1",46118)
        self.dbenvMaster.repmgr_add_remote_site("127.0.0.1",46118)
        self.dbenvClient.repmgr_add_remote_site("127.0.0.1",46117)
        self.dbenvMaster.rep_set_nsites(2)
        self.dbenvClient.rep_set_nsites(2)
        self.dbenvMaster.rep_set_priority(10)
        self.dbenvClient.rep_set_priority(0)

        self.dbenvMaster.repmgr_set_ack_policy(db.DB_REPMGR_ACKS_ALL)
        self.dbenvClient.repmgr_set_ack_policy(db.DB_REPMGR_ACKS_ALL)

        self.dbenvMaster.repmgr_start(1, db.DB_REP_MASTER);
        self.dbenvClient.repmgr_start(1, db.DB_REP_CLIENT);

        self.assertEquals(self.dbenvMaster.rep_get_nsites(),2)
        self.assertEquals(self.dbenvClient.rep_get_nsites(),2)
        self.assertEquals(self.dbenvMaster.rep_get_priority(),10)
        self.assertEquals(self.dbenvClient.rep_get_priority(),0)
        self.assertEquals(self.dbenvMaster.repmgr_get_ack_policy(),
                db.DB_REPMGR_ACKS_ALL)
        self.assertEquals(self.dbenvClient.repmgr_get_ack_policy(),
                db.DB_REPMGR_ACKS_ALL)

        #self.dbenvMaster.set_verbose(db.DB_VERB_REPLICATION, True)
        #self.dbenvMaster.set_verbose(db.DB_VERB_FILEOPS_ALL, True)
        #self.dbenvClient.set_verbose(db.DB_VERB_REPLICATION, True)
        #self.dbenvClient.set_verbose(db.DB_VERB_FILEOPS_ALL, True)

        self.dbMaster = db.DB(self.dbenvMaster)
        #self.dbClient = db.DB(self.dbenvClient)

    def tearDown(self):
        self.dbClient.close()
        self.dbMaster.close()
        self.dbenvClient.close()
        self.dbenvMaster.close()
        test_support.rmtree(self.homeDirClient)
        test_support.rmtree(self.homeDirMaster)

    def test01_basic_replication(self) :
        txn=self.dbenvMaster.txn_begin()
        self.dbMaster.open("test", db.DB_HASH, db.DB_CREATE, 0666, txn=txn)
        txn.commit()

        import time,os.path
        timeout=time.time()+10
        while (time.time()<timeout) and \
          not (os.path.exists(os.path.join(self.homeDirClient,"test"))) :
              time.sleep(0.01)

        timeout=time.time()+10
        while (time.time()<timeout) and \
                (os.path.exists(os.path.join(self.homeDirClient,"__db.rep.init"))):
                    time.sleep(0.01)

        self.dbClient=db.DB(self.dbenvClient)
        while True :
            txn=self.dbenvClient.txn_begin()
            try :
                self.dbClient.open("test", db.DB_HASH, 0, 0666, txn=txn)
            except db.DBRepHandleDeadError :
                txn.abort()
                self.dbClient.close()
                self.dbClient=db.DB(self.dbenvClient)
                continue

            txn.commit()
            break

        txn=self.dbenvMaster.txn_begin()
        self.dbMaster.put("ABC", "123", txn=txn)
        txn.commit()
        import time
        timeout=time.time()+1
        v=None
        while (time.time()<timeout) and (v==None) :
            v=self.dbClient.get("ABC")
        self.assertEquals("123", v)

        txn=self.dbenvMaster.txn_begin()
        self.dbMaster.delete("ABC", txn=txn)
        txn.commit()
        timeout=time.time()+1
        while (time.time()<timeout) and (v!=None) :
            v=self.dbClient.get("ABC")
        self.assertEquals(None, v)

#----------------------------------------------------------------------

def test_suite():
    suite = unittest.TestSuite()
    if db.version() >= (4,5) :
        suite.addTest(unittest.makeSuite(DBReplicationManager))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
