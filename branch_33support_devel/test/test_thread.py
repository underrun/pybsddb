"""
TestCases for multi-threaded access to a DB.
"""

import sys, os, string
import tempfile
import time
from pprint import pprint
from whrandom import random

try:
    from threading import Thread, currentThread
    have_threads = 1
except ImportError:
    have_threads = 0


import unittest
from test_all import verbose

from bsddb3 import db


#----------------------------------------------------------------------

class BaseThreadedTestCase(unittest.TestCase):
    dbtype       = db.DB_UNKNOWN  # must be set in derived class
    dbopenflags  = 0
    dbsetflags   = 0
    envflags     = 0


    def setUp(self):
        homeDir = os.path.join(os.path.dirname(sys.argv[0]), 'db_home')
        self.homeDir = homeDir
        try: os.mkdir(homeDir)
        except os.error: pass
        self.env = db.DBEnv()
        self.setEnvOpts()
        self.env.open(homeDir, self.envflags | db.DB_CREATE)

        self.filename = self.__class__.__name__ + '.db'
        self.d = db.DB(self.env)
        if self.dbsetflags:
            self.d.set_flags(self.dbsetflags)
        self.d.open(self.filename, self.dbtype, self.dbopenflags|db.DB_CREATE)


    def tearDown(self):
        self.d.close()
        self.env.close()
        import glob
        files = glob.glob(os.path.join(self.homeDir, '*'))
        for file in files:
            os.remove(file)


    def setEnvOpts(self):
        pass


    def makeData(self, key):
        return string.join([key] * 5, '-')


#----------------------------------------------------------------------


class ConcurrentDataStoreBase(BaseThreadedTestCase):
    dbopenflags = db.DB_THREAD
    envflags    = db.DB_THREAD | db.DB_INIT_CDB | db.DB_INIT_MPOOL
    readers     = 0 # derived class should set
    writers     = 0
    records     = 1000


    def test01_1WriterMultiReaders(self):
        if verbose:
            print '-=' * 30
            print "Running %s.test01_1WriterMultiReaders..." % self.__class__.__name__

        threads = []
        for x in range(self.writers):
            wt = Thread(target = self.writerThread,
                        args = (self.d, self.records, x),
                        name = 'writer %d' % x,
                        )#verbose = verbose)
            threads.append(wt)

        for x in range(self.readers):
            rt = Thread(target = self.readerThread,
                        args = (self.d, x),
                        name = 'reader %d' % x,
                        )#verbose = verbose)
            threads.append(rt)

        for t in threads:
            t.start()
        for t in threads:
            t.join()


    def writerThread(self, d, howMany, writerNum):
        #time.sleep(0.01 * writerNum + 0.01)
        name = currentThread().getName()
        start, stop = howMany * writerNum, howMany * (writerNum + 1) - 1
        if verbose:
            print "%s: creating records %d - %d" % (name, start, stop)

        for x in range(start, stop):
            key = '%04d' % x
            d.put(key, self.makeData(key))
            if verbose and x % 100 == 0:
                print "%s: records %d - %d finished" % (name, start, x)

        if verbose: print "%s: finished creating records" % name

##         # Each write-cursor will be exclusive, the only one that can update the DB...
##         if verbose: print "%s: deleting a few records" % name
##         c = d.cursor(flags = db.DB_WRITECURSOR)
##         for x in range(10):
##             key = int(random() * howMany) + start
##             key = '%04d' % key
##             if d.has_key(key):
##                 c.set(key)
##                 c.delete()

##         c.close()
        if verbose: print "%s: thread finished" % name


    def readerThread(self, d, readerNum):
        time.sleep(0.01 * readerNum)
        name = currentThread().getName()

        for loop in range(5):
            c = d.cursor()
            count = 0
            rec = c.first()
            while rec:
                count = count + 1
                key, data = rec
                assert self.makeData(key) == data
                rec = c.next()
            if verbose: print "%s: found %d records" % (name, count)
            c.close()
            time.sleep(0.05)

        if verbose: print "%s: thread finished" % name



class BTreeConcurrentDataStore(ConcurrentDataStoreBase):
    dbtype  = db.DB_BTREE
    writers = 2
    readers = 10
    records = 1000


class HashConcurrentDataStore(ConcurrentDataStoreBase):
    dbtype  = db.DB_HASH
    writers = 2
    readers = 10
    records = 1000

