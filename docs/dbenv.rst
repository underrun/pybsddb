.. $Id$

=====
DBEnv
=====

DBEnv Attributes
----------------

.. function:: DBEnv(flags=0)

   database home directory (read-only)

DBEnv Methods
-------------

.. function:: DBEnv(flags=0)

   Constructor.
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/env_class.html>`__

.. function:: close(flags=0)

   Close the database environment, freeing resources.
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/env_close.html>`__

.. function:: open(homedir, flags=0, mode=0660)

   Prepare the database environment for use.
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/env_open.html>`__

.. function:: remove(homedir, flags=0)

   Remove a database environment.
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/env_remove.html>`__

.. function:: set_cachesize(gbytes, bytes, ncache=0)

   Set the size of the shared memory buffer pool
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/env_set_cachesize.html>`__

.. function:: set_data_dir(dir)

   Set the environment data directory
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/env_set_data_dir.html>`__

.. function:: set_flags(flags, onoff)

   Set additional flags for the DBEnv. The onoff parameter specifes if
   the flag is set or cleared.
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/env_set_flags.html>`__

.. function:: set_tmp_dir(dir)

   Set the directory to be used for temporary files
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/env_set_tmp_dir.html>`__

.. function:: set_get_returns_none(flag)

   By default when DB.get or DBCursor.get, get_both, first, last, next
   or prev encounter a DB_NOTFOUND error they return None instead of
   raising DBNotFoundError. This behaviour emulates Python dictionaries
   and is convenient for looping.

   You can use this method to toggle that behaviour for all of the
   aformentioned methods or extend it to also apply to the DBCursor.set,
   set_both, set_range, and set_recno methods. Supported values of
   flag:

   - **0** all DB and DBCursor get and set methods will raise a
     DBNotFoundError rather than returning None.

   - **1** *Default in module version <4.2.4*  The DB.get and
     DBCursor.get, get_both, first, last, next and prev methods return
     None.

   - **2** *Default in module version >=4.2.4* Extends the behaviour of
     **1** to the DBCursor set, set_both, set_range and set_recno
     methods.

   The default of returning None makes it easy to do things like this
   without having to catch DBNotFoundError (KeyError)::

                    data = mydb.get(key)
                    if data:
                        doSomething(data)

   or this::

                    rec = cursor.first()
                    while rec:
                        print rec
                        rec = cursor.next()

   Making the cursor set methods return None is useful in order to do
   this::

                    rec = mydb.set()
                    while rec:
                        key, val = rec
                        doSomething(key, val)
                        rec = mydb.next()

   The downside to this it that it is inconsistent with the rest of the
   package and noticeably diverges from the Oracle Berkeley DB API. If
   you prefer to have the get and set methods raise an exception when a
   key is not found, use this method to tell them to do so.

   Calling this method on a DBEnv object will set the default for all
   DB's later created within that environment. Calling it on a DB
   object sets the behaviour for that DB only.

   The previous setting is returned.

.. function:: set_lg_bsize(size)

   Set the size of the in-memory log buffer, in bytes.
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/env_set_lg_bsize.html>`__

.. function:: set_lg_dir(dir)

   The path of a directory to be used as the location of logging files.
   Log files created by the Log Manager subsystem will be created in
   this directory.
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/env_set_lg_dir.html>`__

.. function:: set_lg_max(size)

   Set the maximum size of a single file in the log, in bytes.
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/env_set_lg_max.html>`__

.. function:: set_lg_regionmax(size)

   Set the maximum size of a single region in the log, in bytes.
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/env_set_lg_regionmax.html>`__

.. function:: set_lk_detect(mode)

   Set the automatic deadlock detection mode
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/env_set_lk_detect.html>`__

.. function:: set_lk_max(max)

   Set the maximum number of locks. (This method is deprecated.)
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/env_set_lk_max.html>`__

.. function:: set_lk_max_locks(max)

   Set the maximum number of locks supported by the Berkeley DB lock
   subsystem.
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/env_set_lk_max_locks.html>`__

.. function:: set_lk_max_lockers(max)

   Set the maximum number of simultaneous locking entities supported by
   the Berkeley DB lock subsystem.
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/env_set_lk_max_lockers.html>`__

.. function:: set_lk_max_objects(max)

   Set the maximum number of simultaneously locked objects supported by
   the Berkeley DB lock subsystem.
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/env_set_lk_max_lockers.html>`__

.. function:: set_mp_mmapsize(size)

   Files that are opened read-only in the memory pool (and that satisfy
   a few other criteria) are, by default, mapped into the process
   address space instead of being copied into the local cache. This can
   result in better-than-usual performance, as available virtual memory
   is normally much larger than the local cache, and page faults are
   faster than page copying on many systems. However, in the presence
   of limited virtual memory it can cause resource starvation, and in
   the presence of large databases, it can result in immense process
   sizes.

   This method sets the maximum file size, in bytes, for a file to be
   mapped into the process address space. If no value is specified, it
   defaults to 10MB.
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/env_set_mp_mmapsize.html>`__

