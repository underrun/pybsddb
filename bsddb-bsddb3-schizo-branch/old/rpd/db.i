/************************************************************************
               Copyright (c) 1997 by Total Control Software
                         All Rights Reserved
------------------------------------------------------------------------

Module Name:    db.i

Description:    SWIG interface file for the BSD DB library.

Creation Date:  8/2/97 5:02:10PM

#
# License:      This is free software.  You may use this software for any
#               purpose including modification/redistribution, so long as
#               this header remains intact and that you do not claim any
#               rights of ownership or authorship of this software.  This
#               software has been tested, but no warranty is expressed or
#               implied.

************************************************************************/

%module db
%{
#include "db.h"
%}

%include typemaps.i

//---------------------------------------------------------------------------

// Version number of this module
#define __version__ "1.2.0"

//---------------------------------------------------------------------------

    /*
     * release the python global lock so that other threads run
     * while we execute the wrapped function.
     */

// *** Seems to cause problems...

//%except(python) {
//    Py_BEGIN_ALLOW_THREADS;
//    $function
//    Py_END_ALLOW_THREADS;
//}

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
// so SWIG will use the symbolic name instead of the macro value.  This protects me
// a bit from those values changing without my knowledge...
enum {
        DB_MAX_PAGES,
        DB_MAX_RECORDS,

        DB_CREATE,
        DB_NOMMAP,
        DB_THREAD,

        DB_INIT_CDB,
        DB_INIT_LOCK,
        DB_INIT_LOG,
        DB_INIT_MPOOL,
        DB_INIT_TXN,
        DB_MPOOL_PRIVATE,
        DB_RECOVER,
        DB_RECOVER_FATAL,
        DB_TXN_NOSYNC,
        DB_USE_ENVIRON,
        DB_USE_ENVIRON_ROOT,

        DB_EXCL,
        DB_RDONLY,
        DB_SEQUENTIAL,
        DB_TEMPORARY,
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

        DB_DELIMITER,
        DB_DUP,
        DB_FIXEDLEN,
        DB_PAD,
        DB_RECNUM,
        DB_RENUMBER,
        DB_SNAPSHOT,

        DB_AFTER,
        DB_APPEND,
        DB_BEFORE,
        DB_CHECKPOINT,
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
        DB_NOOVERWRITE,
        DB_NOSYNC,
        DB_PREV,
        DB_RECORDCOUNT,
        DB_SET,
        DB_SET_RANGE,
        DB_SET_RECNO,

        DB_OPFLAGS_MASK,
        DB_RMW,

        DB_INCOMPLETE,
        DB_KEYEMPTY,
        DB_KEYEXIST,
        DB_LOCK_DEADLOCK,
        DB_LOCK_NOTGRANTED,
        DB_LOCK_NOTHELD,
        DB_NOTFOUND,
        DB_RUNRECOVERY,


};


//----------------------------------------------------------------------
// Definition for the DB_INFO structure  (Only applicable items are here.)


