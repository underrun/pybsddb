"""TestCases for distributed transactions.
"""

import os
import time
import unittest

try:
    # For Pythons w/distutils pybsddb
    from bsddb3 import db
except ImportError:
    # For Python 2.3
    from bsddb import db

from test_all import have_threads, get_new_environment_path, get_new_database_path

try:
    from bsddb3 import test_support
except ImportError:
    from test import test_support

from test_all import verbose

#----------------------------------------------------------------------

class DBReplicationManager(unittest.TestCase):
    import sys
    if sys.version_info[:3] < (2, 4, 0):
        def assertTrue(self, expr, msg=None):
            self.failUnless(expr,msg=msg)

    def setUp(self) :
        self.homeDirMaster = get_new_environment_path()
        self.homeDirClient = get_new_environment_path()

        self.dbenvMaster = db.DBEnv()
        self.dbenvClient = db.DBEnv()

        # Must use "DB_THREAD" because the Replication Manager will
        # be executed in other threads but will use the same environment.
        # http://forums.oracle.com/forums/thread.jspa?threadID=645788&tstart=0
        self.dbenvMaster.open(self.homeDirMaster, db.DB_CREATE | db.DB_INIT_TXN
                | db.DB_INIT_LOG | db.DB_INIT_MPOOL | db.DB_INIT_LOCK |
                db.DB_INIT_REP | db.DB_RECOVER | db.DB_THREAD, 0666)
        self.dbenvClient.open(self.homeDirClient, db.DB_CREATE | db.DB_INIT_TXN
                | db.DB_INIT_LOG | db.DB_INIT_MPOOL | db.DB_INIT_LOCK |
                db.DB_INIT_REP | db.DB_RECOVER | db.DB_THREAD, 0666)

        self.confirmed_master=self.client_startupdone=False
        def confirmed_master(a,b,c) :
            if b==db.DB_EVENT_REP_MASTER :
                self.confirmed_master=True

        def client_startupdone(a,b,c) :
            if b==db.DB_EVENT_REP_STARTUPDONE :
                self.client_startupdone=True

        self.dbenvMaster.set_event_notify(confirmed_master)
        self.dbenvClient.set_event_notify(client_startupdone)

        master_port = test_support.find_unused_port()
        self.dbenvMaster.repmgr_set_local_site("127.0.0.1", master_port)
        client_port = test_support.find_unused_port()
        self.dbenvClient.repmgr_set_local_site("127.0.0.1", client_port)
        self.dbenvMaster.repmgr_add_remote_site("127.0.0.1", client_port)
        self.dbenvClient.repmgr_add_remote_site("127.0.0.1", master_port)
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

        self.dbMaster = self.dbClient = None

        # The timeout is necessary in BDB 4.5, since DB_EVENT_REP_STARTUPDONE
        # is not generated if the master has no new transactions.
        # This is solved in BDB 4.6 (#15542).
        timeout = time.time()+2
        while (time.time()<timeout) and not (self.confirmed_master and self.client_startupdone) :
            time.sleep(0.02)
        if db.version() >= (4,6) :
            self.assertTrue(time.time()<timeout)
        else :
            self.assertTrue(time.time()>=timeout)

        d = self.dbenvMaster.repmgr_site_list()
        self.assertEquals(len(d), 1)
        self.assertEquals(d[0][0], "127.0.0.1")
        self.assertEquals(d[0][1], client_port)
        self.assertTrue((d[0][2]==db.DB_REPMGR_CONNECTED) or \
                (d[0][2]==db.DB_REPMGR_DISCONNECTED))

        d = self.dbenvClient.repmgr_site_list()
        self.assertEquals(len(d), 1)
        self.assertEquals(d[0][0], "127.0.0.1")
        self.assertEquals(d[0][1], master_port)
        self.assertTrue((d[0][2]==db.DB_REPMGR_CONNECTED) or \
                (d[0][2]==db.DB_REPMGR_DISCONNECTED))

        if db.version() >= (4,6) :
            d = self.dbenvMaster.repmgr_stat(flags=db.DB_STAT_CLEAR);
            self.assertTrue("msgs_queued" in d)

    def tearDown(self):
        if self.dbClient :
            self.dbClient.close()
        if self.dbMaster :
            self.dbMaster.close()
        self.dbenvClient.close()
        self.dbenvMaster.close()
        test_support.rmtree(self.homeDirClient)
        test_support.rmtree(self.homeDirMaster)

    def test01_basic_replication(self) :
        self.dbMaster=db.DB(self.dbenvMaster)
        txn=self.dbenvMaster.txn_begin()
        self.dbMaster.open("test", db.DB_HASH, db.DB_CREATE, 0666, txn=txn)
        txn.commit()

        import time,os.path
        timeout=time.time()+10
        while (time.time()<timeout) and \
          not (os.path.exists(os.path.join(self.homeDirClient,"test"))) :
            time.sleep(0.01)

        self.dbClient=db.DB(self.dbenvClient)
        while True :
            txn=self.dbenvClient.txn_begin()
            try :
                self.dbClient.open("test", db.DB_HASH, flags=db.DB_RDONLY,
                        mode=0666, txn=txn)
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
            txn=self.dbenvClient.txn_begin()
            v=self.dbClient.get("ABC", txn=txn)
            txn.commit()
        self.assertEquals("123", v)

        txn=self.dbenvMaster.txn_begin()
        self.dbMaster.delete("ABC", txn=txn)
        txn.commit()
        timeout=time.time()+1
        while (time.time()<timeout) and (v!=None) :
            txn=self.dbenvClient.txn_begin()
            v=self.dbClient.get("ABC", txn=txn)
            txn.commit()
        self.assertEquals(None, v)