.. function:: log_archive(flags=0)

   Returns a list of log or database file names. By default,
   log_archive returns the names of all of the log files that are no
   longer in use (e.g., no longer involved in active transactions), and
   that may safely be archived for catastrophic recovery and then
   removed from the system.
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/log_archive.html>`__

.. function:: lock_detect(atype, flags=0)

   Run one iteration of the deadlock detector, returns the number of
   transactions aborted.
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/lock_detect.html>`__

.. function:: lock_get(locker, obj, lock_mode, flags=0)

   Acquires a lock and returns a handle to it as a DBLock object. The
   locker parameter is an integer representing the entity doing the
   locking, and obj is a string representing the item to be locked.
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/lock_get.html>`__

.. function:: lock_id()

   Acquires a locker id, guaranteed to be unique across all threads and
   processes that have the DBEnv open.
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/lock_id.html>`__

.. function:: lock_put(lock)

   Release the lock.
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/lock_put.html>`__

.. function:: lock_stat(flags=0)

   Returns a dictionary of locking subsystem statistics with the
   following keys:

    +---------------+-------------------------------------+
    | lastid        | Last allocated lock ID              |
    +---------------+-------------------------------------+
    | nmodes        | Number of lock modes                |
    +---------------+-------------------------------------+
    | maxlocks      | Maximum number of locks possible    |
    +---------------+-------------------------------------+
    | maxlockers    | Maximum number of lockers possible  |
    +---------------+-------------------------------------+
    | maxobjects    | Maximum number of objects possible  |
    +---------------+-------------------------------------+
    | nlocks        | Number of current locks             |
    +---------------+-------------------------------------+
    | maxnlocks     | Maximum number of locks at once     |
    +---------------+-------------------------------------+
    | nlockers      | Number of current lockers           |
    +---------------+-------------------------------------+
    | nobjects      | Number of current objects           |
    +---------------+-------------------------------------+
    | maxnobjects   | Maximum number of objects at once   |
    +---------------+-------------------------------------+
    | maxnlockers   | Maximum number of lockers at once   |
    +---------------+-------------------------------------+
    | nrequests     | Total number of locks requested     |
    +---------------+-------------------------------------+
    | nreleases     | Total number of locks released      |
    +---------------+-------------------------------------+
    | nnowaits      | Total number of lock requests that  |
    |               | failed because of DB_LOCK_NOWAIT    |
    +---------------+-------------------------------------+
    | nconflicts    | Tot number of locks not immediately |
    |               | available due to conflicts          |
    +---------------+-------------------------------------+
    | ndeadlocks    | Number of deadlocks detected        |
    +---------------+-------------------------------------+
    | regsize       | Size of the region                  |
    +---------------+-------------------------------------+
    | region_wait   | Number of times a thread of control |
    |               | was forced to wait before obtaining |
    |               | the region lock                     |
    +---------------+-------------------------------------+
    | region_nowait | Number of times a thread of control |
    |               | was able to obtain the region lock  |
    |               | without waiting                     |
    +---------------+-------------------------------------+

   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/lock_stat.html>`__

.. function:: set_tx_max(max)

   Set the maximum number of active transactions
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/env_set_tx_max.html>`__

.. function:: txn_begin(parent=None, flags=0)

   Creates and begins a new transaction. A DBTxn object is returned.
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/txn_begin.html>`__

.. function:: txn_checkpoint(kbyte=0, min=0, flag=0)

   Flushes the underlying memory pool, writes a checkpoint record to the
   log and then flushes the log.
   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/txn_checkpoint.html>`__

.. function:: txn_stat()

   Return a dictionary of transaction statistics with the following
   keys:

    +--------------+---------------------------------------------+
    | time_ckp     | Time the last completed checkpoint finished |
    |              | (as the number of seconds since the Epoch,  |
    |              | returned by the IEEE/ANSI Std 1003.1 POSIX  |
    |              | time interface)                             |
    +--------------+---------------------------------------------+
    | last_txnid   | Last transaction ID allocated               |
    +--------------+---------------------------------------------+
    | maxtxns      | Max number of active transactions possible  |
    +--------------+---------------------------------------------+
    | nactive      | Number of transactions currently active     |
    +--------------+---------------------------------------------+
    | maxnactive   | Max number of active transactions at once   |
    +--------------+---------------------------------------------+
    | nbegins      | Number of transactions that have begun      |
    +--------------+---------------------------------------------+
    | naborts      | Number of transactions that have aborted    |
    +--------------+---------------------------------------------+
    | ncommits     | Number of transactions that have committed  |
    +--------------+---------------------------------------------+
    | regsize      | Size of the region                          |
    +--------------+---------------------------------------------+
    | region_wait  | Number of times that a thread of control    |
    |              | was forced to wait before obtaining the     |
    |              | region lock                                 |
    +--------------+---------------------------------------------+
    | region_nowait| Number of times that a thread of control    |
    |              | was able to obtain the region lock without  |
    |              | waiting                                     |
    +--------------+---------------------------------------------+

   `More info...
   <http://www.oracle.com/technology/documentation/berkeley-db/db/
   api_c/txn_stat.html>`__

