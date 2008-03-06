
#from bsddb3 import _bsddb
#from bsddb3._bsddb import *

import _bsddb
from _bsddb import *

__version__ = _bsddb.__version__

#-------------- USER INCLUDE -----------------------

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
    """DeadlockWrap(function, *_args, **_kwargs) - automatically retries
    function in case of a database deadlock.

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

import os
error = error
DB_READONLY = DB_RDONLY

def hashopen(file, flag='c', mode=0666, pgsize=None, ffactor=None, nelem=None,
            cachesize=None, lorder=None, hflags=0):
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

    env = DbEnv()
    env.open( '/tmp/foo', DB_INIT_MPOOL )
    d = Db(env)
#    d.set_flags(hflags)
    if cachesize is not None: d.set_cachesize(cachesize)
    if pgsize is not None:    d.set_pagesize(pgsize)
    if lorder is not None:    d.set_lorder(lorder)
    if ffactor is not None:   d.set_h_ffactor(ffactor)
    if nelem is not None:     d.set_h_nelem(nelem)
    d.open(file, DB_HASH, flags, mode)
    return d

#---------------------------------------------------------------------------

def btopen(file, flag='c', mode=0666,
            btflags=0, cachesize=None, maxkeypage=None, minkeypage=None,
            pgsize=None, lorder=None):
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

    env = DbEnv()
    env.open( None, DB_INIT_MPOOL )
    d = Db(env)
    if cachesize is not None: d.set_cachesize(cachesize)
    if pgsize is not None: d.set_pagesize(pgsize)
    if lorder is not None: d.set_lorder(lorder)
    d.set_flags(btflags)
    if minkeypage is not None: d.set_bt_minkey(minkeypage)
    if maxkeypage is not None: d.set_bt_maxkey(maxkeypage)
    d.open(file, DB_BTREE, flags, mode)
    return d

#---------------------------------------------------------------------------


def rnopen(file, flag='c', mode=0666,
            rnflags=0, cachesize=None, pgsize=None, lorder=None,
            rlen=None, delim=None, source=None, pad=None):
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

    env = DbEnv()
    env.open( None, DB_INIT_MPOOL )
    d = Db(env)
    if cachesize is not None: d.set_cachesize(cachesize)
    if pgsize is not None: d.set_pagesize(pgsize)
    if lorder is not None: d.set_lorder(lorder)
    d.set_flags(rnflags)
    if delim is not None: d.set_re_delim(delim)
    if rlen is not None: d.set_re_len(rlen)
    if source is not None: d.set_re_source(source)
    if pad is not None: d.set_re_pad(pad)
    d.open(file, DB_RECNO, flags, mode)
    return d

#---------------------------------------------------------------------------

