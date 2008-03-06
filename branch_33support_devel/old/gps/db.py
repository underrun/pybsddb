# This file was created automatically by SWIG.
import dbc
import new
class Txn:
    def __init__(self,*args,**kwargs):
        self.this = apply(dbc.new_Txn,args,kwargs)
        self.thisown = 1

    def __repr__(self):
        return "<C Txn instance at %s>" % (self.this,)
class TxnPtr(Txn):
    def __init__(self,this):
        self.this = this
        self.thisown = 0
        self.__class__ = Txn


Txn.abort = new.instancemethod(dbc.Txn_abort, None, Txn)
Txn.prepare = new.instancemethod(dbc.Txn_prepare, None, Txn)
Txn.commit = new.instancemethod(dbc.Txn_commit, None, Txn)

class DbEnv:
    def __init__(self,*args,**kwargs):
        self.this = apply(dbc.new_DbEnv,args,kwargs)
        self.thisown = 1

    def __del__(self,dbc=dbc):
        if self.thisown == 1 :
            dbc.delete_DbEnv(self)
    def txn_begin(*args, **kwargs):
        val = apply(dbc.DbEnv_txn_begin,args, kwargs)
        if val: val = TxnPtr(val) ; val.thisown = 1
        return val
    def __repr__(self):
        return "<C DbEnv instance at %s>" % (self.this,)
class DbEnvPtr(DbEnv):
    def __init__(self,this):
        self.this = this
        self.thisown = 0
        self.__class__ = DbEnv


DbEnv.open = new.instancemethod(dbc.DbEnv_open, None, DbEnv)
DbEnv.close = new.instancemethod(dbc.DbEnv_close, None, DbEnv)
DbEnv.set_data_dir = new.instancemethod(dbc.DbEnv_set_data_dir, None, DbEnv)
DbEnv.set_lg_dir = new.instancemethod(dbc.DbEnv_set_lg_dir, None, DbEnv)
DbEnv.set_tmp_dir = new.instancemethod(dbc.DbEnv_set_tmp_dir, None, DbEnv)
DbEnv.set_cachesize = new.instancemethod(dbc.DbEnv_set_cachesize, None, DbEnv)
DbEnv.set_lg_bsize = new.instancemethod(dbc.DbEnv_set_lg_bsize, None, DbEnv)
DbEnv.set_lg_max = new.instancemethod(dbc.DbEnv_set_lg_max, None, DbEnv)
DbEnv.set_lk_detect = new.instancemethod(dbc.DbEnv_set_lk_detect, None, DbEnv)
DbEnv.set_mp_mmapsize = new.instancemethod(dbc.DbEnv_set_mp_mmapsize, None, DbEnv)
DbEnv.beginAutoTrans = new.instancemethod(dbc.DbEnv_beginAutoTrans, None, DbEnv)
DbEnv.abortAutoTrans = new.instancemethod(dbc.DbEnv_abortAutoTrans, None, DbEnv)
DbEnv.prepareAutoTrans = new.instancemethod(dbc.DbEnv_prepareAutoTrans, None, DbEnv)
DbEnv.commitAutoTrans = new.instancemethod(dbc.DbEnv_commitAutoTrans, None, DbEnv)
DbEnv.txn_checkpoint = new.instancemethod(dbc.DbEnv_txn_checkpoint, None, DbEnv)

class Dbc:
    def __init__(self,this):
        self.this = this

    def __del__(self,dbc=dbc):
        if self.thisown == 1 :
            dbc.delete_Dbc(self)
    def __repr__(self):
        return "<C Dbc instance at %s>" % (self.this,)
class DbcPtr(Dbc):
    def __init__(self,this):
        self.this = this
        self.thisown = 0
        self.__class__ = Dbc


