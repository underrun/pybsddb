/************************************************************************
               Copyright (c) 1997 by Total Control Software
                         All Rights Reserved
------------------------------------------------------------------------

Module Name:    db.i

Description:    SWIG interface file for the BerkeleyDB 3.1 library.

Creation Date:  8/2/97 5:02:10PM

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
# March 20, 2000
#
# The above license applies.  I ported this code to use Berkeley
# DB 3.1.x (formerly 3.0.x) instead of 2.7.x.  Threading support should
# be better in this version as the global lock is released during DB
# operations.
#   --  Gregory P. Smith <greg@electricrain.com>
#

************************************************************************/

// define this to be one of these:  SWIG11, SWIG13a5
// (this define "magically" works because SWIG11 ignores it and SWIG13a5 puts it in db_wrap.c)
#define SWIG13a5

%module db
%{
#include <db.h>
%}

%include typemaps.i

//---------------------------------------------------------------------------

// Version number of this module
#define __version__ "2.2.3"

// CVS revision
#define cvsid "$Id$"

//----------------------------------------------------------------------
// First, some definitions and constants copied from db.h that need to be
// visible for SWIG or from Python...

typedef unsigned int    size_t;

typedef unsigned char   u_int8_t;
typedef short           int16_t;
typedef unsigned short  u_int16_t;
typedef int             int32_t;
typedef unsigned int    u_int32_t;

typedef u_int32_t       db_pgno_t;  /* Page number type. */
typedef u_int16_t       db_indx_t;  /* Page offset type. */

typedef u_int32_t       db_recno_t; /* Record number type. */
typedef u_int32_t       DB_LOCK;    /* Object returned by lock manager. */


// Most of these are defined in db.h with #define.  We do them here as an enum
// so SWIG will use the symbolic name instead of the macro value.
// This protects us a bit from those values changing without my knowledge...
enum {
        DB_VERSION_MAJOR,
        DB_VERSION_MINOR,
        DB_VERSION_PATCH,
        DB_VERSION_STRING,

        DB_MAX_PAGES,
        DB_MAX_RECORDS,

        DB_DBT_PARTIAL,

        DB_XA_CREATE,

        DB_CREATE,
        DB_NOMMAP,
        DB_THREAD,

        DB_INIT_CDB,
        DB_INIT_LOCK,
        DB_INIT_LOG,
        DB_INIT_MPOOL,
        DB_INIT_TXN,
        DB_RECOVER,
        DB_RECOVER_FATAL,
        DB_TXN_NOSYNC,
        DB_USE_ENVIRON,
        DB_USE_ENVIRON_ROOT,

        DB_LOCKDOWN,
        DB_PRIVATE,

        DB_TXN_SYNC,
        DB_TXN_NOWAIT,
        DB_FORCE,

        DB_EXCL,
        DB_RDONLY,
        DB_TRUNCATE,

        DB_LOCK_NORUN,
        DB_LOCK_DEFAULT,
        DB_LOCK_OLDEST,
        DB_LOCK_RANDOM,
        DB_LOCK_YOUNGEST,

        DB_BTREE,
        DB_HASH,
        DB_RECNO,
        DB_UNKNOWN,

        DB_DUP,
        DB_DUPSORT,
        DB_RECNUM,
        DB_RENUMBER,
        DB_REVSPLITOFF,
        DB_SNAPSHOT,

        DB_AFTER,
        DB_APPEND,
        DB_BEFORE,
        DB_CHECKPOINT,
        DB_CONSUME,
        DB_CURLSN,
        DB_CURRENT,
        DB_FIRST,
        DB_FLUSH,
        DB_GET_BOTH,
        DB_GET_RECNO,
        DB_JOIN_ITEM,
        DB_KEYFIRST,
        DB_KEYLAST,
        DB_LAST,
        DB_NEXT,
        DB_NEXT_DUP,
        DB_NEXT_NODUP,
        DB_NOOVERWRITE,
        DB_NOSYNC,
        DB_POSITION,
        DB_PREV,
        DB_RECORDCOUNT,
        DB_SET,
        DB_SET_RANGE,
        DB_SET_RECNO,
        DB_WRITECURSOR,

        DB_OPFLAGS_MASK,
        DB_RMW,

        DB_INCOMPLETE,
        DB_KEYEMPTY,
        DB_KEYEXIST,
        DB_LOCK_DEADLOCK,
        DB_LOCK_NOTGRANTED,
        DB_NOTFOUND,
        DB_OLD_VERSION,
        DB_RUNRECOVERY,

};


//----------------------------------------------------------------------
// And now some C code to help with the wrappers...

%{
struct __db_txn;        // from <db.h>
%}

// tell SWIG about the typedef in db.h (without duplicating it here
// and getting a redefinition of DB_TXN compiler Warning)
//%name(DB_TXN) struct __db_txn; 

%{
static PyObject* dbError;             // Make an error variable for exceptions

struct MyDB_ENV {
    DB_ENV* db_env;
    DB_TXN* autoTrans;
    int     flags;             // saved flags from open()
    int     atRefCnt;
    int     closed;
};

struct MyDB {
    DB*             db;
    struct MyDB_ENV* myenv;
    PyObject*       myenvobj;  // PyObject "containing" the above MyDB_ENV
    int             flags;     // saved flags from open()
    long            size;
    int             closed;
};

#define CHECK_DBFLAG(mydb, flag)        ( ((mydb)->flags & (flag)) || ((mydb)->myenv->flags & (flag)) )

struct MyDBC {
    DBC*            dbc;
    struct MyDB*    mydb;
    PyObject*       mydbobj;  // PyObject "containing" the above MyDB
    int             closed;
};

/* make a nice error object to raise for errors. */
static PyObject* makeDbError(int err) {
    struct { int code; char* text; } errors[] = {
        { DB_INCOMPLETE,        "DB_INCOMPLETE: Sync didn't finish" },
        { DB_KEYEMPTY,          "DB_KEYEMPTY: The key/data pair was deleted or was never created" },
        { DB_KEYEXIST,          "DB_KEYEXIST: The key/data pair already exists" },
        { DB_LOCK_DEADLOCK,     "DB_LOCK_DEADLOCK: Locker killed to resolve deadlock" },
        { DB_LOCK_NOTGRANTED,   "DB_LOCK_NOTGRANTED: Lock unavailable, no-wait set" },
        { DB_NOTFOUND,          "DB_NOTFOUND: Key/data pair not found (EOF)" },
        { DB_OLD_VERSION,       "DB_OLD_VERSION: Out-of-date version" },
        { DB_RUNRECOVERY,       "DB_RUNRECOVERY: PANIC!  Run recovery utilities" },
        { -99,                  "UNKNOWN ERROR!!!" },
    };
    int         i;
    char*       errTxt;
    int         numErrors = sizeof(errors) / sizeof(errors[0]);

    if (err < 0) {
        for (i=0; i<numErrors; i++) {
            errTxt = errors[i].text;
            if (err == errors[i].code) break;
        }
    }
    else {
        errTxt = strerror(err);
    }

    return Py_BuildValue("(is)", err, errTxt);
}

// Used to pass errors up to raise exceptions.  The setting and
// testing of this variable must happen while threads are disabled to
// prevent threads from clobbering eachother's return values.
static int MyDb_ErrorValue = 0;

#define passthruError  -2872  // XXX a value not used by BerkeleyDB or errno

#define RETURN_IF_ERR()   { MyDb_ErrorValue = err; if (err) return NULL; }
#define RETURN_PASS()  { MyDb_ErrorValue = passthruError; return NULL; }
#define RETURN_NONE()  { Py_INCREF(Py_None); return Py_None; }

#define MYDB_BEGIN_ALLOW_THREADS Py_BEGIN_ALLOW_THREADS;
#define MYDB_END_ALLOW_THREADS Py_END_ALLOW_THREADS;

%}


// Pass DBT key and data values in using python strings
// (this used to be done explicitly everywhere using PyObject
// parameters and GET_DBT)
%typemap(python,in) DBT*(DBT dbt) {
    memset(&dbt, 0, sizeof(dbt));
    if ($source == Py_None) {
        dbt.data = NULL;
        dbt.size = 0;
    } else if (!PyArg_Parse($source, "s#", &dbt.data, &dbt.size)) {
        PyErr_SetString(PyExc_TypeError,
                "Key and Data values must be of type string or None.");
        return NULL;
    }
    $target = &dbt;
}