//
// class DB_INFO
//
// Objects of this type are used for setting initialization options and flags
// for DB files upon their creation.  Each DB object has a DB_INFO object
// contained within it named "info" for the purpose of setting its options
// before it is opened the first time.  The following options are available,
// (all default to zero):
//
// db_cachesize (integer)
//        A suggested maximum size of the memory pool cache, in bytes.  If
//        db_cachesize is 0, an appropriate default is used.
//
//        Note, the minimum number of pages in the cache should be no less
//        than 10, and the access methods will fail if an insufficiently
//        large cache is specified.  In addition, for applications that
//        exhibit strong locality in their data access patterns,
//        increasing the size of the cache can significantly improve
//        application performance.
//
// db_lorder (integer)
//        The byte order for integers in the stored database metadata.  The
//        number should represent the order as an integer, for example, big
//        endian order is the number 4321, and little endian order is the
//        number 1234.  If db_lorder is 0, the host order of the machine where
//        the DB library was compiled is used.
//
//        The value of db_lorder is ignored except when databases are being
//        created.  If a database already exists, the byte order it uses is
//        determined when the file is read.
//
//        The access methods provide no guarantees about the byte ordering of
//        the application data stored in the database, and applications are
//        responsible for maintaining any necessary ordering.
//
// db_pagesize (integer)
//        The size of the pages used to hold items in the database, in bytes.
//        The minimum page size is 512 bytes and the maximum page size is 64K
//        bytes.  If db_pagesize is 0, a page size is selected based on the
//        underlying filesystem I/O block size.  The selected size has a lower
//        limit of 512 bytes and an upper limit of 16K bytes.
//
// bt_minkey (integer) BTREE only
//        The minimum number of keys that will be stored on any single
//        page. This value is used to determine which keys will be stored
//        on overflow pages, i.e. if a key or data item is larger than the
//        pagesize divided by the bt_minkey value, it will be stored on
//        overflow pages instead of in the page itself.  The bt_minkey
//        value specified must be at least 2; if bt_minkey is 0, a value of
//        2 is used.
//
// bt_maxkey (integer) BTREE only
//        The maximum number of keys that will be stored on any single page.
//
//
// h_ffactor (integer) HASH only
//        The desired density within the hash table.  It is an
//        approximation of the number of keys allowed to accumulate in
//        any one bucket, determining when the hash table grows or shrinks.
//        The default value is 0, indicating that the fill factor will be
//        selected dynamically as pages are filled.
//
// h_nelem (integer) HASH only
//        An estimate of the final size of the hash table.  If not set or
//        set too low, hash tables will expand gracefully as keys are
//        entered, although a slight performance degradation may be
//        noticed.  The default value is 1.
//
//
// re_delim (integer) RECNO only
//        For variable length records, if the re_source file is specified
//        and the DB_DELIMITER flag is set, the delimiting byte used to
//        mark the end of a record in the source file.  If the re_source
//        file is specified and the DB_DELIMITER flag is not set, <newline>
//        characters (i.e. "\\n", 0x0a) are interpreted as
//        end-of-record markers.
//
// re_len (integer) RECNO only
//        The length of a fixed-length record.
//
// re_pad (integer) RECNO only
//        For fixed length records, if the DB_PAD flag is set, the pad
//        character for short records.  If the DB_PAD flag is not set,
//        <space> characters (i.e., 0x20) are used for padding.
//
// re_source (string) RECNO only
//        The purpose of the re_source field is to provide fast access and
//        modification to databases that are normally stored as flat text
//        files.
//
//        If the re_source field is non-NULL, it specifies an underlying
//        flat text database file that is read to initialize a transient
//        record number index.  In the case of variable length records, the
//        records are separated by the byte value re_delim.  For example,
//        standard UNIX byte stream files can be interpreted as a sequence
//        of variable length records separated by <newline> characters.
//
//        In addition, when cached data would normally be written back to
//        the underlying database file (e.g., the close or sync functions
//        are called), the in-memory copy of the database will be written
//        back to the re_source file.
//
//        By default, the backing source file is read lazily, i.e., records
//        are not read from the file until they are requested by the
//        application.  If multiple processes (not threads) are accessing a
//        recno database concurrently and either inserting or deleting
//        records, the backing source file must be read in its entirety
//        before more than a single process accesses the database, and only
//        that process should specify the backing source file as part of
//        the db_open call. See the DB_SNAPSHOT flag below for more
//        information.
//
//        Reading and writing the backing source file specified by
//        re_source cannot be transactionally protected because it involves
//        filesystem operations that are not part of the DB transaction
//        methodology.  For this reason, if a temporary database is used to
//        hold the records, i.e., a NULL was specified as the file argument
//        to db_open, it is possible to lose the contents of the re_source
//        file, e.g., if the system crashes at the right instant. If a file
//        is used to hold the database, i.e., a file name was specified as
//        the file argument to db_open, normal database recovery on that
//        file can be used to prevent information loss, although it is
//        still possible that the contents of re_source will be lost if the
//        system crashes.
//
//        The re_source file must already exist (but may be zero-length)
//        when db_open is called.
//
//        For all of the above reasons, the re_source field is generally
//        used to specify databases that are read-only for DB
//        applications, and that are either generated on the fly by
//        software tools, or modified using a different mechanism, e.g., a
//        text editor.
//
//
// flags (integer)
//        May be set to a combination of the following flags or'ed together,
//        as appropriate for the access method (BTREE, HASH or RECNO).
//
//        DB_DUP (BTREE or HASH)
//            Permit duplicate keys in the tree, i.e. insertion when the
//            key of the key/data pair being inserted already exists in the
//            tree will be successful.  The ordering of duplicates in the
//            tree is determined by the order of insertion, unless the
//            ordering is otherwise specified by use of a cursor.  It is an
//            error to specify both DB_DUP and DB_RECNUM.
//
//        DB_RECNUM (BTREE)
//            Support retrieval from btrees using record numbers.  For
//            more information, see the DB.getRec and DBC.getRec methods.
//
//            Logical record numbers in btrees are mutable in the face of
//            record insertion or deletion.  See the DB_RENUMBER flag in
//            the RECNO section below for further discussion.
//
//            Maintaining record counts within a btree introduces a
//            serious point of contention, namely the page locations where
//            the record counts are stored.  In addition, the entire tree
//            must be locked during both insertions and deletions,
//            effectively single-threading the tree for those operations.
//            Specifying DB_RECNUM can result in serious performance
//            degradation for some applications and data sets.
//
//            It is an error to specify both DB_DUP and DB_RECNUM.
//
//        DB_DELIMITER (RECNO)
//            The re_delim field is set.
//
//        DB_FIXEDLEN (RECNO)
//            The records are fixed-length, not byte delimited.  The
//            structure element re_len specifies the length of the record,
//            and the structure element re_pad is used as the pad
//            character.
//
//            Any records added to the database that are less than re_len
//            bytes long are automatically padded. Any attempt to insert
//            records into the database that are greater than re_len bytes
//            long will cause the call to fail immediately and return an
//            error.
//
//         DB_PAD (RECNO)
//            The re_pad field is set.
//
//         DB_RENUMBER (RECNO)
//            Specifying the DB_RENUMBER flag causes the logical record
//            numbers to be mutable, and change as records are added to
//            and deleted from the database.  For example, the deletion of
//            record number 4 causes records numbered 5 and greater to be
//            renumbered downward by 1.  If a cursor was positioned to
//            record number 4 before the deletion, it will reference the
//            new record number 4, if any such record exists, after the
//            deletion. If a cursor was positioned after record number 4
//            before the deletion, it will be shifted downward 1 logical
//            record, continuing to reference the same record as it did
//            before.
//
//            Using the put methods to create new records will cause the
//            creation of multiple records if the record number is more than
//            one greater than the largest record currently in the database.
//            For example, creating record 28, when record 25 was previously
//            the last record in the database, will create records 26 and 27 as
//            well as 28.  Attempts to retrieve records that were created in
//            this manner will result in an error return of DB_KEYEMPTY.
//
//            If a created record is not at the end of the database, all
//            records following the new record will be automatically
//            renumbered upward by 1. For example, the creation of a new
//            record numbered 8 causes records numbered 8 and greater to
//            be renumbered upward by 1.  If a cursor was positioned to
//            record number 8 or greater before the insertion, it will be
//            shifted upward 1 logical record, continuing to reference the
//            same record as it did before.
//
//            For these reasons, concurrent access to a recno database
//            with the DB_RENUMBER flag specified may be largely
//            meaningless, although it is supported.
//
//         DB_SNAPSHOT (RECNO)
//            This flag specifies that any specified re_source file be read
//            in its entirety when db_open is called.  If this flag is not
//            specified, the re_source file may be read lazily.
//
%name(DB_INFO) struct __db_info {
        int db_lorder; /* Byte order. */
        size_t db_cachesize; /* Underlying cache size. */
        size_t db_pagesize; /* Underlying page size. */

        /* Btree access method. */
        int              bt_maxkey;     /* Maximum keys per page. */
        int              bt_minkey;     /* Minimum keys per page. */

        /* Hash access method. */
        unsigned int     h_ffactor;     /* Fill factor. */
        unsigned int     h_nelem;       /* Number of elements. */

        /* Recno access method. */
        int              re_pad;        /* Fixed-length padding byte. */
        int              re_delim;      /* Variable-length delimiting byte. */
        u_int32_t        re_len;        /* Length for fixed-length records. */
        char            *re_source;     /* Source file name. */

        u_int32_t        flags;
};