Dbc.close = new.instancemethod(dbc.Dbc_close, None, Dbc)
Dbc.delete = new.instancemethod(dbc.Dbc_delete, None, Dbc)
Dbc.get = new.instancemethod(dbc.Dbc_get, None, Dbc)
Dbc.first = new.instancemethod(dbc.Dbc_first, None, Dbc)
Dbc.last = new.instancemethod(dbc.Dbc_last, None, Dbc)
Dbc.next = new.instancemethod(dbc.Dbc_next, None, Dbc)
Dbc.prev = new.instancemethod(dbc.Dbc_prev, None, Dbc)
Dbc.current = new.instancemethod(dbc.Dbc_current, None, Dbc)
Dbc.set = new.instancemethod(dbc.Dbc_set, None, Dbc)
Dbc.setRange = new.instancemethod(dbc.Dbc_setRange, None, Dbc)
Dbc.setRecno = new.instancemethod(dbc.Dbc_setRecno, None, Dbc)
Dbc.getRecno = new.instancemethod(dbc.Dbc_getRecno, None, Dbc)
Dbc.put = new.instancemethod(dbc.Dbc_put, None, Dbc)
Dbc.count = new.instancemethod(dbc.Dbc_count, None, Dbc)

class Db:
    def __init__(self,*args,**kwargs):
        self.this = apply(dbc.new_Db,args,kwargs)
        self.thisown = 1

    def __del__(self,dbc=dbc):
        if self.thisown == 1 :
            dbc.delete_Db(self)
    def cursor(*args, **kwargs):
        val = apply(dbc.Db_cursor,args, kwargs)
        if val: val = DbcPtr(val) ; val.thisown = 1
        return val
    def __repr__(self):
        return "<C Db instance at %s>" % (self.this,)
class DbPtr(Db):
    def __init__(self,this):
        self.this = this
        self.thisown = 0
        self.__class__ = Db


Db.set_cachesize = new.instancemethod(dbc.Db_set_cachesize, None, Db)
Db.set_lorder = new.instancemethod(dbc.Db_set_lorder, None, Db)
Db.set_pagesize = new.instancemethod(dbc.Db_set_pagesize, None, Db)
Db.set_bt_minkey = new.instancemethod(dbc.Db_set_bt_minkey, None, Db)
Db.set_h_ffactor = new.instancemethod(dbc.Db_set_h_ffactor, None, Db)
Db.set_h_nelem = new.instancemethod(dbc.Db_set_h_nelem, None, Db)
Db.set_re_delim = new.instancemethod(dbc.Db_set_re_delim, None, Db)
Db.set_re_len = new.instancemethod(dbc.Db_set_re_len, None, Db)
Db.set_re_pad = new.instancemethod(dbc.Db_set_re_pad, None, Db)
Db.set_re_source = new.instancemethod(dbc.Db_set_re_source, None, Db)
Db.set_flags = new.instancemethod(dbc.Db_set_flags, None, Db)
Db.open = new.instancemethod(dbc.Db_open, None, Db)
Db.upgrade = new.instancemethod(dbc.Db_upgrade, None, Db)
Db.type = new.instancemethod(dbc.Db_type, None, Db)
Db.close = new.instancemethod(dbc.Db_close, None, Db)
Db.delete = new.instancemethod(dbc.Db_delete, None, Db)
Db.get = new.instancemethod(dbc.Db_get, None, Db)
Db.getRec = new.instancemethod(dbc.Db_getRec, None, Db)
Db.fd = new.instancemethod(dbc.Db_fd, None, Db)
Db.put = new.instancemethod(dbc.Db_put, None, Db)
Db.sync = new.instancemethod(dbc.Db_sync, None, Db)
Db.__len__ = new.instancemethod(dbc.Db___len__, None, Db)
Db.__getitem__ = new.instancemethod(dbc.Db___getitem__, None, Db)
Db.__setitem__ = new.instancemethod(dbc.Db___setitem__, None, Db)
Db.__delitem__ = new.instancemethod(dbc.Db___delitem__, None, Db)
Db.keys = new.instancemethod(dbc.Db_keys, None, Db)
Db.has_key = new.instancemethod(dbc.Db_has_key, None, Db)



#-------------- FUNCTION WRAPPERS ------------------

version = dbc.version