#----------------------------------------------------------------------

class SimpleThreadedBase(BaseThreadedTestCase):
    dbopenflags = db.DB_THREAD
    envflags    = db.DB_THREAD | db.DB_INIT_MPOOL | db.DB_INIT_LOCK
    readers = 5
    writers = 3
    records = 1000


    def setEnvOpts(self):
        self.env.set_lk_detect(db.DB_LOCK_DEFAULT)


    def test02_SimpleLocks(self):
        if verbose:
            print '-=' * 30
            print "Running %s.test02_SimpleLocks..." % self.__class__.__name__

        threads = []
        for x in range(self.writers):
            wt = Thread(target = self.writerThread,
                        args = (self.d, self.records, x),
                        name = 'writer %d' % x,
                        )#verbose = verbose)
            threads.append(wt)
        for x in range(self.readers):
            rt = Thread(target = self.readerThread,
                        args = (self.d, x),
                        name = 'reader %d' % x,
                        )#verbose = verbose)
            threads.append(rt)

        for t in threads:
            t.start()
        for t in threads:
            t.join()



    def writerThread(self, d, howMany, writerNum):
        name = currentThread().getName()
        start, stop = howMany * writerNum, howMany * (writerNum + 1) - 1
        if verbose:
            print "%s: creating records %d - %d" % (name, start, stop)

        # create a bunch of records
        for x in xrange(start, stop):
            key = '%04d' % x
            d.put(key, self.makeData(key))

            if verbose and x % 100 == 0:
                print "%s: records %d - %d finished" % (name, start, x)

            # do a bit or reading too
            if random() <= 0.05:
                for y in xrange(start, x):
                    key = '%04d' % x
                    data = d.get(key)
                    assert data == self.makeData(key)

        # flush them
        try:
            d.sync()
        except db.DBIncompleteError, val:
            if verbose:
                print "could not complete sync()..."

        # read them back, deleting a few
        for x in xrange(start, stop):
            key = '%04d' % x
            data = d.get(key)
            if verbose and x % 100 == 0:
                print "%s: fetched record (%s, %s)" % (name, key, data)
            assert data == self.makeData(key)
            if random() <= 0.10:
                d.delete(key)
                if verbose:
                    print "%s: deleted record %s" % (name, key)

        if verbose: print "%s: thread finished" % name


    def readerThread(self, d, readerNum):
        time.sleep(0.01 * readerNum)
        name = currentThread().getName()

        for loop in range(5):
            c = d.cursor()
            count = 0
            rec = c.first()
            while rec:
                count = count + 1
                key, data = rec
                assert self.makeData(key) == data
                rec = c.next()
            if verbose: print "%s: found %d records" % (name, count)
            c.close()
            time.sleep(0.05)

        if verbose: print "%s: thread finished" % name




class BTreeSimpleThreaded(SimpleThreadedBase):
    dbtype = db.DB_BTREE


class HashSimpleThreaded(SimpleThreadedBase):
    dbtype = db.DB_BTREE


#----------------------------------------------------------------------



