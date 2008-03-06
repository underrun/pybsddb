#!/usr/bin/env python
#
#-----------------------------------------------------------------------
# Test cases for the bsddb3.db module
#-----------------------------------------------------------------------
#
# Copyright (C) 2000 by Autonomous Zone Industries
#
# March 20, 2000
#
# License:      This is free software.  You may use this software for any
#               purpose including modification/redistribution, so long as
#               this header remains intact and that you do not claim any
#               rights of ownership or authorship of this software.  This
#               software has been tested, but no warranty is expressed or
#               implied.
#
#   --  Gregory P. Smith <greg@electricrain.com>
#

from whrandom import random, randint
from threading import Thread
import time

from bsddb3 import db

# If our (Mojo Nation) unit testing module is available, use it
try:
    import RunTests
    TestHomeDir = RunTests.get_next_dir_name()
    mojo_test_flag = 0
    __use_RunTests = 1
except ImportError:
    __use_RunTests = 0
    # Directory that a test database environment will be opened in
    TestHomeDir = "foo"


class TestFailed(StandardError) : pass


def test0_version():
    assert db.version()[1:] >= (3,1,14), ("Incorrect BerkeleyDB version: %s" % db.version()[0])


########################################################################
def test1(dbname="test1.db3", testno=1, extraflags=0) :
    """a test to see that simple databases work via the python interface"""
    print "+++ test %d ..." % testno
    e = db.DbEnv()
    e.open(TestHomeDir, db.DB_CREATE | db.DB_TRUNCATE | db.DB_INIT_MPOOL | extraflags)
    d = db.Db(e)
    d.open(dbname, db.DB_BTREE, db.DB_CREATE | extraflags)

    d['hello'] = 'world!'
    d['World!'] = 'Hello, '

    if len(d) != 2 :
        raise TestFailed, "database length problem"

    keys = d.keys()
    if len(keys) != 2 :
        raise TestFailed, "incorrect number of keys in %s" % dbname
    
    if d.get('a former parrot!') != None :
        raise TestFailed, "get did not return None"

    if d.get('hello') != 'world!' or d['World!'] != 'Hello, ' :
        raise TestFailed, "bad values found in %s" % dbname
    
    del d['hello']
    d.delete('World!')

    if len(d) != 0 and len(d.keys()) != 0 :
        raise TestFailed, "Db.delete failed or length problem"

    d.close()
    e.close()
    print "--- OK"


########################################################################
def test2(dbname="test2.db3") :
    """Like test1 but with DB_THREAD specified"""
    test1(dbname=dbname, testno=2, extraflags=db.DB_THREAD)



########################################################################
#class DeadlockBreakerThread(Thread) :
#    def run(self) :
        



########################################################################
def test3(dbname="test3.db3", start=0, stop=5000) :
    """Test lots of stores, a sync and full retrieval with some deletions"""
    print "+++ testing lots of gets and puts..."
    e = db.DbEnv()
    e.open(TestHomeDir, db.DB_CREATE | db.DB_INIT_MPOOL )
    d = db.Db(e)
    d.open(dbname, db.DB_HASH, db.DB_CREATE)

    foo = {}  # a dictionary to test against
    for x in xrange(start,stop) :
        foo[x] = str( random() )
        d[str(x)] = foo[x]
    
    d.sync()

    for x in xrange(start,stop) :
        if d.get(str(x)) != foo[x] :
            raise TestFailed, "stored value %s is not %s" % (`d[str(x)]`, `foo[x]`)
        if random() > 0.666 :
            d.delete(str(x))
    
    del d
    del e
    print "--- OK"


########################################################################
def test4(dbname="test4.db3", dbtype=db.DB_BTREE, threads=3) :
    """Test several concurrent threads accessing a single Db"""
    print "+++ testing multithreaded access..."
    if dbtype == db.DB_BTREE :
        print "[BTREE]"
    elif dbtype == db.DB_HASH :
        print "[HASH]"
    else :
        raise ValueError, "this test only supports BTREE and HASH databases"

    starttime = time.time()

    e = db.DbEnv()
    e.set_lk_detect(db.DB_LOCK_DEFAULT)   # enable automatic deadlock detection
    e.open(TestHomeDir, db.DB_CREATE | db.DB_TRUNCATE | db.DB_INIT_MPOOL | db.DB_INIT_LOCK | db.DB_THREAD)
    d = db.Db(e)
    d.open(dbname, dbtype, db.DB_CREATE | db.DB_THREAD)

    def mythread(d=d, start=0, stop=5000, threadnum=None) :
        print "starting thread", threadnum
        foo = {}  # known good dictionary to compare with

        # put a bunch of items
        for x in xrange(start,stop) :
            foo[x] = str( random() )
            db.DeadlockWrap(d.put, str(x), foo[x])

        # verify our puts, deleting many of them
        for k in db.DeadlockWrap(d.keys) :
            # only check/delete keys that we inserted
            if not foo.has_key(int(k)) :
                continue
            val = db.DeadlockWrap(d.get, k)
            if val != foo[int(k)] :
                raise TestFailed, ( "stored value %s is not %s" % 
		    (`val`,`foo[int(k)]` ) )
            if random() > 0.2 :
                db.DeadlockWrap(d.delete, k)
        print "ending thread", threadnum

    tlist = []
    for x in range(0, threads) :
        tlist.append( Thread(target=mythread,
            kwargs={'d'     : d,
                    'threadnum' : x,
                    'start' : x*5000,
                    'stop'  : (x+1)*5000} ))
    
    for th in tlist :
        th.start()
    
    for th in tlist :
        th.join()

    del d
    del e

    print "time elapsed:", time.time() - starttime
    print "--- OK"


########################################################################
def test5(dbname="test5.db3", threads=3) :
    test4(dbname=dbname, dbtype=db.DB_HASH, threads=threads)
 
########################################################################
def test6(dbname="test6.db3", start=0, stop=5000) :
    """Test lots of stores, a sync and full retrieval with some deletions,
    using transactions this time.
    """
    print "+++ testing simple transactions..."
    e = db.DbEnv()
    e.open(TestHomeDir, db.DB_CREATE | db.DB_INIT_MPOOL | db.DB_INIT_LOCK | db.DB_INIT_LOG | db.DB_INIT_TXN | db.DB_THREAD)
    d = db.Db(e)
    d.open(dbname, db.DB_BTREE, db.DB_CREATE | db.DB_THREAD)

    txn = e.txn_begin()
    d.put("key", "value", txn)
    txn.abort()

    txn = e.txn_begin()
    foo = {}  # a dictionary to test against
    for x in xrange(start,stop) :
        foo[x] = str( random() )
        d.put(str(x), foo[x], txn)
    txn.commit()
    
    d.sync()

    txn = e.txn_begin()
    for x in xrange(start,stop) :
        if d.get(str(x), txn) != foo[x] :
            raise TestFailed, "stored value %s is not %s"%(`d[str(x)]`,`foo[x]`)
        if random() > 0.666 :
            d.delete(str(x), txn)
    txn.abort()
    
    del d
    del e
    print "--- OK"

########################################################################
def run() :
    test0_version()
    test1()
    test2()
    test3()
    test4()
    test5()
    test6()
    print "All tests completed successfully"


if __name__ == '__main__' :
    print "Testing bsddb3.db:"
    print " ", db.version()
    print " ", db.cvsid
    print "  db.i", db.__version__
    if __use_RunTests :
        RunTests.runTests(["bsddb3.dbtest"])
    else :
        run()