#-------------- VARIABLE WRAPPERS ------------------

__version__ = dbc.__version__
cvsid = dbc.cvsid
DB_VERSION_MAJOR = dbc.DB_VERSION_MAJOR
DB_VERSION_MINOR = dbc.DB_VERSION_MINOR
DB_VERSION_PATCH = dbc.DB_VERSION_PATCH
DB_VERSION_STRING = dbc.DB_VERSION_STRING
DB_MAX_PAGES = dbc.DB_MAX_PAGES
DB_MAX_RECORDS = dbc.DB_MAX_RECORDS
DB_DBT_PARTIAL = dbc.DB_DBT_PARTIAL
DB_XA_CREATE = dbc.DB_XA_CREATE
DB_CREATE = dbc.DB_CREATE
DB_NOMMAP = dbc.DB_NOMMAP
DB_THREAD = dbc.DB_THREAD
DB_INIT_CDB = dbc.DB_INIT_CDB
DB_INIT_LOCK = dbc.DB_INIT_LOCK
DB_INIT_LOG = dbc.DB_INIT_LOG
DB_INIT_MPOOL = dbc.DB_INIT_MPOOL
DB_INIT_TXN = dbc.DB_INIT_TXN
DB_RECOVER = dbc.DB_RECOVER
DB_RECOVER_FATAL = dbc.DB_RECOVER_FATAL
DB_TXN_NOSYNC = dbc.DB_TXN_NOSYNC
DB_USE_ENVIRON = dbc.DB_USE_ENVIRON
DB_USE_ENVIRON_ROOT = dbc.DB_USE_ENVIRON_ROOT
DB_LOCKDOWN = dbc.DB_LOCKDOWN
DB_PRIVATE = dbc.DB_PRIVATE
DB_TXN_SYNC = dbc.DB_TXN_SYNC
DB_TXN_NOWAIT = dbc.DB_TXN_NOWAIT
DB_FORCE = dbc.DB_FORCE
DB_EXCL = dbc.DB_EXCL
DB_RDONLY = dbc.DB_RDONLY
DB_TRUNCATE = dbc.DB_TRUNCATE
DB_LOCK_NORUN = dbc.DB_LOCK_NORUN
DB_LOCK_DEFAULT = dbc.DB_LOCK_DEFAULT
DB_LOCK_OLDEST = dbc.DB_LOCK_OLDEST
DB_LOCK_RANDOM = dbc.DB_LOCK_RANDOM
DB_LOCK_YOUNGEST = dbc.DB_LOCK_YOUNGEST
DB_BTREE = dbc.DB_BTREE
DB_HASH = dbc.DB_HASH
DB_RECNO = dbc.DB_RECNO
DB_UNKNOWN = dbc.DB_UNKNOWN
DB_DUP = dbc.DB_DUP
DB_DUPSORT = dbc.DB_DUPSORT
DB_RECNUM = dbc.DB_RECNUM
DB_RENUMBER = dbc.DB_RENUMBER
DB_REVSPLITOFF = dbc.DB_REVSPLITOFF
DB_SNAPSHOT = dbc.DB_SNAPSHOT
DB_AFTER = dbc.DB_AFTER
DB_APPEND = dbc.DB_APPEND
DB_BEFORE = dbc.DB_BEFORE
DB_CHECKPOINT = dbc.DB_CHECKPOINT
DB_CONSUME = dbc.DB_CONSUME
DB_CURLSN = dbc.DB_CURLSN
DB_CURRENT = dbc.DB_CURRENT
DB_FIRST = dbc.DB_FIRST
DB_FLUSH = dbc.DB_FLUSH
DB_GET_BOTH = dbc.DB_GET_BOTH
DB_GET_RECNO = dbc.DB_GET_RECNO
DB_JOIN_ITEM = dbc.DB_JOIN_ITEM
DB_KEYFIRST = dbc.DB_KEYFIRST
DB_KEYLAST = dbc.DB_KEYLAST
DB_LAST = dbc.DB_LAST
DB_NEXT = dbc.DB_NEXT
DB_NEXT_DUP = dbc.DB_NEXT_DUP
DB_NEXT_NODUP = dbc.DB_NEXT_NODUP
DB_NOOVERWRITE = dbc.DB_NOOVERWRITE
DB_NOSYNC = dbc.DB_NOSYNC
DB_POSITION = dbc.DB_POSITION
DB_PREV = dbc.DB_PREV
DB_RECORDCOUNT = dbc.DB_RECORDCOUNT
DB_SET = dbc.DB_SET
DB_SET_RANGE = dbc.DB_SET_RANGE
DB_SET_RECNO = dbc.DB_SET_RECNO
DB_WRITECURSOR = dbc.DB_WRITECURSOR
DB_OPFLAGS_MASK = dbc.DB_OPFLAGS_MASK
DB_RMW = dbc.DB_RMW
DB_INCOMPLETE = dbc.DB_INCOMPLETE
DB_KEYEMPTY = dbc.DB_KEYEMPTY
DB_KEYEXIST = dbc.DB_KEYEXIST
DB_LOCK_DEADLOCK = dbc.DB_LOCK_DEADLOCK
DB_LOCK_NOTGRANTED = dbc.DB_LOCK_NOTGRANTED
DB_NOTFOUND = dbc.DB_NOTFOUND
DB_OLD_VERSION = dbc.DB_OLD_VERSION
DB_RUNRECOVERY = dbc.DB_RUNRECOVERY