// Surround all function calls by checking the module's global error
// value.
%except(python) {
    //printf("### Entering: $name\n");
    $function
    // MyDb_ErrorValue is a global; the global python thread lock must
    // be held from the time it is set through the time it gets tested
    // here.  This means all functions must call MYDB_END_ALLOW_THREADS
    // before calling RETURN_*() to test & set the global error value
    // if they ever called MYDB_BEGIN_ALLOW_THREADS.
    if (MyDb_ErrorValue == passthruError) {
        // Someone called PyErr_SetString and RETURN_PASS()
        MyDb_ErrorValue = 0;
        return NULL;
    } else if (MyDb_ErrorValue != 0) {
        // MyDb_ErrorValue contains an error set by RETURN_IF_ERR()
        PyErr_SetObject(dbError, makeDbError(MyDb_ErrorValue));
        MyDb_ErrorValue = 0;
        return NULL;
    }
    //printf("### Leaving: $name\n");
}


//----------------------------------------------------------------------


// version()
//
// Returns a tuple of major, minor, and patch release numbers of the
// underlying DB library.
//
%name(version) char* db_version(int* T_OUTPUT, int* T_OUTPUT, int* T_OUTPUT);


//---------------------------------------------------------------------------

// class Txn - An explicit database transaction
//
// An explicit transaction must have its ID explicitly passed to the DB method
// calls, and therefore cannot be passed to the dictionary simulation routines.
// On the other hand, there can be more than one explicit transaction active in
// any one process at once.
// (You should also be able to mix explicit and automatic transactions.)
//
// Txn objects are created using the DbEnv.txn_begin() method.
//
//%name(Txn) struct __db_txn {
%name(Txn) struct __db_txn {

    %addmethods {

        // Txn(DbEnv, parent=None, flags=0)
        //
        // Do not call this directly.  Call DbEnv->txn_begin()
        //
        __db_txn(struct MyDB_ENV* myenv, struct __db_txn* parent=NULL, long flags=0) {
            int err;
            struct __db_txn* txn;
            err = txn_begin(myenv->db_env, parent, &txn, flags);
            RETURN_IF_ERR();
            return txn;
        }

        // Txn.abort()
        //
        // This function causes an abnormal termination of the transaction.  The
        // log is played backwards and any necessary recovery operations are
        // initiated.
        PyObject* abort() {
            int err;
            err = txn_abort(self);
            RETURN_IF_ERR();
            RETURN_NONE();
        }

        // Txn.prepare()
        //
        // If this transaction is involved in a distributed transaction system,
        // this function should be called to begin the two-phase commit.
        PyObject* prepare() {
            int err = txn_prepare(self);
            RETURN_IF_ERR();
            RETURN_NONE();
        }

        // Txn.commit(flags=0)
        //
        // This function ends the transaction, commiting the changes to the
        // database.
        PyObject* commit(long flags=0) {
            int err;
            err = txn_commit(self, flags);
            RETURN_IF_ERR();
            RETURN_NONE();
        }

    }
};


//---------------------------------------------------------------------------
// The DbEnv database environment class

// BerkeleyDB database environment
//
%name(DbEnv) struct MyDB_ENV {

    %addmethods {

        MyDB_ENV() {
            int err;
            struct MyDB_ENV* new_envp;
            new_envp = (struct MyDB_ENV*)PyMem_Malloc(sizeof(struct MyDB_ENV));
            if (!new_envp) {
                PyErr_SetString(PyExc_MemoryError, "PyMem_Malloc failed");
                RETURN_PASS();
            }
            err = db_env_create(&new_envp->db_env, 0);
            RETURN_IF_ERR();
            new_envp->closed = 1;
            new_envp->autoTrans = NULL;
            new_envp->atRefCnt = 0;
            new_envp->flags = 0;
            return new_envp;
        }

        ~MyDB_ENV() {
            if (!self->closed) {
                self->db_env->close(self->db_env, 0);
                // return value ignored in destructor, possibly bad...?
            }
            PyMem_Free(self);
        }

        // open(string db_home, integer flags)
        //   Open/initialize the database environment.
        PyObject* open(char* db_home, long flags) {
            int err = self->db_env->open(self->db_env, db_home, flags, 0);
            RETURN_IF_ERR();
            self->closed = 0;
            self->flags = flags;
            RETURN_NONE();
        }

        // close()
        //   Close this database environment by freeing any allocated resources
        //   and closing any underlying subsystems.
        PyObject* close() {
            int err;
            if (!self->closed) {      /* Don't close more than once */
                err = self->db_env->close(self->db_env, 0);
                RETURN_IF_ERR();
                self->closed = 1;
            }
            RETURN_NONE();
        }

        // set_data_dir(string dir)
        //   Set the path of a directory to be used as the location of the
        //   access method database files.  See BerkeleyDB docs for
        //   more detailed info.
        PyObject* set_data_dir(char* dir) {
            int err = self->db_env->set_data_dir(self->db_env, dir);
            RETURN_IF_ERR();
            RETURN_NONE();
        }

        // set_lg_dir(string dir)
        //   The path of a directory to be used as the location of logging files.
        PyObject* set_lg_dir(char* dir) {
            int err = self->db_env->set_lg_dir(self->db_env, dir);
            RETURN_IF_ERR();
            RETURN_NONE();
        }

        // set_tmp_dir(string dir)
        //   The path of a directory to be used as the location of temporary files.
        PyObject* set_tmp_dir(char* dir) {
            int err = self->db_env->set_tmp_dir(self->db_env, dir);
            RETURN_IF_ERR();
            RETURN_NONE();
        }

        // set_cachesize(gbytes=0, bytes=0, ncache=0)
        //
        // Set the size of this database's shared memory buffer pool,
        // i.e., the cache, to gbytes gigabytes plus bytes. The
        // cache should be the size of the normal working data set of the
        // application, with some small amount of additional
        // memory for unusual situations. (Note, the working set is
        // not the same as the number of simultaneously referenced pages,
        // and should be quite a bit larger!) 
        PyObject* set_cachesize(int gbytes=0, int bytes=0, int ncache=0) {
            int err = self->db_env->set_cachesize(self->db_env, gbytes, bytes, ncache);
            RETURN_IF_ERR();
            RETURN_NONE();
        }

        // set_lg_bsize(integer)
        //
        // Set the size of the in-memory log buffer, in bytes.
        PyObject* set_lg_bsize(int lg_bsize) {
            int err = self->db_env->set_lg_bsize(self->db_env, lg_bsize);
            RETURN_IF_ERR();
            RETURN_NONE();
        }

        // set_lg_max(integer)
        //
        // Set the maximum size of a single file in the log, in bytes. Because
        // DbLsn file offsets are unsigned 4-byte values, the set value may not
        // be larger than the maximum unsigned 4-byte value.
        PyObject* set_lg_max(int lg_max) {
            int err = self->db_env->set_lg_max(self->db_env, lg_max);
            RETURN_IF_ERR();
            RETURN_NONE();
        }

        // set_lg_detect(integer)
        //
        // Set if the deadlock detector is to be run whenever a lock conflict
        // occurs, and specify which transaction should be aborted in the case
        // of a deadlock. The specified value must be one of the following list:
        // DB_LOCK_DEFAULT
        //       Use the default policy as specified by db_deadlock.
        // DB_LOCK_OLDEST
        //       Abort the oldest transaction.
        // DB_LOCK_RANDOM
        //       Abort a random transaction involved in the deadlock.
        // DB_LOCK_YOUNGEST
        //       Abort the youngest transaction.
        PyObject* set_lk_detect(int lk_detect) {
            int err = self->db_env->set_lk_detect(self->db_env, lk_detect);
            RETURN_IF_ERR();
            RETURN_NONE();
        }

        // set_mp_mmapsize(integer)
        // 
        // Set the maximum file size, in bytes, for a file to be mapped into the
        // process address space. If no value is specified, it defaults to 10MB.
        PyObject* set_mp_mmapsize(int mp_mmapsize) {
            int err = self->db_env->set_mp_mmapsize(self->db_env, mp_mmapsize);
            RETURN_IF_ERR();
            RETURN_NONE();
        }

        //-------------------------------------------------------------------
        // Transaction interface

        // beginAutoTrans(flags=0)
        //
        // This function begins an "Automatic Transaction."  An automatic
        // transaction automatically involves all DB method calls including the
        // dictionary simulation routines, until the transaction is commited or
        // aborted.  There can only be one automatic transaction in any process
        // at a time, however nested calls can be made to beginAutoTrans and
        // commitAutoTrans are supported via reference counting.  abortAutoTrans
        // ignores the nesting count and performs the abort.
        PyObject* beginAutoTrans(long flags=0) {
            int err;
            if (self->atRefCnt == 0) {
                err = txn_begin(self->db_env, NULL, &self->autoTrans, flags);
                RETURN_IF_ERR();
            }
            self->atRefCnt += 1;
            RETURN_NONE();
        }

        // abortAutoTrans()
        //
        // Aborts and rolls-back the active automatic transaction.
        PyObject* abortAutoTrans() {
            int err;
            if (self->atRefCnt) {
                err = txn_abort(self->autoTrans);
                self->autoTrans = NULL;
                self->atRefCnt = 0;
                RETURN_IF_ERR();
            }
            RETURN_NONE();
        }

        // prepareAutoTrans()
        //
        // If the active automatic transaction is involved in a distributed
        // transaction system, this function should be called to begin the
        // two-phase commit.
        PyObject* prepareAutoTrans() {
            int err;
            if (self->atRefCnt) {
                err = txn_prepare(self->autoTrans);
                RETURN_IF_ERR();
            }
            RETURN_NONE();
        }

        // commitAutoTrans(flags=0)
        //
        // This function ends the active automatic transaction, commiting the
        // changes to the database.
        PyObject* commitAutoTrans(long flags=0) {
            int err;
            self->atRefCnt -= 1;
            if (self->atRefCnt == 0) {
                err = txn_commit(self->autoTrans, flags);
                RETURN_IF_ERR();
            }
            RETURN_NONE();
        }


        // txn_begin(parent=None, flags=0)
        //
        // This function starts a new explicit transaction.  An explicit
        // transaction must be passed to each of the database access routines
        // that need to be involved in the transaction, and therefore cannot
        // include the dictionary simulation routines.  On the other hand,
        // there can be more than one explicit transaction active in any one
        // process at once.  (You should also be able to mix explicit and
        // automatic transactions.)
        //
        // This function returns a Txn object that must be passed along to
        // any function that needs to be involved in the transaction.
        //
        // Notes:
        //  * transactions may not span threads, i.e., each
        //    transaction must begin and end in the same thread, and each
        //    transaction may only be used by a single thread. 
        //  * cursors may not span transactions, i.e., each cursor
        //    must be opened and closed within a single transaction. 
        //  * a parent transaction may not issue any Berkeley DB
        //    operations, except for txn_begin and txn_abort, while it
        //    has active child transactions (transactions that have not
        //    yet been committed or aborted).
        %new struct __db_txn* txn_begin(struct __db_txn* parent=NULL, long flags=0) {
            return new___db_txn(self, parent, flags);
        }

        // txn_checkpoint(min=0)
        //
        // The txn_checkpoint function flushes the underlying memory
        // pool, writes a checkpoint record to the log and then
        // flushes the log.  If min is non-zero, a checkpoint is only
        // done if more than min minutes have passed since the last
        // previous checkpoint.
        // The only valid flag is DB_FORCE which forces a checkpoint
        // record even if there has been no activity since the
        // previous checkpoint.
        PyObject* txn_checkpoint(int min=0, long flags=0) {
            int err = txn_checkpoint(self->db_env, 0, min, flags);
            RETURN_IF_ERR();
            RETURN_NONE();
        }


    }

};