class DBBaseReplication(unittest.TestCase):
    import sys
    if sys.version_info[:3] < (2, 4, 0):
        def assertTrue(self, expr, msg=None):
            self.failUnless(expr,msg=msg)

    def setUp(self) :
        self.homeDirMaster = get_new_environment_path()
        self.homeDirClient = get_new_environment_path()

        self.dbenvMaster = db.DBEnv()
        self.dbenvClient = db.DBEnv()

        self.dbenvMaster.open(self.homeDirMaster, db.DB_CREATE | db.DB_INIT_TXN
                | db.DB_INIT_LOG | db.DB_INIT_MPOOL | db.DB_INIT_LOCK |
                db.DB_INIT_REP | db.DB_RECOVER | db.DB_THREAD, 0666)
        self.dbenvClient.open(self.homeDirClient, db.DB_CREATE | db.DB_INIT_TXN
                | db.DB_INIT_LOG | db.DB_INIT_MPOOL | db.DB_INIT_LOCK |
                db.DB_INIT_REP | db.DB_RECOVER | db.DB_THREAD, 0666)

        self.confirmed_master=self.client_startupdone=False
        def confirmed_master(a,b,c) :
            if b==db.DB_EVENT_REP_MASTER :
                self.confirmed_master=True

        def client_startupdone(a,b,c) :
            if b==db.DB_EVENT_REP_STARTUPDONE :
                self.client_startupdone=True

        self.dbenvMaster.set_event_notify(confirmed_master)
        self.dbenvClient.set_event_notify(client_startupdone)

        import Queue
        self.m2c = Queue.Queue()
        self.c2m = Queue.Queue()

        # There are only two nodes, so we don't need to
        # do any routing decision
        def m2c(dbenv, control, rec, lsnp, envid, flags) :
            self.m2c.put((control, rec, envid))

        def c2m(dbenv, control, rec, lsnp, envid, flags) :
            self.c2m.put((control, rec, envid))

        self.dbenvMaster.rep_set_transport(0,m2c)
        self.dbenvClient.rep_set_transport(1,c2m)

        #self.dbenvMaster.set_verbose(db.DB_VERB_REPLICATION, True)
        #self.dbenvMaster.set_verbose(db.DB_VERB_FILEOPS_ALL, True)
        #self.dbenvClient.set_verbose(db.DB_VERB_REPLICATION, True)
        #self.dbenvClient.set_verbose(db.DB_VERB_FILEOPS_ALL, True)

        self.dbenvMaster.rep_start(flags=db.DB_REP_MASTER)
        self.dbenvClient.rep_start(flags=db.DB_REP_CLIENT)

        def thread_do(env, q) :
            while True :
                v=q.get()
                if v == None : return
                env.rep_process_message(v[0],v[1],v[2])

        def thread_master() :
            return thread_do(self.dbenvMaster, self.c2m)

        def thread_client() :
            return thread_do(self.dbenvClient, self.m2c)

        from threading import Thread
        t_m=Thread(target=thread_master)
        t_m.setDaemon(True)
        t_m.start()
        t_c=Thread(target=thread_client)
        t_c.setDaemon(True)
        t_c.start()

        self.t_m = t_m
        self.t_c = t_c

        self.dbMaster = self.dbClient = None

        # The timeout is necessary in BDB 4.5, since DB_EVENT_REP_STARTUPDONE
        # is not generated if the master has no new transactions.
        # This is solved in BDB 4.6 (#15542).
        import time
        timeout = time.time()+2
        while (time.time()<timeout) and not (self.confirmed_master and self.client_startupdone) :
            time.sleep(0.02)
        if db.version() >= (4,6) :
            self.assertTrue(time.time()<timeout)
        else :
            self.assertTrue(time.time()>=timeout)

    def tearDown(self):
        if self.dbClient :
            self.dbClient.close()
        if self.dbMaster :
            self.dbMaster.close()
        self.m2c.put(None)
        self.c2m.put(None)
        self.t_m.join()
        self.t_c.join()
        self.dbenvClient.close()
        self.dbenvMaster.close()
        test_support.rmtree(self.homeDirClient)
        test_support.rmtree(self.homeDirMaster)

    def test01_basic_replication(self) :
        self.dbMaster=db.DB(self.dbenvMaster)
        txn=self.dbenvMaster.txn_begin()
        self.dbMaster.open("test", db.DB_HASH, db.DB_CREATE, 0666, txn=txn)
        txn.commit()

        import time,os.path
        timeout=time.time()+10
        while (time.time()<timeout) and \
          not (os.path.exists(os.path.join(self.homeDirClient,"test"))) :
            time.sleep(0.01)

        self.dbClient=db.DB(self.dbenvClient)
        while True :
            txn=self.dbenvClient.txn_begin()
            try :
                self.dbClient.open("test", db.DB_HASH, flags=db.DB_RDONLY,
                        mode=0666, txn=txn)
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
            txn=self.dbenvClient.txn_begin()
            v=self.dbClient.get("ABC", txn=txn)
            txn.commit()
        self.assertEquals("123", v)

        txn=self.dbenvMaster.txn_begin()
        self.dbMaster.delete("ABC", txn=txn)
        txn.commit()
        timeout=time.time()+1
        while (time.time()<timeout) and (v!=None) :
            txn=self.dbenvClient.txn_begin()
            v=self.dbClient.get("ABC", txn=txn)
            txn.commit()
        self.assertEquals(None, v)

#----------------------------------------------------------------------

def test_suite():
    suite = unittest.TestSuite()
    if db.version() >= (4,5) :
        dbenv = db.DBEnv()
        try :
            dbenv.repmgr_get_ack_policy()
            ReplicationManager_available=True
        except :
            ReplicationManager_available=False
        dbenv.close()
        del dbenv
        if ReplicationManager_available :
            suite.addTest(unittest.makeSuite(DBReplicationManager))

        if have_threads :
            suite.addTest(unittest.makeSuite(DBBaseReplication))

    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