#-------------- USER INCLUDE -----------------------


# This is here because python2.0 by default seems to link itself
# against an older berkeleydb 2.x library on my debian system.  This
# prevents the symbols defined in dbc.so itself from being used and
# causes the library to misbehave in unpredictable ways.
if version()[1:] < (3, 1, 14):
    raise RuntimeError, "BerkeleyDB 3.1.14 or later required; found version `%s' on import.  Perhaps your python binary or an already loaded module was linked against an older version?" % version()[0]

#------------------------------------------------------------------------
# This file is appended to the SWIG generated shadow file.  It
# provides a conventient Db class with a DeadLockWrap method which can
# be used when making Db function calls to automatically handle
# potential DB_LOCK_DEADLOCK exceptions.
#
# In my performance tests, using this (as in dbtest.py test4) is
# slightly slower than simply compiling db.i with MYDB_THREAD
# undefined to prevent multithreading support in the C module.
# Using NoDeadlockDb also prevent deadlocks from mutliple processes
# accessing the same database.
#
# Copyright (C) 2000 Autonomous Zone Industries
#
# License:      This is free software.  You may use this software for any
#               purpose including modification/redistribution, so long as
#               this header remains intact and that you do not claim any
#               rights of ownership or authorship of this software.  This
#               software has been tested, but no warranty is expressed or
#               implied.
#
# Author: Gregory P. Smith <greg@electricrain.com>
#------------------------------------------------------------------------


#
# import the time.sleep function in a namespace safe way to allow
# "from bsddb3.db import *"
#
from time import sleep
_sleep = sleep
del sleep


deadlock_MinSleepTime = 1.0/64  # always sleep at least N seconds between retrys
deadlock_MaxSleepTime = 1.0     # never sleep more than N seconds between retrys

def DeadlockWrap(function, *_args, **_kwargs):
    """DeadlockWrap(function, *_args, **_kwards) - automatically retrys
    function incase of a database deadlock.

    This is a DeadlockWrapper method which Db calls can be made using to
    preform infinite retrys with sleeps inbetween when a DB_LOCK_DEADLOCK
    exception is raised in a database call:

        d = Db(...)
        d.open(...)
        DeadlockWrap(d.put, "foo", data="bar")  # set key "foo" to "bar"
    """
    sleeptime = deadlock_MinSleepTime
    while (1) :
        try:
            return apply(function, _args, _kwargs)
        except error, e:
            if (e[0] != DB_LOCK_DEADLOCK) :
                raise
            else :
                _sleep(sleeptime)
                # exponential backoff in the sleep time
                sleeptime = sleeptime * 2
                if sleeptime > deadlock_MaxSleepTime :
                    sleeptime = deadlock_MaxSleepTime