//----------------------------------------------------------------------

// class Dbc
//
//  The Dbc (Database Cursor) class supports sequential access to the records
//  stored in a given databse file.  Cursors are created by calling the cursor
//  method of an instance of the DB class.
//
//  Each cursor maintains positioning information within a set of key/data pairs.
//  In the presence of transactions, cursors are only valid within the context of
//  a single transaction, the one specified during the cursor method of the DB
//  class. All cursor operations will be executed in the context of that
//  transaction.  Before aborting or committing a transaction, all cursors used
//  within that transaction must be closed.  In the presence of transactions, the
//  application must call abortTrans() (or abortAutoTrans() as appropriate) if
//  any of the cursor operations raises an exception, indicating that a deadlock
//  (DB_LOCK_DEADLOCK) or system failure occurred.
//
//  When locking is enabled, page locks are retained between consecutive cursor
//  calls.  For this reason, in the presence of locking, applications should
//  discard cursors as soon as they are done with them.  Calling the DB.close
//  method discards any cursors opened from that DB.
//
%name(Dbc) struct MyDBC {
    %addmethods {

        // Dbc.__del__
        //
        // When the cursor object goes out of scope, it is closed.
        ~MyDBC() {
            if (!self->closed) {
                MYDB_BEGIN_ALLOW_THREADS;
                self->dbc->c_close(self->dbc);
                MYDB_END_ALLOW_THREADS;
            }
            // TODO Py_DECREF on the Db object that created us (also INCREF when created)
            PyMem_Free(self);
        }

        // Dbc.close()
        //
        // The cursor is discarded.  No further references to this cursor
        // should be made.
        //
        PyObject* close() {
            int err;
            MYDB_BEGIN_ALLOW_THREADS;
            err = self->dbc->c_close(self->dbc);
            MYDB_END_ALLOW_THREADS;
            RETURN_IF_ERR();
            self->closed = 1;
            RETURN_NONE();
        }

        // Dbc.delete()
        //
        // The key/data pair currently referenced by the cursor is removed
        // from the database.
        //
        // The cursor position is unchanged after a delete and subsequent
        // calls to cursor functions expecting the cursor to reference an
        // existing key will fail.
        PyObject* delete(long flags=0) {
            int err;
            MYDB_BEGIN_ALLOW_THREADS;
            err = self->dbc->c_del(self->dbc, flags);
            MYDB_END_ALLOW_THREADS;
            RETURN_IF_ERR();
            self->mydb->size = -1;
            RETURN_NONE();
        }

        // Dbc.get(flags)
        //
        // This function returns a tuple containing a key and data value from
        // the database.
        //
        // Modifications to the database during a sequential scan will be
        // reflected in the scan, i.e. records inserted behind a cursor will
        // not be returned while records inserted in front of a cursor will
        // be returned.
        //
        // If multiple threads or processes insert items into the same
        // database file without using locking, the results are undefined.
        //
        // The parameter flags must be set to exactly one of the following
        // values:
        //
        //    DB_FIRST
        //        The cursor is set to reference the first key/data pair of the
        //        database, and that pair is returned.  In the presence of
        //        duplicate key values, the first data item in the set of
        //        duplicates is returned.  If the database is empty, this
        //        function will return None.
        //
        //    DB_LAST
        //        The cursor is set to reference the last key/data pair of the
        //        database, and that pair is returned. In the presence of
        //        duplicate key values, the last data item in the set of
        //        duplicates is returned.  If the database is empty, this
        //        method will return None.
        //
        //    DB_NEXT
        //        If the cursor is not yet initialized, DB_NEXT is identical to
        //        DB_FIRST.  Otherwise, move the cursor to the next key/data
        //        pair of the database, and that pair is returned. In the
        //        presence of duplicate key values, the key may not change.  If
        //        the cursor is already on the last record in the database,
        //        this method will return None.
        //
        //    DB_PREV
        //        If the cursor is not yet initialized, DB_PREV is identical to
        //        DB_LAST. Otherwise, move the cursor to the previous key/data
        //        pair of the database, and that pair is returned.  In the
        //        presence of duplicate key values, the key may not change.  If
        //        the cursor is already on the first record in the database,
        //        this method will return None.
        //
        //    DB_CURRENT
        //        Return the key/data pair currently referenced by the cursor.
        //        If the cursor key/data pair has been deleted, this method
        //        will return DB_KEYEMPTY.  If the cursor is not yet
        //        initialized, the get method will raise db.error with a value
        //        of EINVAL.
        PyObject* get(long flags) {
            int err;
            DBT key;
            DBT data;
            PyObject *retval = NULL;
            memset(&key, 0, sizeof(key));
            memset(&data, 0, sizeof(data));
            if (CHECK_DBFLAG(self->mydb, DB_THREAD)) {
                // Tell BerkeleyDB to malloc the return value (thread safe)
                data.flags = DB_DBT_MALLOC;
                key.flags = DB_DBT_MALLOC;
            }
            MYDB_BEGIN_ALLOW_THREADS;
            err = self->dbc->c_get(self->dbc, &key, &data, flags);
            MYDB_END_ALLOW_THREADS;

            // emulate Python dict.get() behavior, return None if the key was not found
            if (err == DB_NOTFOUND) {
                Py_INCREF(Py_None);
                retval = Py_None;
            } else {
                RETURN_IF_ERR();
            }
            if (retval == NULL) {  // if we're not returning Py_None
                retval = Py_BuildValue("s#s#", key.data, key.size,
                                             data.data, data.size);
            }
            if (CHECK_DBFLAG(self->mydb, DB_THREAD)) {
                if (key.data != NULL) free(key.data);
                if (data.data != NULL) free(data.data);
            }
            return retval;
        }

        // Dbc.first()
        //
        // A convenience method.  Equivalent to calling get with DB_FIRST.
        PyObject* first()   { return MyDBC_get(self, DB_FIRST); }

        // Dbc.last()
        //
        // A convenience method.  Equivalent to calling get with DB_LAST.
        PyObject* last()    { return MyDBC_get(self, DB_LAST); }

        // Dbc.next()
        //
        // A convenience method.  Equivalent to calling get with DB_NEXT.
        PyObject* next()    { return MyDBC_get(self, DB_NEXT); }

        // Dbc.prev()
        //
        // A convenience method.  Equivalent to calling get with DB_PREV.
        PyObject* prev()    { return MyDBC_get(self, DB_PREV); }

        // Dbc.current()
        //
        // A convenience method.  Equivalent to calling get with DB_CURRENT.
        PyObject* current() { return MyDBC_get(self, DB_CURRENT);   }


        // Dbc.set(key)
        //
        // Move the cursor to the specified key of the database, and return
        // the given key/data pair. In the presence of duplicate key values,
        // the method will return the first key/data pair for the given key.
        //
        // If the database is a recno database and the requested key exists,
        // but was never explicitly created by the application or was later
        // deleted, the set method raises db.error with a value of
        // DB_KEYEMPTY.
        //
        // The range parameter can be set to true in BTREE databases to set
        // the position to the smallest key greater than or equal too the
        // specified key.  This allows for partial key matches and range
        // searches.
        //
        // If no matching keys are found, this method will raise db.error
        // with a value of DB_NOTFOUND.
        PyObject* set(DBT* keyp) {
            int err;
            DBT data;
            PyObject *retval;
            memset(&data, 0, sizeof(data));
            if (CHECK_DBFLAG(self->mydb, DB_THREAD)) {
                // Tell BerkeleyDB to malloc the return value (thread safe)
                data.flags = DB_DBT_MALLOC;
            }
            MYDB_BEGIN_ALLOW_THREADS;
            err = self->dbc->c_get(self->dbc, keyp, &data, DB_SET);
            MYDB_END_ALLOW_THREADS;
            RETURN_IF_ERR();
            retval = Py_BuildValue("s#s#", keyp->data, keyp->size,
                                         data.data, data.size);
            if (CHECK_DBFLAG(self->mydb, DB_THREAD)) {
                if (data.data != NULL) free(data.data);
            }
            return retval;
        }

        // Dbc.setRange(key)
        //
        // Identical to the set method, except in the case of the btree access
        // method, the returned key/data pair is the smallest key greater than
        // or equal to the specified key, permitting partial key matches and
        // range searches.
        PyObject* setRange(DBT* keyp) {
            int err;
            DBT data;
            PyObject *retval;
            memset(&data, 0, sizeof(data));
            if (CHECK_DBFLAG(self->mydb, DB_THREAD)) {
                // Tell BerkeleyDB to malloc the return value (thread safe)
                data.flags = DB_DBT_MALLOC;
                keyp->flags = DB_DBT_MALLOC;
            }
            MYDB_BEGIN_ALLOW_THREADS;
            err = self->dbc->c_get(self->dbc, keyp, &data, DB_SET_RANGE);
            MYDB_END_ALLOW_THREADS;
            RETURN_IF_ERR();
            retval = Py_BuildValue("s#s#", keyp->data, keyp->size,
                                         data.data, data.size);
            if (CHECK_DBFLAG(self->mydb, DB_THREAD)) {
                if (keyp->data != NULL) free(keyp->data);
                if (data.data != NULL) free(data.data);
            }
            return retval;
        }

        // Dbc.setRecno(recno)
        //
        // Move the cursor to the specific numbered record of the database, and
        // return the associated key/data pair.  For this method to be used, the
        // underlying database must be of type btree and it must have been
        // created with the DB_RECNUM flag.
        PyObject* setRecno(db_recno_t recno) {
            int err;
            DBT key;
            DBT data;
            PyObject *retval;
            key.data = &recno;
            key.size = sizeof(db_recno_t);
            key.ulen = key.size;
            key.flags = DB_DBT_USERMEM;
            memset(&data, 0, sizeof(data));
            if (CHECK_DBFLAG(self->mydb, DB_THREAD)) {
                // Tell BerkeleyDB to malloc the return value (thread safe)
                data.flags = DB_DBT_MALLOC;
            }
            MYDB_BEGIN_ALLOW_THREADS;
            err = self->dbc->c_get(self->dbc, &key, &data, DB_SET_RECNO);
            MYDB_END_ALLOW_THREADS;
            RETURN_IF_ERR();
            retval = Py_BuildValue("s#s#", key.data, key.size,
                                         data.data, data.size);
            if (CHECK_DBFLAG(self->mydb, DB_THREAD) && (data.data != NULL)) {
                free(data.data);
            }
            return retval;
        }

        // Dbc.getRecno()
        //
        // Return the record number associated with the cursor.  For this
        // method to be used, the underlying database must be of type btree
        // and it must have been created with the DB_RECNUM flag.
        PyObject* getRecno() {
            int err;
            db_recno_t recno;
            DBT key;
            DBT data;
            memset(&key, 0, sizeof(key));
            memset(&data, 0, sizeof(data));
            if (CHECK_DBFLAG(self->mydb, DB_THREAD)) {
                // Tell BerkeleyDB to malloc the return value (thread safe)
                data.flags = DB_DBT_MALLOC;
                key.flags = DB_DBT_MALLOC;
            }
            MYDB_BEGIN_ALLOW_THREADS;
            err = self->dbc->c_get(self->dbc, &key, &data, DB_GET_RECNO);
            MYDB_END_ALLOW_THREADS;
            RETURN_IF_ERR();
            memcpy(&recno, data.data, sizeof(db_recno_t));
            if (CHECK_DBFLAG(self->mydb, DB_THREAD)) {
                if (key.data != NULL) free(key.data);
                if (data.data != NULL) free(data.data);
            }
            return PyInt_FromLong(recno);
        }


        // Dbc.put(key, data, flags)
        //
        // This method stores key/data pairs into the database.  The flags
        // parameter must be set to exactly one of the following values:
        //
        //    DB_AFTER
        //            In the case of the btree and hash access methods, insert the
        //            data element as a duplicate element of the key referenced by
        //            the cursor.  The new element appears immediately after the
        //            current cursor position.  It is an error to specify DB_AFTER
        //            if the underlying btree or hash database was not created
        //            with the DB_DUP flag. The key parameter is ignored.
        //
        //            In the case of the recno access method, it is an error to
        //            specify DB_AFTER if the underlying recno database was not
        //            created with the DB_RENUMBER flag.  If the DB_RENUMBER flag
        //            was specified, a new key is created, all records after the
        //            inserted item are automatically renumbered.  The initial
        //            value of the key parameter is ignored.
        //
        //    DB_BEFORE
        //            Identical to DB_AFTER except the new element appears
        //            immediately before the current cursor position.
        //
        //    DB_CURRENT
        //            Overwrite the data of the key/data pair referenced by the
        //            cursor with the specified data item.  The key parameter is
        //            ignored.
        //
        //    DB_KEYFIRST
        //            In the case of the btree and hash access methods, insert the
        //            specified key/data pair into the database.  If the key
        //            already exists in the database, the inserted data item is
        //            added as the first of the data items for that key.
        //
        //            The DB_KEYFIRST flag may not be specified to the recno access
        //            method.
        //
        //    DB_KEYLAST
        //            Insert the specified key/data pair into the database.  If
        //            the key already exists in the database, the inserted data
        //            item is added as the last of the data items for that key.
        //
        //            The DB_KEYLAST flag may not be specified to the recno access
        //            method.
        //
        // If the cursor record has been deleted, the put method raises
        // db.error with value of DB_KEYEMPTY.
        //
        // If the put method fails for any reason, the state of the cursor
        // will be unchanged.  If put succeeds and an item is inserted
        // into the database, the cursor is always positioned to reference
        // the newly inserted item.
        PyObject* put(DBT* keyp, DBT* datap, long flags) {
            int err;
            MYDB_BEGIN_ALLOW_THREADS;
            err = self->dbc->c_put(self->dbc, keyp, datap, flags);
            MYDB_END_ALLOW_THREADS;
            RETURN_IF_ERR();
            self->mydb->size = -1;
            RETURN_NONE();
        }

        // Dbc.count()
        //
        // The Dbc.count method returns a count of the number of duplicate
        // data items for the key referenced by the cursor.  If the
        // underlying database does not support duplicate data items (ie: it
        // wasn't opened with the DB_DUP flag) the call will still succeed
        // and a count of 1 will be returned. 
        //
        // If the cursor is not yet initialized, this method throws an
        // exception that encapsulates EINVAL.
        //
        PyObject* count() {
            int err;
            db_recno_t mycount;
            MYDB_BEGIN_ALLOW_THREADS;
            err = self->dbc->c_count(self->dbc, &mycount, 0);
            MYDB_END_ALLOW_THREADS;
            RETURN_IF_ERR();
            return PyInt_FromLong(mycount);
        }
    }
};