//----------------------------------------------------------------------
// And now some C code to help with the wrappers...

%{
static PyObject* dbError;             // Make an error variable for exceptions

typedef void (*AtExitFcn) ();


static DB_ENV*   db_env = NULL;
static DB_TXN*  autoTrans = NULL;
static int      atRefCnt = 0;
static int      doneAppinit = 0;

struct MyDB {
    DB*     db;
    DB_INFO info;
    long    size;
    int     closed;
};

struct MyDBC {
    DBC*            dbc;
    struct MyDB*    mydb;
    int             closed;
};

#define CHECK_ERR()      if (err) { PyErr_SetObject(dbError, makeDbError(err)); return NULL; }
#define RETURN_NONE()    Py_INCREF(Py_None); return Py_None;

#define GET_DBT(pyo, dbt)                                   \
    memset(&dbt, 0, sizeof(dbt));                           \
    if (!PyArg_Parse(pyo, "s#", &dbt.data, &dbt.size)) {    \
        PyErr_SetString(PyExc_TypeError,"Key and Data values must be of type string.");   \
        return NULL;                                        \
    }

/* make a nice error object to raise for errors. */
static PyObject* makeDbError(int err) {
    struct { int code; char* text; } errors[] = {
        { DB_INCOMPLETE,        "DB_INCOMPLETE: Sync didn't finish" },
        { DB_KEYEMPTY,          "DB_KEYEMPTY: The key/data pair was deleted or was never created" },
        { DB_KEYEXIST,          "DB_KEYEXIST: The key/data pair already exists" },
        { DB_LOCK_DEADLOCK,     "DB_LOCK_DEADLOCK: Locker killed to resolve deadlock" },
        { DB_LOCK_NOTGRANTED,   "DB_LOCK_NOTGRANTED: Lock unavailable, no-wait set" },
        { DB_LOCK_NOTHELD,      "DB_LOCK_NOTHELD: Lock not held by locker" },
        { DB_NOTFOUND,          "DB_NOTFOUND: Key/data pair not found (EOF)" },
        { DB_RUNRECOVERY,       "DB_RUNRECOVERY: PANIC!  Run recovery utilities"},
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
%}


//----------------------------------------------------------------------


//
// version()
//
// Returns a tuple of major, minor, and patch release numbers of the
// underlying DB library.
//
%name(version) char* db_version(int* T_OUTPUT, int* T_OUTPUT, int* T_OUTPUT);

%inline %{

    //
    // appinit(db_home, flags)
    //
    // The appinit function provides a simple way to initialize and configure the
    // DB environment.  It is not necessary that it be called, but it provides a
    // method of creating a consistent environment for processes using one or more
    // of the features of DB.
    //
    //      db_home     The database home directory.  Files named in DB.open are
    //                  relative to this directory.
    //
    //      flags       0 or any of the following flags, or'ed together:
    //
    //                  DB_CREATE
    //                    Cause subsystems to create any underlying files, as
    //                    necessary.
    //
    //                  DB_INIT_CDB
    //                    Initialize locking for the Berkeley DB Concurrent
    //                    Access Methods product. In this mode, Berkeley DB
    //                    provides multiple reader/single writer access. No
    //                    other locking should be specified (e.g., do not set
    //                    DB_INIT_LOCK). Access method calls are largely
    //                    unchanged when using the DB_INIT_CDB flag, although
    //                    any cursors through which update operations (e.g.,
    //                    DBcursor.put, DBcursor.delete) will be made, must
    //                    have the DB_RMW value set in the flags parameter to
    //                    the cursor call that creates the cursor. See
    //                    DB.cursor for more information.
    //
    //                  DB_INIT_LOCK
    //                    Initialize the lock subsystem.  This subsystem should
    //                    be used when multiple processes or threads are going to
    //                    be reading or writing a DB database, so that they do
    //                    not interfere with each other.  When the DB_INIT_LOCK
    //                    flag is specified, it is usually necessary to run the
    //                    deadlock detector, db_deadlock, as well.
    //
    //                  DB_INIT_LOG
    //                    Initialize the log subsystem. This subsystem is used
    //                    when recovery from application or system failure is
    //                    important.
    //
    //                  DB_INIT_MPOOL
    //                    Initialize the mpool subsystem. This subsystem is used
    //                    whenever the application is using the DB access methods
    //                    for any purpose.
    //
    //                  DB_INIT_TXN
    //                    Initialize the transaction subsystem. This subsystem is
    //                    used when atomicity of multiple operations and recovery
    //                    are important.  The DB_INIT_TXN flag implies the
    //                    DB_INIT_LOG flag.
    //
    //                  DB_MPOOL_PRIVATE
    //                    Create a private memory pool.  Ignored unless
    //                    DB_INIT_MPOOL is also specified.
    //
    //                  DB_NOMMAP
    //                    Do not map any files within this environment.  Ignored
    //                    unless DB_INIT_MPOOL is also specified.
    //
    //                  DB_RECOVER
    //                    Run normal recovery on this environment before opening it
    //                    for normal use.  If this flag is set, the DB_CREATE,
    //                    DB_INIT_TXN, and DB_INIT_LOG flags must also be set since
    //                    the regions will be removed and recreated.  For further
    //                    information, consult the man page for db_recover(1).
    //
    //                  DB_RECOVER_FATAL
    //                    Run catastrophic recovery on this environment before
    //                    opening it for normal use.  If this flag is set, the
    //                    DB_CREATE, DB_INIT_TXN, and DB_INIT_LOG flags must also
    //                    be set since the regions will be removed and recreated.
    //                    For further information, consult the man page for
    //                    db_recover(1).
    //
    //                  DB_THREAD
    //                    Ensure that handles returned by the DB subsystems are
    //                    useable by multiple threads within a single process,
    //                    i.e., that the system is "free-threaded".
    //
    //                  DB_TXN_NOSYNC
    //                    On transaction commit, do not synchronously flush the
    //                    log.  Ignored unless DB_INIT_TXN is also specified.
    //
    //                  DB_USE_ENVIRON
    //                    The Berkeley DB process' environment may be
    //                    permitted to specify information to be used when
    //                    naming files; see Berkeley DB File Naming. As
    //                    permitting users to specify which files are used can
    //                    create security problems, environment information
    //                    will be used in file naming for all users only if
    //                    the DB_USE_ENVIRON flag is set.
    //
    //                  DB_USE_ENVIRON_ROOT
    //                    The Berkeley DB process' environment may be
    //                    permitted to specify information to be used when
    //                    naming files; see Berkeley DB File Naming. As
    //                    permitting users to specify which files are used can
    //                    create security problems, if the DB_USE_ENVIRON_ROOT
    //                    flag is set, environment information will be used
    //                    for file naming only for users with a user-ID
    //                    matching that of the superuser (specifically, users
    //                    for whom the getuid(2) system call returns the
    //                    user-ID 0).
    //
    static PyObject* appinit(char *db_home, int flags) {
        int err;
        db_env = (DB_ENV*)malloc(sizeof(DB_ENV));
        memset(db_env, 0, sizeof(DB_ENV));
        err = db_appinit(db_home, NULL, db_env, flags);
        CHECK_ERR();
        doneAppinit = 1;
        RETURN_NONE();
    }

    //
    // appexit()
    //
    // The db_appexit function closes the initialized DB subsystems, freeing
    // any allocated resources and closing any underlying subsystems.
    //
    static PyObject* appexit() {
        int err;
        if (doneAppinit) {      /* Don't appexit if havn't done appinit. */
            err = db_appexit(db_env);
            free(db_env);
            CHECK_ERR();
            doneAppinit = 0;
        }
        RETURN_NONE();
    }
%}


//---------------------------------------------------------------------------
// There are two types of transactions supported by this module, automatic
// and explicit.
//
//
// An explicit transaction must have its ID explicitly passed to the DB method
// calls, and therefore cannot be passed to the dictionary simulation routines.
// On the other hand, there can be more than one explicit transaction active in
// any one process at once.  (You should also be able to mix explicit and automatic
// transactions.)
//



%inline %{

    //
    // beginAutoTrans()
    //
    // This function begins an "Automatic Transaction."  An automatic
    // transaction automatically involves all DB method calls including the
    // dictionary simulation routines, until the transaction is commited or
    // aborted.  There can only be one automatic transaction in any process
    // at a time, however nested calls can be made to beginAutoTrans and
    // commitAutoTrans are supported via reference counting.  abortAutoTrans
    // ignores the nesting count and performs the abort.
    //
    static PyObject* beginAutoTrans() {
        int err;
        if (atRefCnt == 0) {
            if (! db_env) {
                PyErr_SetString(dbError, "appinit() required for transaction use");
                return NULL;
            }
            err = txn_begin(db_env->tx_info, 0, &autoTrans);
            CHECK_ERR();
        }
        atRefCnt += 1;
        RETURN_NONE();
    }

    //
    // abortAutoTrans()
    //
    // Aborts and rolls-back the active automatic transaction.
    //
    static PyObject* abortAutoTrans() {
        int err;
        if (atRefCnt) {
            err = txn_abort(autoTrans);
            autoTrans = NULL;
            atRefCnt = 0;
            CHECK_ERR();
        }
        RETURN_NONE();
    }

    //
    // prepareAutoTrans()
    //
    // If the active automatic transaction is involved in a distributed
    // transaction system, this function should be called to begin the
    // two-phase commit.
    //
    static PyObject* prepareAutoTrans() {
        int err;
        if (atRefCnt) {
            err = txn_prepare(autoTrans);
            CHECK_ERR();
        }
        RETURN_NONE();
    }

    //
    // commitAutoTrans()
    //
    // This function ends the active automatic transaction, commiting the
    // changes to the database.
    //
    static PyObject* commitAutoTrans() {
        int err;
        atRefCnt -= 1;
        if (atRefCnt == 0) {
            err = txn_commit(autoTrans);
            CHECK_ERR();
        }
        RETURN_NONE();
    }


    //
    // beginTrans()
    //
    // This function starts a new explicit transaction.  An explicit
    // transaction must be explicitly passed to each of the database access
    // routines that need to be involved in the transaction, and therefore
    // cannot include the dictionary  simulation routines.  On the other hand,
    // there can be more than one explicit transaction active in any one
    // process at once.  (You should also be able to mix explicit and
    // automatic transactions.)
    //
    // This function returns a DB_TXN object that must be passed along to
    // any function that needs to be involved in the transaction, and to the
    // abort and commit functions described below.
    //
    static PyObject* beginTrans() {
        int err;
        DB_TXN  *txn;
        char    swigptr[48];
        if (! db_env) {
            PyErr_SetString(dbError, "appinit() required for transaction use");
            return NULL;
        }
        err = txn_begin(db_env->tx_info, 0, &txn);
        CHECK_ERR();
        SWIG_MakePtr(swigptr, (char *)txn, "_DB_TXN_p");
        return PyString_FromString(swigptr);
    }

    //
    // abortTrans(DB_TXN)
    //
    // This function causes an abnormal termination of the transaction.  The
    // log is played backwards and any necessary recovery operations are
    // initiated.
    //
    static PyObject* abortTrans(DB_TXN* txn) {
        int err;
        err = txn_abort(txn);
        CHECK_ERR();
        RETURN_NONE();
    }

    //
    // prepareTrans(DB_TXN)
    //
    // If this transaction is involved in a distributed transaction system,
    // this function should be called to begin the two-phase commit.
    //
    static PyObject* prepareTrans(DB_TXN* txn) {
        int err;
        err = txn_prepare(txn);
        CHECK_ERR();
        RETURN_NONE();
    }

    //
    // commitTrans(DB_TXN)
    //
    // This function ends the transaction, commiting the changes to the
    // database.
    //
    static PyObject* commitTrans(DB_TXN* txn) {
        int err;
        err = txn_commit(txn);
        CHECK_ERR();
        RETURN_NONE();
    }


%}

//----------------------------------------------------------------------

//
// class DBC
//
//  The DBC (DataBase Cursor) class supports sequential access to the records
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
//  (EAGAIN) or system failure occurred.
//
//  When locking is enabled, page locks are retained between consecutive cursor
//  calls.  For this reason, in the presence of locking, applications should
//  discard cursors as soon as they are done with them.  Calling the DB.close
//  method discards any cursors opened from that DB.
//
%name(DBC) struct MyDBC {
    %addmethods {

        //
        // DBC.__del__
        //
        // When the cursor object goes out of scope, it is closed.
        //
        ~MyDBC() {
            if (!self->closed) {
                self->dbc->c_close(self->dbc);
            }
            free(self);
        }

        //
        // DBC.close()
        //
        // The cursor is discarded.  No further references to this cursor
        // should be made.
        //
        PyObject* close() {
            int err;
            err = self->dbc->c_close(self->dbc);
            CHECK_ERR();
            self->closed = 1;
            RETURN_NONE();
        }

        //
        // DBC.delete()
        //
        // The key/data pair currently referenced by the cursor is removed
        // from the database.
        //
        // The cursor position is unchanged after a delete and subsequent
        // calls to cursor functions expecting the cursor to reference an
        // existing key will fail.
        //
        PyObject* delete(int flags=0) {
            int err;
            err = self->dbc->c_del(self->dbc, flags);
            CHECK_ERR();
            self->mydb->size = -1;
            RETURN_NONE();
        }

        //
        // DBC.get(flags)
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
        //        function will raise db.error with a value of DB_NOTFOUND.
        //
        //    DB_LAST
        //        The cursor is set to reference the last key/data pair of the
        //        database, and that pair is returned. In the presence of
        //        duplicate key values, the last data item in the set of
        //        duplicates is returned.  If the database is empty, this
        //        method will raise db.error with a value of DB_NOTFOUND.
        //
        //    DB_NEXT
        //        If the cursor is not yet initialized, DB_NEXT is identical to
        //        DB_FIRST.  Otherwise, move the cursor to the next key/data
        //        pair of the database, and that pair is returned. In the
        //        presence of duplicate key values, the key may not change.  If
        //        the cursor is already on the last record in the database,
        //        this method will raise db.error with a value of DB_NOTFOUND.
        //
        //    DB_PREV
        //        If the cursor is not yet initialized, DB_PREV is identical to
        //        DB_LAST. Otherwise, move the cursor to the previous key/data
        //        pair of the database, and that pair is returned.  In the
        //        presence of duplicate key values, the key may not change.  If
        //        the cursor is already on the first record in the database,
        //        this method will raise db.error with a value of DB_NOTFOUND.
        //
        //    DB_CURRENT
        //        Return the key/data pair currently referenced by the cursor.
        //        If the cursor key/data pair has been deleted, this method
        //        will return DB_KEYEMPTY.  If the cursor is not yet
        //        initialized, the get method will raise db.error with a value
        //        of EINVAL.
        //
        PyObject* get(int flags) {
            int err;
            DBT key;
            DBT data;
            memset(&key, 0, sizeof(key));
            memset(&data, 0, sizeof(data));
            err = self->dbc->c_get(self->dbc, &key, &data, flags);
            CHECK_ERR();
            return Py_BuildValue("s#s#", key.data, key.size,
                                         data.data, data.size);
        }

        //
        // DBC.first()
        //
        // A convenience method.  Equivalent to calling get with DB_FIRST.
        //
        PyObject* first()   { return MyDBC_get(self, DB_FIRST); }

        //
        // DBC.last()
        //
        // A convenience method.  Equivalent to calling get with DB_LAST.
        //
        PyObject* last()    { return MyDBC_get(self, DB_LAST); }

        //
        // DBC.next()
        //
        // A convenience method.  Equivalent to calling get with DB_NEXT.
        //
        PyObject* next()    { return MyDBC_get(self, DB_NEXT); }

        //
        // DBC.prev()
        //
        // A convenience method.  Equivalent to calling get with DB_PREV.
        //
        PyObject* prev()    { return MyDBC_get(self, DB_PREV); }

        //
        // DBC.current()
        //
        // A convenience method.  Equivalent to calling get with DB_CURRENT.
        //
        PyObject* current() { return MyDBC_get(self, DB_CURRENT);   }


        //
        // DBC.set(key)
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
        // If no matching keys are found, this method will raise db.error
        // with a value of DB_NOTFOUND.
        //
        PyObject* set(PyObject* pyKey) {
            int err;
            DBT key;
            DBT data;
            GET_DBT(pyKey, key);
            memset(&data, 0, sizeof(data));
            err = self->dbc->c_get(self->dbc, &key, &data, DB_SET);
            CHECK_ERR();
            return Py_BuildValue("s#s#", key.data, key.size,
                                         data.data, data.size);
        }

        //
        // DBC.setRange(key)
        //
        // Identical to the set method, except in the case of the btree access
        // method, the returned key/data pair is the smallest key greater than
        // or equal to the speci- fied key, permitting partial key matches and
        // range searches.
        //
        PyObject* setRange(PyObject* pyKey) {
            int err;
            DBT key;
            DBT data;
            GET_DBT(pyKey, key);
            memset(&data, 0, sizeof(data));
            err = self->dbc->c_get(self->dbc, &key, &data, DB_SET_RANGE);
            CHECK_ERR();
            return Py_BuildValue("s#s#", key.data, key.size,
                                         data.data, data.size);
        }

        //
        // DBC.setRecno(record_number)
        //
        // Move the cursor to the specific numbered record of the database, and
        // return the associated key/data pair.  For this method to be used, the
        // underlying database must be of type btree and it must have been
        // created with the DB_RECNUM flag.
        //
        PyObject* setRecno(db_recno_t recno) {
            int err;
            DBT key;
            DBT data;
            key.data = &recno;
            key.size = sizeof(db_recno_t);
            memset(&data, 0, sizeof(data));
            err = self->dbc->c_get(self->dbc, &key, &data, DB_SET_RECNO);
            CHECK_ERR();
            return Py_BuildValue("s#s#", key.data, key.size,
                                         data.data, data.size);
        }

        //
        // DBC.getRecno()
        //
        // Return the record number associated with the cursor.  For this
        // method to be used, the underlying database must be of type btree
        // and it must have been created with the DB_RECNUM flag.
        //
        PyObject* getRecno() {
            int err;
            db_recno_t recno;
            DBT key;
            DBT data;
            memset(&key, 0, sizeof(key));
            memset(&data, 0, sizeof(data));
            err = self->dbc->c_get(self->dbc, &key, &data, DB_GET_RECNO);
            CHECK_ERR();
            memcpy(&recno, data.data, sizeof(db_recno_t));
            return PyInt_FromLong(recno);
        }


        //
        // DBC.put(key, data, flags)
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
        //
        PyObject* put(PyObject* pyKey, PyObject* pyData, int flags) {
            int err;
            DBT key;
            DBT data;
            GET_DBT(pyKey, key);
            GET_DBT(pyData, data);
            err = self->dbc->c_put(self->dbc, &key, &data, flags);
            CHECK_ERR();
            self->mydb->size = -1;
            RETURN_NONE();
        }
    }
};



//----------------------------------------------------------------------

//
// class DB
//
// This class encapsulates the DB database file access methods, and also
// has an embedded DB_INFO object named "info" used for setting configuration
// parameters and flags prior to creation of the database.  See the docstring
// for the DB_INFO object for details.
//
// The DB object must be opened before any other methods can be called.  The
// only thing that can be done before opening is setting options and flags
// in the info object.  For example:
//
//      import db
//      data = db.DB()
//      data.info.db_pagesize = 4096
//      data.open("datafile", db.DB_BTREE, db.DB_CREATE)
//
// The DB class supports a dictionary-like interface, including the len, keys,
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
//
%name(DB) struct MyDB {
    struct __db_info info;

    %addmethods {
        MyDB() {
            struct MyDB* retval = (struct MyDB*)malloc(sizeof(struct MyDB));
            memset(retval, 0, sizeof(struct MyDB));
            retval->size = -1;
            retval->closed = 1;
            return retval;
        }

        ~MyDB() {
            if (!self->closed) {
                self->db->close(self->db, 0);
            }
            free(self);
        }

        //
        // DB.open(filename, type, flags=0, mode=0660)
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
        //    DB_CREATE
        //        Create any underlying files, as necessary.  If the
        //        files do not already exist and the DB_CREATE flag is
        //        not specified, the call will fail.
        //
        //    DB_NOMMAP
        //        Do not memory-map this file.
        //
        //    DB_RDONLY
        //        Open the database for reading only.  Any attempt to write the
        //        database using the access methods will fail regardless of the
        //        actual permissions of any underlying files.
        //
        //    DB_THREAD
        //        Cause the DB handle returned by the open function to be useable
        //        by multiple threads within a single address space, i.e., to be
        //        "free-threaded".
        //
        //    DB_TRUNCATE
        //        "Truncate" the database if it exists, i.e., behave as if the
        //        database were just created, discarding any previous contents.
        //
        // All files created by the access methods are created with mode mode (as
        // described in chmod) and modified by the process' umask value at the
        // time of creation.  The group ownership of created files is based on
        // the system and directory defaults, and is not further specified by DB.
        //
        PyObject* open(const char *file, int type=DB_UNKNOWN, int flags=0, int mode=0660) {
            int err = db_open(file, (DBTYPE)type, flags, mode, db_env,
                              &self->info, &self->db);
            CHECK_ERR();
            self->closed = 0;
            RETURN_NONE();
        }

        //
        // DB.type()
        //
        // The type of the underlying access method (and file format).  Set to
        // one of DB_BTREE, DB_HASH or DB_RECNO.  This field may be used to
        // determine the type of the database after a return from open with
        // the type argument set to DB_UNKNOWN.
        //
        int type() {
            return self->db->type;
        }

        //
        // DB.close(flags=0)
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
        //
        PyObject* close(int flags=0) {
            int err = 0;
            if (!self->closed) {
                err = self->db->close(self->db, flags);
            }
            CHECK_ERR();
            self->closed = 1;
            RETURN_NONE();
        }


        //
        // DB.cursor(txn=None, flags=0)
        //
        // Creates and returns a DBC object used to provide sequential access
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
        //      DB_RMW
        //        Specify that the cursor will be used to update the
        //        database. This flag should only be set when the DB_INIT_CDB
        //        flag was specified to db_appinit.
        //
        %new struct MyDBC* cursor(DB_TXN* txn=NULL, int flags=0) {
            int err;
            DBC* dbc;
            struct MyDBC* retval;
            if (!txn) txn = autoTrans;
            err = self->db->cursor(self->db, txn, &dbc, flags);
            CHECK_ERR();
            retval = (struct MyDBC*)malloc(sizeof(struct MyDBC));
            retval->dbc = dbc;
            retval->mydb = self;
            retval->closed = 0;
            return retval;              // Let SWIG turn it into a python DBC
        }

        //
        // DB.delete(key, txn=None)
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
        //
        PyObject* delete(PyObject* pyKey, DB_TXN* txn=NULL) {
            int err;
            DBT key;
            GET_DBT(pyKey, key);
            if (!txn) txn = autoTrans;
            err = self->db->del(self->db, txn, &key, 0);
            CHECK_ERR();
            self->size = -1;
            RETURN_NONE();
        }

        //
        // DB.get(key, txn=None)
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
        // database, the get function method raises db.error with a value of
        // DB_NOTFOUND.
        //
        PyObject* get(PyObject* pyKey, DB_TXN* txn=NULL) {
            int err;
            DBT key;
            DBT data;
            GET_DBT(pyKey, key);        // **** if the type is RECNO, get an
                                        //      int instead of a string...
            memset(&data, 0, sizeof(DBT));
            if (!txn) txn = autoTrans;
            err = self->db->get(self->db, txn, &key, &data, 0);
            CHECK_ERR();
            return PyString_FromStringAndSize((char*)data.data, data.size);
        }

        //
        // DB.getRec(recno, txn=None)
        //
        // Retrieve a specific numbered record from a database.  Both the
        // key and data item will be returned as a tuple.  In order to use
        // this method, the underlying database must be of type btree, and it
        // must have been created with the DB_RECNUM flag.
        //
        // If the file is being accessed under transaction protection, the
        // txn parameter is a transaction ID returned from beginTrans,
        // otherwise, the autoTrans (if any) is used.
        //
        PyObject* getRec(db_recno_t recno, DB_TXN* txn=NULL) {
            int err;
            DBT key;
            DBT data;
            key.data = &recno;
            key.size = sizeof(db_recno_t);
            memset(&data, 0, sizeof(data));
            if (!txn) txn = autoTrans;
            err = self->db->get(self->db, txn, &key, &data, DB_SET_RECNO);
            CHECK_ERR();
            return Py_BuildValue("s#s#", key.data, key.size,
                                         data.data, data.size);
            RETURN_NONE();
        }

        //
        // DB.fd()
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
        //
        PyObject* fd() {
            int err;
            int the_fd;
            err = self->db->fd(self->db, &the_fd);
            CHECK_ERR();
            return PyInt_FromLong(the_fd);
        }

        //
        // DB.put(key, data, flags=0, txn=None)
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
        //
        PyObject* put(PyObject* pyKey, PyObject* pyData, int flags=0, DB_TXN* txn=NULL) {
            int err;
            DBT key;
            DBT data;
            GET_DBT(pyKey, key);
            GET_DBT(pyData, data);
            if (!txn) txn = autoTrans;
            err = self->db->put(self->db, txn, &key, &data, flags);
            CHECK_ERR();
            self->size = -1;
                                // **** if RECNO type, return as integer
            return Py_BuildValue("s#", key.data, key.size);
        }

        //
        // DB.sync()
        //
        // This method flushes any cached information to disk.
        //
        PyObject* sync() {
            int err;
            err = self->db->sync(self->db, 0);
            CHECK_ERR();
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
                err = self->db->cursor(self->db, autoTrans, &cursor, 0);
                CHECK_ERR();
                while ((err = cursor->c_get(cursor, &key, &data, DB_NEXT)) == 0) {
                    size += 1;
                }
                if (err < 0 && err != DB_NOTFOUND) {
                    PyErr_SetObject(dbError, makeDbError(err));
                    cursor->c_close(cursor);
                    return NULL;
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
            GET_DBT(pyKey, key);
            memset(&data, 0, sizeof(DBT));
            err = self->db->get(self->db, autoTrans, &key, &data, 0);
            if (err) {
                if (err == DB_NOTFOUND)
                    PyErr_SetObject(PyExc_KeyError, pyKey);
                else
                    PyErr_SetObject(dbError, makeDbError(err));
                return NULL;
            }
            return PyString_FromStringAndSize((char*)data.data, data.size);
        }

        PyObject* __setitem__(PyObject* pyKey, PyObject* pyData) {
            return MyDB_put(self, pyKey, pyData, 0, autoTrans);
        }

        PyObject* __delitem__(PyObject* pyKey) {
            return MyDB_delete(self, pyKey, autoTrans);
        }


        PyObject* keys() {
            int err;
            DBT key;
            DBT data;
            DBC *cursor;
            PyObject* list;
            PyObject* item;

            list = PyList_New(0);
            if (list == NULL)
                return NULL;
            memset(&key, 0, sizeof(DBT));
            memset(&data, 0, sizeof(DBT));
            err = self->db->cursor(self->db, autoTrans, &cursor, 0);
            CHECK_ERR();
            while ((err = cursor->c_get(cursor, &key, &data, DB_NEXT)) == 0) {
                item = PyString_FromStringAndSize((char*)key.data, key.size);
                if (item == NULL) {
                    Py_DECREF(list);
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
            cursor->c_close(cursor);
            return list;
        }


        // ****  Don't forget items() and values()...

        PyObject* has_key(PyObject* pyKey) {
            int err;
            DBT key;
            DBT data;
            GET_DBT(pyKey, key);
            memset(&data, 0, sizeof(DBT));
            err = self->db->get(self->db, autoTrans, &key, &data, 0);
            return PyInt_FromLong(err == 0);
        }
    }
};

//---------------------------------------------------------------------------

%pragma(python) include="db_compat.py"

//----------------------------------------------------------------------

%init %{
    dbError = PyString_FromString("db.error");
    PyDict_SetItemString(d,"error", dbError);

    Py_AtExit((AtExitFcn)appexit);
%}


//----------------------------------------------------------------------