class ThreadedTransactionsBase(BaseThreadedTestCase):
    dbopenflags = db.DB_THREAD
    envflags    = db.DB_THREAD | db.DB_INIT_MPOOL | db.DB_INIT_LOCK | \
                  db.DB_INIT_LOG | db.DB_INIT_TXN
    readers = 0
    writers = 0
    records = 2000


    def setEnvOpts(self):
        #self.env.set_lk_detect(db.DB_LOCK_DEFAULT)
        pass


    def test03_ThreadedTransactions(self):
        if verbose:
            print '-=' * 30
            print "Running %s.test03_ThreadedTransactions..." % self.__class__.__name__

        threads = []
        for x in range(self.writers):
            wt = Thread(target = self.writerThread,
                        args = (self.d, self.records, x),
                        name = 'writer %d' % x,
                        )#verbose = verbose)
            threads.append(wt)

        for x in range(self.readers):
            rt = Thread(target = self.readerThread,
                        args = (self.d, x),
                        name = 'reader %d' % x,
                        )#verbose = verbose)
            threads.append(rt)

        dt = Thread(target = self.deadlockThread)
        #dt.setDaemon(1)
        dt.start()

        for t in threads:
            t.start()
        for t in threads:
            t.join()

        self.doLockDetect = 0
        dt.join()


    def doWrite(self, d, name, start, stop):
        finished = 0
        while not finished:
            try:
                #txn = self.env.txn_begin()                         # will raise DBLockDeadlockError
                txn = self.env.txn_begin(None, db.DB_TXN_NOWAIT)   # will raise DBLockNotGrantedError
                for x in range(start, stop):
                    key = '%04d' % x
                    d.put(key, self.makeData(key), txn)
                    if verbose and x % 100 == 0:
                        print "%s: records %d - %d finished" % (name, start, x)
                txn.commit()
                finished = 1
            except (db.DBLockDeadlockError, db.DBLockNotGrantedError), val:
                if verbose:
                    print "%s: Aborting transaction (%s)" % (name, val[1])
                txn.abort()
                time.sleep(0.05)



    def writerThread(self, d, howMany, writerNum):
        name = currentThread().getName()
        start, stop = howMany * writerNum, howMany * (writerNum + 1) - 1
        if verbose:
            print "%s: creating records %d - %d" % (name, start, stop)

        step = 100
        for x in range(start, stop, step):
            self.doWrite(d, name, x, min(stop, x+step))

        if verbose: print "%s: finished creating records" % name
        if verbose: print "%s: deleting a few records" % name

        finished = 0
        while not finished:
            try:
                recs = []
                txn = self.env.txn_begin()
                for x in range(10):
                    key = int(random() * howMany) + start
                    key = '%04d' % key
                    data = d.get(key, None, txn, db.DB_RMW)
                    if data is not None:
                        d.delete(key, txn)
                        recs.append(key)
                txn.commit()
                finished = 1
                if verbose: print "%s: deleted records %s" % (name, recs)
            except (db.DBLockDeadlockError, db.DBLockNotGrantedError), val:
                if verbose:
                    print "%s: Aborting transaction (%s)" % (name, val[1])
                txn.abort()
                time.sleep(0.05)

        if verbose: print "%s: thread finished" % name


    def readerThread(self, d, readerNum):
        time.sleep(0.01 * readerNum + 0.05)
        name = currentThread().getName()

        for loop in range(5):
            finished = 0
            while not finished:
                try:
                    txn = self.env.txn_begin(None, db.DB_TXN_NOWAIT)
                    c = d.cursor(txn)
                    count = 0
                    rec = c.first()
                    while rec:
                        count = count + 1
                        key, data = rec
                        assert self.makeData(key) == data
                        rec = c.next()
                    if verbose: print "%s: found %d records" % (name, count)
                    c.close()
                    txn.commit()
                    finished = 1
                except (db.DBLockDeadlockError, db.DBLockNotGrantedError), val:
                    if verbose:
                        print "%s: Aborting transaction (%s)" % (name, val[1])
                    c.close()
                    txn.abort()
                    time.sleep(0.05)

            time.sleep(0.05)

        if verbose: print "%s: thread finished" % name


    def deadlockThread(self):
        self.doLockDetect = 1
        while self.doLockDetect:
            time.sleep(0.5)
            try:
                aborted = self.env.lock_detect(db.DB_LOCK_RANDOM, db.DB_LOCK_CONFLICT)
                if verbose and aborted:
                    print "Aborted %d deadlocked transaction(s)" % aborted
            except db.DBError:
                pass



class BTreeThreadedTransactions(ThreadedTransactionsBase):
    dbtype = db.DB_BTREE
    writers = 3
    readers = 5
    records = 2000

class HashThreadedTransactions(ThreadedTransactionsBase):
    dbtype = db.DB_HASH
    writers = 3
    readers = 5
    records = 2000


#----------------------------------------------------------------------

def suite():
    theSuite = unittest.TestSuite()

    if have_threads:
        theSuite.addTest(unittest.makeSuite(BTreeConcurrentDataStore))
        theSuite.addTest(unittest.makeSuite(HashConcurrentDataStore))
        theSuite.addTest(unittest.makeSuite(BTreeSimpleThreaded))
        theSuite.addTest(unittest.makeSuite(HashSimpleThreaded))
        theSuite.addTest(unittest.makeSuite(BTreeThreadedTransactions))
        theSuite.addTest(unittest.makeSuite(HashThreadedTransactions))
    else:
        print "Threads not available, skipping thread tests."

    return theSuite


if __name__ == '__main__':
    unittest.main( defaultTest='suite' )