//----------------------------------------------------------------------

// class Db
//
// This class encapsulates the DB database file access methods, and also
// has an embedded DB_INFO object named "info" used for setting configuration
// parameters and flags prior to creation of the database.  See the docstring
// for the DB_INFO object for details.
//
// The Db object must be opened before any other methods can be called.  The
// only thing that can be done before opening is setting options and flags
// in the info object.  For example:
//
//      import db
//      env = db.DbEnv()
//      env.open(...)
//      data = db.Db(env)
//      data.set_db_pagesize(4096)
//      data.open("datafile", db.DB_BTREE, db.DB_CREATE)
//
// The Db class supports a dictionary-like interface, including the len, keys,
// has_attr methods, as well as the item reference, item assigment and item
// deletion.  Dictionary access methods can be involved in transactions by
// using the autoTrans functions.
//
// Various types of database files can be created, based on a flag to the
// open method.  The types are:
//
//  DB_BTREE
//       The btree data structure is a sorted, balanced tree structure storing
//       associated key/data pairs.  Searches, inserions, and deletions in the
//       btree will all complete in O(lg base N) where base is the average
//       number of keys per page.  Often, inserting ordered data into btrees
//       results in pages that are half-full.  This implementation has been
//       modified to make ordered (or inverse ordered) insertion the best case,
//       resulting in nearly perfect page space utilization.
//
//       Space freed by deleting key/data pairs from the database is never
//       reclaimed from the filesystem, although it is reused where possible.
//       This means that the btree storage structure is grow-only.  If
//       sufficiently many keys are deleted from a tree that shrinking the
//       underlying database file is desirable, this can be accomplished by
//       creating a new tree from a scan of the existing one.
//
//  DB_HASH
//       The hash data structure is an extensible, dynamic hashing scheme,
//       able to store variable length key/data pairs.
//
//  DB_RECNO
//       The recno access method provides support for fixed and variable length
//       records, optionally backed by a flat text (byte stream) file.  Both
//       fixed and variable length records are accessed by their logical record
//       number.
//
//       It is valid to create a record whose record number is more than one
//       greater than the last record currently in the database.  For example,
//       the creation of record number 8, when records 6 and 7 do not yet
//       exist, is not an error. However, any attempt to retrieve such records
//       (e.g., records 6 and 7) will raise db.error with a value of
//       DB_KEYEMPTY.
//
//       Deleting a record will not, by default, renumber records following the
//       deleted record (see DB_RENUMBER in the DB_INFO class for more
//       information).  Any attempt to retrieve deleted records will raise
//       db.error with a value of DB_KEYEMPTY.
%name(Db) struct MyDB {

    %addmethods {

        MyDB(PyObject *pyDbEnv) {
            int err;
            struct MyDB* self = (struct MyDB*)PyMem_Malloc(sizeof(struct MyDB));

            if (!self) {
                PyErr_SetString(PyExc_MemoryError, "PyMem_Malloc failed");
                RETURN_PASS();
            }
            memset(self, 0, sizeof(struct MyDB));
            self->size = -1;
            self->closed = 1;
            self->flags = 0;

            // be sure we got a MyDB_ENV object
#ifdef SWIG13a5
            // for SWIG v1.3a5 do this:
            if (SWIG_ConvertPtr(pyDbEnv, (void **) &self->myenv,
                                SWIGTYPE_p_MyDB_ENV, 0))   // the 0 flag means we set the error ourself
#else
            // for SWIG v1.1-883 do this:
            if (SWIG_GetPtrObj(pyDbEnv, (void **) &self->myenv,
                                "_struct_MyDB_ENV_p"))
#endif
            {
                PyMem_Free(self);
                PyErr_SetString(PyExc_TypeError,
                        "DbEnv object expected in argument 1");
                RETURN_PASS();
            }

            // keep a reference to our python DbEnv object
            Py_INCREF(pyDbEnv);
            self->myenvobj = pyDbEnv;

            err = db_create(&self->db, self->myenv->db_env, 0);
            RETURN_IF_ERR();

            return self;
        }

        ~MyDB() {
            if (!self->closed) {
                MYDB_BEGIN_ALLOW_THREADS;
                self->db->close(self->db, 0);
                MYDB_END_ALLOW_THREADS;
            }
            if (self->myenvobj) {
                Py_DECREF(self->myenvobj);
                self->myenvobj = NULL;
                self->myenv = NULL;
            }
            PyMem_Free(self);
        }

        // Db.set_cachesize(gbytes=0, bytes=0, ncache=0)
        //
        // Set the size of the database's shared memory buffer pool,
        // i.e., the cache, to gbytes gigabytes plus bytes. The
        // cache should be the size of the normal working data set of the
        // application, with some small amount of additional
        // memory for unusual situations. (Note, the working set is
        // not the same as the number of simultaneously referenced pages,
        // and should be quite a bit larger!) 
        PyObject* set_cachesize(int gbytes=0, int bytes=0, int ncache=0) {
            int err = self->db->set_cachesize(self->db, gbytes, bytes, ncache);
            RETURN_IF_ERR();
            RETURN_NONE();
        }

        // Db.set_lorder(integer)
        //
        // Set the byte order for integers in the stored database metadata.
        // The number should represent the order as an integer, for example,
        // big endian order is the number 4,321, and little endian order is
        // the number 1,234. If lorder is not explicitly set, the host order
        // of the machine where the Berkeley DB library was compiled is used.
        //
        // The value of lorder is ignored except when databases are being
        // created.
        PyObject* set_lorder(int lorder) {
            int err = self->db->set_lorder(self->db, lorder);
            RETURN_IF_ERR();
            RETURN_NONE();
        }

        // Db.set_pagesize(integer)
        //
        // Set the size of the pages used to hold items in the database,
        // in bytes. The minimum page size is 512 bytes and the maximum
        // page size is 64K bytes. If the page size is not explicitly set,
        // one is selected based on the underlying filesystem I/O block
        // size. The automatically selected size has a lower limit of 512
        // bytes and an upper limit of 16K bytes.
        PyObject* set_pagesize(int pagesize) {
            int err = self->db->set_pagesize(self->db, pagesize);
            RETURN_IF_ERR();
            RETURN_NONE();
        }

        // Db.set_bt_minkey(integer)
        //
        // Set the minimum number of keys that will be stored on any single
        // Btree page.
        PyObject* set_bt_minkey(int minkey) {
            int err = self->db->set_bt_minkey(self->db, minkey);
            RETURN_IF_ERR();
            RETURN_NONE();
        }

        // Db.set_h_ffactor(integer)
        //
        // Set the desired density within the hash table.
        //
        // The density is an approximation of the number of keys allowed to
        // accumulate in any one bucket, determining when the hash table
        // grows or shrinks. If you know the average sizes of the keys
        // and data in your dataset, setting the fill factor can enhance
        // performance. A reasonable rule computing fill factor is to set
        // it to:
        //
        // (pagesize - 32) / (average_key_size + average_data_size + 8)
        //
        // If no value is specified, the fill factor will be selected
        // dynamically as pages are filled.
        PyObject* set_h_ffactor(int ffactor) {
            int err = self->db->set_h_ffactor(self->db, ffactor);
            RETURN_IF_ERR();
            RETURN_NONE();
        }

        // Db.set_h_nelem(integer)
        //
        // Set an estimate of the final size of the hash table.
        //
        // If not set or set too low, hash tables will still expand
        // gracefully as keys are entered, although a slight performance
        // degradation may be noticed.
        PyObject* set_h_nelem(int nelem) {
            int err = self->db->set_h_nelem(self->db, nelem);
            RETURN_IF_ERR();
            RETURN_NONE();
        }

        // Db.set_re_delim(integer)
        //
        // Set the delimiting byte used to mark the end of a record in the
        // backing source file for the Recno access method.
        //
        // This byte is used for variable length records, if the re_source
        // file is specified. If the re_source file is specified and no
        // delimiting byte was specified, <newline> characters (i.e. ASCII
        // 0x0a) are interpreted as end-of-record markers.
        PyObject* set_re_delim(int delim) {
            int err = self->db->set_re_delim(self->db, delim);
            RETURN_IF_ERR();
            RETURN_NONE();
        }

        // Db.set_re_len(integer)
        //
        // For the Queue access method, specify that the records are of
        // length re_len.
        //
        // For the Recno access method, specify that the records are
        // fixed-length, not byte delimited, and are of length re_len.
        //
        // Any records added to the database that are less than re_len
        // bytes long are automatically padded (see DB->set_re_pad for
        // more information).
        PyObject* set_re_len(int len) {
            int err = self->db->set_re_len(self->db, len);
            RETURN_IF_ERR();
            RETURN_NONE();
        }

        // Db.set_re_pad(string)
        //
        // Set the padding character for short, fixed-length records for the
        // Queue and Recno access methods.  If no pad character is specified,
        // <space> characters (i.e., ASCII 0x20) are used for padding.
        // The DB->set_re_pad interface may only be used to configure
        // Berkeley DB before the DB->open interface is called.
        //
        // The first character of the given string will be used.
        PyObject* set_re_pad(char *pad) {
            int err = self->db->set_re_pad(self->db, *pad);
            RETURN_IF_ERR();
            RETURN_NONE();
        }

        // Db.set_re_source(string)
        //
        // Set the underlying source file for the Recno access method. The
        // purpose of the re_source value is to provide fast access and
        // modification to databases that are normally stored as flat
        // text files.
        //
        // If the re_source field is set, it specifies an underlying flat
        // text database file that is read to initialize a transient record
        // number index. In the case of variable length records, the records
        // are separated as specified by DB->set_re_delim. For example,
        // standard UNIX byte stream files can be interpreted as a sequence
        // of variable length records separated by <newline> characters.
        //
        // In addition, when cached data would normally be written back to
        // the underlying database file (e.g., the DB->close or DB->sync
        // methods are called), the in-memory copy of the database will be
        // written back to the re_source file.
        PyObject* set_re_source(char* re_source) {
            int err = self->db->set_re_source(self->db, re_source);
            RETURN_IF_ERR();
            RETURN_NONE();
        }

        // Db.set_flags(flags)
        //
        // Calling Db->set_flags is additive, there is no way to clear flags.
        //
        // The flags value must be set to 0 or by bitwise inclusively OR'ing
        // together one or more of the following values.
        //
        //Btree
        //
        // The following flags may be specified for the Btree access method:
        // DB_DUP
        //    Permit duplicate data items in the tree, i.e. insertion when
        //    the key of the key/data pair being inserted already exists in
        //    the tree will be successful. The ordering of duplicates in the
        //    tree is determined by the order of insertion, unless the
        //    ordering is otherwise specified by use of a cursor or a
        //    duplicate comparison function. It is an error to specify both
        //    DB_DUP and DB_RECNUM.
        // DB_DUPSORT
        //    Sort duplicates within a set of data items. If the application
        //    does not specify a comparison function using the
        //    DB->set_dup_compare function, a default, lexical comparison
        //    will be used.
        //    Specifying that duplicates are to be sorted changes the
        //    behavior of the DB->put operation as well as the
        //    DBcursor->c_put operation when the DB_KEYFIRST, DB_KEYLAST and
        //    DB_CURRENT flags are specified.
        // DB_RECNUM
        //    Support retrieval from the Btree using record numbers. For more
        //    information, see the DB_GET_RECNO flag to the DB->get and
        //    DBcursor->c_get methods.
        //    Logical record numbers in Btree databases are mutable in the
        //    face of record insertion or deletion. See the DB_RENUMBER flag
        //    in the Recno access method information for further discussion.
        //    Maintaining record counts within a Btree introduces a serious
        //    point of contention, namely the page locations where the record
        //    counts are stored. In addition, the entire tree must be locked
        //    during both insertions and deletions, effectively
        //    single-threading the tree for those operations. Specifying
        //    DB_RECNUM can result in serious performance degradation for
        //    some applications and data sets.
        //    It is an error to specify both DB_DUP and DB_RECNUM.
        // DB_REVSPLITOFF
        //    Turn off reverse splitting in the Btree. As pages are emptied
        //    in a database, the Berkeley DB Btree implementation attempts to
        //    coalesce empty pages into higher-level pages in order to keep
        //    the tree as small as possible and minimize tree search time.
        //    This can hurt performance in applications with cyclical data
        //    demands, that is, applications where the database grows and
        //    shrinks repeatedly. For example, because Berkeley DB does
        //    page-level locking, the maximum level of concurrency in a
        //    database of 2 pages is far smaller than that in a database of
        //    100 pages, and so a database that has shrunk to a minimal size
        //    can cause severe deadlocking when a new cycle of data insertion
        //    begins.
        //Hash
        //
        // The following flags may be specified for the Hash access method:
        // DB_DUP
        //    Permit duplicate data items in the tree, i.e. insertion when
        //    the key of the key/data pair being inserted already exists in
        //    the tree will be successful. The ordering of duplicates in the
        //    tree is determined by the order of insertion, unless the
        //    ordering is otherwise specified by use of a cursor or a
        //    duplicate comparison function.
        // DB_DUPSORT
        //    Sort duplicates within a set of data items. If the application
        //    does not specify a comparison function using the
        //    DB->set_dup_compare function, a default, lexical comparison
        //    will be used.
        //    Specifying that duplicates are to be sorted changes the
        //    behavior of the DB->put operation as well as the
        //    DBcursor->c_put operation when the DB_KEYFIRST, DB_KEYLAST and
        //    DB_CURRENT flags are specified.
        //
        //Queue
        //
        // There are no additional flags that may be specified for the Queue
        // access method.
        //
        //Recno
        //
        // The following flags may be specified for the Recno access method:
        // DB_RENUMBER
        //    Specifying the DB_RENUMBER flag causes the logical record
        //    numbers to be mutable, and change as records are added to and
        //    deleted from the database. For example, the deletion of record
        //    number 4 causes records numbered 5 and greater to be renumbered
        //    downward by 1. If a cursor was positioned to record number 4
        //    before the deletion, it will reference the new record number 4,
        //    if any such record exists, after the deletion. If a cursor was
        //    positioned after record number 4 before the deletion, it will
        //    be shifted downward 1 logical record, continuing to reference
        //    the same record as it did before.
        //    Using the DB->put or DBcursor->c_put interfaces to create new
        //    records will cause the creation of multiple records if the
        //    record number is more than one greater than the largest record
        //    currently in the database. For example, creating record 28,
        //    when record 25 was previously the last record in the database,
        //    will create records 26 and 27 as well as 28. Attempts to
        //    retrieve records that were created in this manner will result
        //    in an error return of DB_KEYEMPTY.
        //    If a created record is not at the end of the database, all
        //    records following the new record will be automatically
        //    renumbered upward by 1. For example, the creation of a new
        //    record numbered 8 causes records numbered 8 and greater to be
        //    renumbered upward by 1. If a cursor was positioned to record
        //    number 8 or greater before the insertion, it will be shifted
        //    upward 1 logical record, continuing to reference the same
        //    record as it did before.
        //    For these reasons, concurrent access to a Recno database with
        //    the DB_RENUMBER flag specified may be largely meaningless,
        //    although it is supported.
        // DB_SNAPSHOT
        //    This flag specifies that any specified re_source file be read
        //    in its entirety when DB->open is called. If this flag is not
        //    specified, the re_source file may be read lazily.
        PyObject* set_flags(long flags) {
            int err = self->db->set_flags(self->db, flags);
            RETURN_IF_ERR();
            RETURN_NONE();
        }


        // Db.open(filename, type=DB_UNKNOWN, flags=0, mode=0660)
        //
        // This method opens the database represented by file for both reading
        // and writing by default.  Note, while most of the access methods use
        // file as the name of an underlying file on disk, this is not
        // guaranteed.  Also, calling open is a reasonably expensive operation.
        // (This is based on a model where the DBMS keeps a set of files open
        // (for a long time rather than opening and closing them on each query.)
        //
        // The type argument must be set to one of DB_BTREE, DB_HASH, DB_RECNO
        // or DB_UNKNOWN.  If type is DB_UNKNOWN, the database must already
        // exist and open will then determine if it is of type DB_BTREE,
        // DB_HASH or DB_RECNO.
        //
        // The flags and mode arguments specify how files will be
        // opened and/or created when they don't already exist.  The
        // flags value is specified by or'ing together one or more of
        // the following values:
        //
        //  DB_CREATE
        //      Create any underlying files, as necessary.  If the
        //      files do not already exist and the DB_CREATE flag is
        //      not specified, the call will fail.
        //
        //  DB_NOMMAP
        //      Do not memory-map this file.
        //
        //  DB_RDONLY
        //      Open the database for reading only.  Any attempt to write the
        //      database using the access methods will fail regardless of the
        //      actual permissions of any underlying files.
        //
        //  DB_THREAD
        //      Cause the DB handle returned by the open function to be useable
        //      by multiple threads within a single address space, i.e., to be
        //      "free-threaded".
        //
        //  DB_TRUNCATE
        //      "Truncate" the database if it exists, i.e., behave as if the
        //      database were just created, discarding any previous contents.
        //
        // All files created by the access methods are created with mode mode
        // (see chmod) and modified by the process' umask value at the
        // time of creation.  The group ownership of created files is based on
        // the system and directory defaults.
        PyObject* open(char *filename, int type=DB_UNKNOWN, long flags=0, int mode=0660) {
            int err;
            MYDB_BEGIN_ALLOW_THREADS;
            err = self->db->open(self->db, filename, NULL,
                    type, flags, mode);
            MYDB_END_ALLOW_THREADS;
            if (err) self->db->close(self->db, 0);
            RETURN_IF_ERR();
            self->closed = 0;
            self->flags = flags;
            RETURN_NONE();
        }

        // Db.upgrade(string file, flags=0)
        //   Upgrades all databases included in the file filename if necessary.
        //   Upgrades are done in place and are destructive.  Unlike other
        //   BerkeleyDB operations, upgrades may only be done on a system
        //   with the same byte-order as the database.
        //   ** Backups should be made before databases are upgraded! **
        PyObject * upgrade(char *filename, long flags=0) {
            int err = self->db->upgrade(self->db, filename, flags);
            RETURN_IF_ERR();
            RETURN_NONE();
        }

        // Db.type()
        //
        // The type of the underlying access method (and file format).  Set to
        // one of DB_BTREE, DB_HASH or DB_RECNO.  This field may be used to
        // determine the type of the database after a return from open with
        // the type argument set to DB_UNKNOWN.
        int type() {
            int t;
            MYDB_BEGIN_ALLOW_THREADS;
            t = self->db->get_type(self->db);
            MYDB_END_ALLOW_THREADS;
            return t;
        }

        // Db.close(flags=0)
        //
        // A pointer to a function to flush any cached information to disk,
        // close any open cursors, free any allocated resources, and close
        // any underlying files.  Since key/data pairs are cached in memory,
        // failing to sync the file with the close or sync method may result
        // in inconsistent or lost information.  (When the DB object's
        // reference count reaches zero, the close method is called, but you
        // should probably always call the close method just in case...)
        //
        // The flags parameter must be set to DB_NOSYNC, which specifies to
        // not flush cached information to disk.  The DB_NOSYNC flag is a
        // dangerous option.  It should only be set if the application is
        // doing logging (with or without transactions) so that the database
        // is recoverable after a system or application crash, or if the
        // database is always generated from scratch after any system or
        // application crash.
        //
        // When multiple threads are using the DB handle concurrently, only
        // a single thread may call the DB handle close function.
        PyObject* close(long flags=0) {
            int err = 0;
            if (!self->closed) {
                MYDB_BEGIN_ALLOW_THREADS;
                err = self->db->close(self->db, flags);
                MYDB_END_ALLOW_THREADS;
            }
            RETURN_IF_ERR();
            self->closed = 1;
            RETURN_NONE();
        }


        // Db.cursor(txn=None, flags=0)
        //
        // Creates and returns a Dbc object used to provide sequential access
        // to a database.
        //
        // If the file is being accessed under transaction protection, the
        // txn parameter is a transaction ID returned from beginTrans,
        // otherwise, the autoTrans (if any) is used.  If transaction
        // protection is enabled, cursors must be opened and closed within
        // the context of a transaction, and the txnid parameter specifies
        // the transaction context in which the cursor may be used.
        //
        // The  flags value is specified by or'ing together one or more of
        // the following values:
        //
        //   DB_WRITECURSOR
        //      Specify that the cursor will be used to update the
        //      database. This flag should only be set when the DB_INIT_CDB
        //      flag was specified to db_env->open.
        %new struct MyDBC* cursor(struct __db_txn* txn=NULL, long flags=0) {
            int err;
            DBC* dbc;
            struct MyDBC* retval;
            if (!txn) txn = self->myenv->autoTrans;
            MYDB_BEGIN_ALLOW_THREADS;
            err = self->db->cursor(self->db, txn, &dbc, flags);
            MYDB_END_ALLOW_THREADS;
            RETURN_IF_ERR();
            // TODO Py_INCREF on the Db object (also DECREF in the cursor's destructor)
            retval = (struct MyDBC*)PyMem_Malloc(sizeof(struct MyDBC));
            retval->dbc = dbc;
            retval->mydb = self;
            retval->closed = 0;
            return retval;              // Let SWIG turn it into a python Dbc
        }

        // Db.delete(key, txn=None)
        //
        // The key/data pair associated with the specified key is discarded
        // from the database.  In the presence of duplicate key values, all
        // records associated with the designated key will be discarded.
        //
        // If the file is being accessed under transaction protection, the
        // txn parameter is a transaction ID returned from beginTrans,
        // otherwise, the autoTrans (if any) is used.
        //
        // The delete method raises db.error with a value of DB_NOTFOUND if
        // the specified key did not exist in the file.
        PyObject* delete(DBT* keyp, struct __db_txn* txn=NULL) {
            int err;
            if (!txn) txn = self->myenv->autoTrans;
            MYDB_BEGIN_ALLOW_THREADS;
            err = self->db->del(self->db, txn, keyp, 0);
            MYDB_END_ALLOW_THREADS;
            RETURN_IF_ERR();
            self->size = -1;
            RETURN_NONE();
        }

        // Db.get(key, txn=None, flags=0)
        //
        // This method performs keyed retrievel from the database.  The data
        // value coresponding to the given key is returned.
        //
        // In the presence of duplicate key values, get will return the
        // first data item for the designated key. Duplicates are sorted by
        // insert order except where this order has been overwritten by
        // cursor operations. Retrieval of duplicates requires the use of
        // cursor operations.
        //
        // If the file is being accessed under transaction protection, the
        // txn parameter is a transaction ID returned from beginTrans,
        // otherwise, the autoTrans (if any) is used.
        //
        // If the database is a recno database and the requested key exists,
        // but was never explicitly created by the application or was later
        // deleted, the get method raises db.error with a value of
        // DB_KEYEMPTY.  Otherwise, if the requested key isn't in the
        // database, the get method returns None.
        PyObject* get(DBT* keyp, struct __db_txn* txn=NULL, long flags=0) {
            int err;
            DBT data;
            PyObject *retval = NULL;
            // XXX RECNO databases could use another get interface
            // that accepts an integer instead of a string.  (for now,
            // RECNO users need to put the 32-bit integer into a
            // string before calling get)
            memset(&data, 0, sizeof(DBT));
            if (!txn) txn = self->myenv->autoTrans;
            if (CHECK_DBFLAG(self, DB_THREAD)) {
                // Tell BerkeleyDB to malloc the return value (thread safe)
                data.flags = DB_DBT_MALLOC;
            }
            MYDB_BEGIN_ALLOW_THREADS;
            err = self->db->get(self->db, txn, keyp, &data, flags);
            MYDB_END_ALLOW_THREADS;

            // emulate Python dict.get() behavior, return None if the key was not found
            if (err == DB_NOTFOUND) {
                Py_INCREF(Py_None);
                retval = Py_None;
            } else {
                RETURN_IF_ERR();
            }
            if (retval == NULL) {  // if we're not returning Py_None
                retval = PyString_FromStringAndSize((char*)data.data, data.size);
            }
            if ((CHECK_DBFLAG(self, DB_THREAD)) && (data.data != NULL)) {
                free(data.data);
            }
            return retval;
        }

        // Db.getRec(recno, txn=None)
        //
        // Retrieve a specific numbered record from a database.  Both the
        // key and data item will be returned as a tuple.  In order to use
        // this method, the underlying database must be of type btree, and it
        // must have been created with the DB_RECNUM flag.
        //
        // If the file is being accessed under transaction protection, the
        // txn parameter is a transaction ID returned from beginTrans,
        // otherwise, the autoTrans (if any) is used.
        PyObject* getRec(db_recno_t recno, struct __db_txn* txn=NULL) {
            int err;
            DBT key;
            DBT data;
            PyObject *retval;
            key.data = &recno;
            key.size = sizeof(db_recno_t);
            key.ulen = key.size;
            key.flags = DB_DBT_USERMEM;
            memset(&data, 0, sizeof(data));
            if (CHECK_DBFLAG(self, DB_THREAD)) {
                // Tell BerkeleyDB to malloc the return value (thread safe)
                data.flags = DB_DBT_MALLOC;
            }
            if (!txn) txn = self->myenv->autoTrans;
            MYDB_BEGIN_ALLOW_THREADS;
            err = self->db->get(self->db, txn, &key, &data, DB_SET_RECNO);
            MYDB_END_ALLOW_THREADS;
            RETURN_IF_ERR();
            retval = Py_BuildValue("s#s#", key.data, key.size,
                                         data.data, data.size);
            if ((CHECK_DBFLAG(self, DB_THREAD)) && (data.data != NULL)) {
                free(data.data);
            }
            return retval;
        }

        // Db.fd()
        //
        // Returns a file descriptor representative of the underlying
        // database.  A file descriptor referencing the same file will be
        // returned to all processes that call db_open with the same file
        // argument. This file descriptor may be safely used as an argument
        // to the fcntl and flock locking functions. The file descriptor is
        // not necessarily associated with any of the underlying files used
        // by the access method.
        //
        // The fd function only supports a coarse-grained form of locking.
        // Applications should use the lock manager where possible.
        PyObject* fd() {
            int err;
            int the_fd;
            MYDB_BEGIN_ALLOW_THREADS;
            err = self->db->fd(self->db, &the_fd);
            MYDB_END_ALLOW_THREADS;
            RETURN_IF_ERR();
            return PyInt_FromLong(the_fd);
        }

        // Db.put(key, data, txn=None, flags=0)
        //
        // A method to store key/data pairs in the database.  If the
        // database supports duplicates, the put method adds the new data
        // value at the end of the duplicate set.
        //
        // If the file is being accessed under transaction protection, the
        // txn parameter is a transaction ID returned from beginTrans,
        // otherwise, the autoTrans (if any) is used.
        //
        // The flags value is specified by or'ing together one or more of
        // the following values:
        //
        // DB_APPEND
        //      Append the key/data pair to the end of the database.  For
        //      DB_APPEND to be specified, the underlying database must be
        //      of type recno.  The record number allocated to the record is
        //      returned.
        //
        // DB_NOOVERWRITE
        //      Enter the new key/data pair only if the key does not already
        //      appear in the database.
        //
        // The default behavior of the put method is to enter the new
        // key/data pair, replacing any previously existing key if
        // duplicates are disallowed, or to add a duplicate entry if
        // duplicates are allowed.  Even if the designated database allows
        // duplicates, a call to put with the DB_NOOVERWRITE flag set will
        // fail if the key already exists in the database.
        //
        // This method raises db.error with a value of DB_KEYEXIST if the
        // DB_NOOVERWRITE flag was set and the key already exists in the
        // file.
        PyObject* put(DBT* keyp, DBT* datap, struct __db_txn* txn=NULL, long flags=0) {
            int err;
            if (!txn) txn = self->myenv->autoTrans;
            MYDB_BEGIN_ALLOW_THREADS;
            err = self->db->put(self->db, txn, keyp, datap, flags);
            MYDB_END_ALLOW_THREADS;
            RETURN_IF_ERR();
            self->size = -1;
                                // XXX if RECNO type, return as integer
            return Py_BuildValue("s#", keyp->data, keyp->size);
        }

        // Db.sync()
        //
        // This method flushes any cached information to disk.
        PyObject* sync() {
            int err;
            MYDB_BEGIN_ALLOW_THREADS;
            err = self->db->sync(self->db, 0);
            MYDB_END_ALLOW_THREADS;
            RETURN_IF_ERR();
            RETURN_NONE();
        }


        //-----------------------------------------------------
        // Dictionary access routines
        //-----------------------------------------------------

        PyObject* __len__() {
            int err;
            DBT key;
            DBT data;
            DBC *cursor = NULL;
            long size = 0;

            if (self->size < 0) {       // recompute
                memset(&key, 0, sizeof(DBT));
                memset(&data, 0, sizeof(DBT));
                MYDB_BEGIN_ALLOW_THREADS;
                err = self->db->cursor(self->db, self->myenv->autoTrans, &cursor, 0);
                MYDB_END_ALLOW_THREADS;
                RETURN_IF_ERR();
                while (1) {
                    if (CHECK_DBFLAG(self, DB_THREAD)) {
                        // XXX tons of mallocs are highly inefficient
                        key.flags = DB_DBT_REALLOC;
                        data.flags = DB_DBT_REALLOC;
                    }
                    MYDB_BEGIN_ALLOW_THREADS;
                    err = cursor->c_get(cursor, &key, &data, DB_NEXT);
                    MYDB_END_ALLOW_THREADS;
                    if (err != 0)
                        break;

                    size += 1;
                }
                if (CHECK_DBFLAG(self, DB_THREAD)) {
                    if (key.data != NULL) free(key.data);
                    if (data.data != NULL) free(data.data);
                }
                if (err < 0 && err != DB_NOTFOUND) {
                    PyErr_SetObject(dbError, makeDbError(err));
                    cursor->c_close(cursor);
                    RETURN_PASS();
                }
                self->size = size;
            }
            if (cursor)
                cursor->c_close(cursor);
            return PyInt_FromLong(self->size);
        }


        PyObject* __getitem__(PyObject* pyKey) {
            int err;
            DBT key;
            DBT data;
            PyObject *retval;

            memset(&key, 0, sizeof(key));
            if (!PyArg_Parse(pyKey, "s#", &key.data, &key.size)) {
                PyErr_SetString(PyExc_TypeError, "Key must be a string.");
                RETURN_PASS();
            }

            memset(&data, 0, sizeof(DBT));
            if (CHECK_DBFLAG(self, DB_THREAD)) {
                // Tell BerkeleyDB to malloc the return value (thread safe)
                data.flags = DB_DBT_MALLOC;
            }
            MYDB_BEGIN_ALLOW_THREADS;
            err = self->db->get(self->db, self->myenv->autoTrans, &key, &data, 0);
            MYDB_END_ALLOW_THREADS;
            if (err) {
                if (err == DB_NOTFOUND)
                    PyErr_SetObject(PyExc_KeyError, pyKey);
                else
                    PyErr_SetObject(dbError, makeDbError(err));
                RETURN_PASS();
            }

            retval = PyString_FromStringAndSize((char*)data.data, data.size);
            if (CHECK_DBFLAG(self, DB_THREAD) && (data.data != NULL)) {
                free(data.data);  // free any malloc'd return value
            }

            return retval;
        }

        PyObject* __setitem__(DBT* keyp, DBT* datap) {
            return MyDB_put(self, keyp, datap, self->myenv->autoTrans, 0);
        }

        PyObject* __delitem__(DBT* keyp) {
            return MyDB_delete(self, keyp, self->myenv->autoTrans);
        }


        PyObject* keys() {
            int err;
            DBT key;
            DBT data;
            DBC *cursor;
            PyObject* list;
            PyObject* item;

            list = PyList_New(0);
            if (list == NULL) {
                PyErr_SetString(PyExc_MemoryError, "PyList_New failed");
                RETURN_PASS();
            }
            memset(&key, 0, sizeof(DBT));
            memset(&data, 0, sizeof(DBT));
            MYDB_BEGIN_ALLOW_THREADS;
            err = self->db->cursor(self->db, self->myenv->autoTrans, &cursor, 0);
            MYDB_END_ALLOW_THREADS;
            RETURN_IF_ERR();

            while (1) {
                if (CHECK_DBFLAG(self, DB_THREAD)) {
                    // XXX tons of mallocs are highly inefficient
                    key.flags = DB_DBT_REALLOC;
                    data.flags = DB_DBT_REALLOC;
                }
                MYDB_BEGIN_ALLOW_THREADS;
                err = cursor->c_get(cursor, &key, &data, DB_NEXT);
                MYDB_END_ALLOW_THREADS;
                if ((err != ENOMEM) && (err != 0)) {
                    break;
                }

                item = PyString_FromStringAndSize((char*)key.data, key.size);
                if (item == NULL) {
                    Py_DECREF(list);
                    PyErr_SetString(PyExc_MemoryError,
                            "PyString creation failed");
                    list = NULL;
                    goto done;
                }
                PyList_Append(list, item);
                Py_DECREF(item);
            }
            if (err < 0 && err != DB_NOTFOUND) {
                PyErr_SetObject(dbError, makeDbError(err));
                Py_DECREF(list);
                list = NULL;
                goto done;
            }
        done:
            if (CHECK_DBFLAG(self, DB_THREAD)) {
                if (key.data != NULL) free(key.data);
                if (data.data != NULL) free(data.data);
            }
            cursor->c_close(cursor);
            if (list == NULL) {
                RETURN_PASS();
            }
            return list;
        }


        // ****  Don't forget items() and values()...

        PyObject* has_key(DBT* keyp) {
            int err;
            DBT data;
            memset(&data, 0, sizeof(DBT));

            // this causes ENOMEM to be returned when the db has the key
            data.ulen = 0;
            data.data = NULL;
            data.flags = DB_DBT_USERMEM;

            MYDB_BEGIN_ALLOW_THREADS;
            err = self->db->get(self->db, self->myenv->autoTrans, keyp, &data, 0);
            MYDB_END_ALLOW_THREADS;
            return PyInt_FromLong((err == ENOMEM) || (err == 0));
        }
    }
};

//---------------------------------------------------------------------------

%pragma(python) include="db_version.py"
%pragma(python) include="db_thread.py"
%pragma(python) include="db_compat.py"

//----------------------------------------------------------------------

%init %{
    dbError = PyString_FromString("db.error");
    PyDict_SetItemString(d,"error", dbError);
%}


//----------------------------------------------------------------------


