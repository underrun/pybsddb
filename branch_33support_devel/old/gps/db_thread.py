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