#------------------------------------------------------------------------
#               Copyright (c) 1997 by Total Control Software
#                         All Rights Reserved
#------------------------------------------------------------------------
#
# Module Name:  db_compat.py
#
# Description:  This file is appended to the SWIG generated shadow file.
#               It contains a few functions to provide some backwards
#               compatibility with the old bsddb module.
#
# Creation Date:    12/17/97 7:50:28PM
#
# License:      This is free software.  You may use this software for any
#               purpose including modification/redistribution, so long as
#               this header remains intact and that you do not claim any
#               rights of ownership or authorship of this software.  This
#               software has been tested, but no warranty is expressed or
#               implied.
#
# Copyright (C) 2000 Autonomous Zone Industries
#
# The above license applies.  I just ported this code to use Berkeley
# DB 3.0.x instead of 2.7.x.  The code below here (from db_compat.py)
# has not been tested by me!
#   --  Gregory P. Smith <greg@electricrain.com>
#
#
#------------------------------------------------------------------------

error = dbc.error
DB_READONLY = DB_RDONLY

def hashopen(file, flag='c', mode=0666, pgsize=0, ffactor=0, nelem=0,
            cachesize=0, lorder=0, hflags=0):
    if flag == 'r':
        flags = DB_READONLY
    elif flag == 'rw':
        flags = 0
    elif flag == 'w':
        flags =  DB_CREATE
    elif flag == 'c':
        flags =  DB_CREATE
    elif flag == 'n':
        flags = DB_TRUNCATE
    else:
        raise error, "flags should be one of 'r', 'w', 'c' or 'n'"

    d = DB()
    d.set_cachesize(cachesize)
    d.set_pagesize(pgsize)
    d.set_lorder(lorder)
    d.set_flags(hflags)
    d.set_h_ffactor(ffactor)
    d.set_h_nelem(nelem)
    d.open(file, DB_HASH, flags, mode)
    return d

#---------------------------------------------------------------------------

def btopen(file, flag='c', mode=0666,
            btflags=0, cachesize=0, maxkeypage=0, minkeypage=0,
            pgsize=0, lorder=0):
    if flag == 'r':
        flags = DB_READONLY
    elif flag == 'rw':
        flags = 0
    elif flag == 'w':
        flags =  DB_CREATE
    elif flag == 'c':
        flags =  DB_CREATE
    elif flag == 'n':
        flags = DB_TRUNCATE
    else:
        raise error, "flags should be one of 'r', 'w', 'c' or 'n'"

    d = DB()
    d.set_cachesize(cachesize)
    d.set_pagesize(pgsize)
    d.set_lorder(lorder)
    d.set_flags(btflags)
    d.set_bt_minkey(minkeypage)
    d.set_bt_maxkey(maxkeypage)
    d.open(file, DB_BTREE, flags, mode)
    return d

#---------------------------------------------------------------------------


def rnopen(file, flag='c', mode=0666,
            rnflags=0, cachesize=0, pgsize=0, lorder=0,
            rlen=0, delim=0, source=0, pad=0):
    if flag == 'r':
        flags = DB_READONLY
    elif flag == 'rw':
        flags = 0
    elif flag == 'w':
        flags =  DB_CREATE
    elif flag == 'c':
        flags =  DB_CREATE
    elif flag == 'n':
        flags = DB_TRUNCATE
    else:
        raise error, "flags should be one of 'r', 'w', 'c' or 'n'"

    d = DB()
    d.set_cachesize(cachesize)
    d.set_pagesize(pgsize)
    d.set_lorder(lorder)
    d.set_flags(rnflags)
    d.set_re_delim(delim)
    d.set_re_len(rlen)
    d.set_re_source(source)
    d.set_re_pad(pad)
    d.open(file, DB_RECNO, flags, mode)
    return d

#---------------------------------------------------------------------------

