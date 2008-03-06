/***********************************************************
Copyright (c) 2000, BeOpen.com.
All rights reserved.

See the file "Misc/COPYRIGHT" for information on usage and
redistribution of this file, and for a DISCLAIMER OF ALL WARRANTIES.
******************************************************************/

/* Handwritten code to wrap version 3 of the Berkeley DB library.
   Written to replace a SWIG-generated file.

   This module contains 4 different types:

   DB (Database)
   DBC (Database Cursor)
   DBEnv (database environment)
   Txn (An explicit database transaction)
*/

#include "Python.h"
#include <db.h>

/* --------------------------------------------------------------------- */
/* Various macro definitions */

/* Version number of module */
#define PY_BSDDB_VERSION "2.9.0"

static char *rcs_id = "$Id$";

/*
   This allows threading support to be easily removed (forcing
   monothreaded execution of all code in this module).  With threading
   enabled, be sure to open your BerkeleyDB environments using
   DB_THREAD as needed!  If you're using BerkeleyDB in a multi thread
   or process environment, be sure to run the db_deadlock utility or
   enable automatic deadlock detection.
  
   In my experience on a dual-cpu box running three threads in a test
   program (dbtest.py) with BerkeleyDB 3.0.55, HASH databases had frequent
   deadlocks requiring db_deadlock to be running to abort the locked calls.
   BTREE databases did not appear to have problems. -greg  (using
   set_lk_detect(1) also helped the problem)
*/
#define MYDB_THREAD

#ifdef MYDB_THREAD
#define MYDB_BEGIN_ALLOW_THREADS Py_BEGIN_ALLOW_THREADS;
#define MYDB_END_ALLOW_THREADS Py_END_ALLOW_THREADS;
#else 
#warning "Forcing monothreaded execution"
#define MYDB_BEGIN_ALLOW_THREADS {
#define MYDB_END_ALLOW_THREADS }
/* causes code using DB_THREAD to not actually pass the flag when
   the database library won't accept it on the given platform. */
#undef DB_THREAD
#define DB_THREAD 0
#endif /* MYDB_THREAD */

#define RETURN_IF_ERR()                                   \
    if (err != 0) {                                     \
        PyErr_SetObject(dbError, makeDbError(err));     \
        return NULL;                                    \
    }
#define RETURN_NONE()  Py_INCREF(Py_None); return Py_None;

/* --------------------------------------------------------------------- */
/* Structure definitions */

static PyObject* dbError;             /* Make an error variable for exceptions */

typedef struct _DBEnvObject DBEnvObject;

typedef struct {
	PyObject_HEAD
	DB*             db;
	/* Use myenvobj-> instead of myenv */
	DBEnvObject*       myenvobj;  /* PyObject containing the DB_ENV */
	int             flags;     /* saved flags from open() */
	long            size;
} DBObject;

typedef struct {
	PyObject_HEAD
	DBC*            dbc;
	DBObject*       mydb;
} DBCObject;

struct _DBEnvObject {
	PyObject_HEAD
	DB_ENV* db_env;
	DB_TXN* autoTrans;
	int     flags;             /* saved flags from open() */
	int     atRefCnt;
	int     closed;
};

typedef struct {
	PyObject_HEAD
	DB_TXN *txn;
} TxnObject;

staticforward PyTypeObject DB_Type, DBC_Type, DBEnv_Type, Txn_Type;

#define DBObject_Check(v)	((v)->ob_type == &DB_Type)
#define DBCObject_Check(v)	((v)->ob_type == &DBC_Type)
#define DBEnvObject_Check(v)	((v)->ob_type == &DBEnv_Type)
#define TxnObject_Check(v)	((v)->ob_type == &Txn_Type)

#define CHECK_DBFLAG(mydb, flag)        ( ((mydb)->flags & (flag)) || ((mydb)->myenvobj->flags & (flag)) )


/* --------------------------------------------------------------------- */
/* Utility functions */

/* Create a DBT structure (containing key and data values) from 
   Python strings.
   Returns 1 on success, 0 on an error. 
*/

int parse_dbt(PyObject *obj, DBT *dbt)
{
	memset(dbt, 0, sizeof(DBT));
	if (obj == Py_None) {
		dbt->data = NULL;
		dbt->size = 0;
	} else if (!PyArg_Parse(obj, "s#", &dbt->data, &dbt->size)) {
		PyErr_SetString(PyExc_TypeError,
				"Key and Data values must be of type string or None.");
		return 0;
	}
	return 1;
}

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

/* Delete a key from a database 
  Returns 0 on success, -1 on an error.  */

static int
_DB_delete(DBObject *self, DB_TXN *txn, DBT *key, int flags)
{
	int err;

	MYDB_BEGIN_ALLOW_THREADS;
	err = self->db->del(self->db, txn, key, 0);
	MYDB_END_ALLOW_THREADS;
	if (err != 0) {                                     
		PyErr_SetObject(dbError, makeDbError(err));     
		return -1;                                    
	}
	self->size = -1;
	return 0;
}

/* Store a key into a database 
   Returns 0 on success, -1 on an error.  */

static int
_DB_put(DBObject *self, DB_TXN *txn, DBT *key, DBT *data, int flags)
{
	int err;

	MYDB_BEGIN_ALLOW_THREADS;
	err = self->db->put(self->db, txn, key, data, flags);
	MYDB_END_ALLOW_THREADS;
	if (err != 0) {                                     
		PyErr_SetObject(dbError, makeDbError(err));     
		return -1;                                    
	}
	self->size = -1;
	return 0;
}

/* Get a value from a cursor */

static PyObject *
_DBC_get(DBCObject *self, int flags)
{
	int err;
	PyObject *retval = NULL;
	DBT key, data;

	memset(&key, 0, sizeof(key));
	memset(&data, 0, sizeof(data));
	if (CHECK_DBFLAG(self->mydb, DB_THREAD)) {
                /* Tell BerkeleyDB to malloc the return value (thread safe) */
                data.flags = DB_DBT_MALLOC;
                key.flags = DB_DBT_MALLOC;
	}
	MYDB_BEGIN_ALLOW_THREADS;
	err = self->dbc->c_get(self->dbc, &key, &data, flags);
	MYDB_END_ALLOW_THREADS;

	/* emulate Python dict.get() behavior, return None if the key was not found */
	if (err == DB_NOTFOUND) {
                Py_INCREF(Py_None);
                retval = Py_None;
	} else {
                RETURN_IF_ERR();
	}
	if (retval == NULL) {  /* if we're not returning Py_None */
                retval = Py_BuildValue("s#s#", key.data, key.size,
				       data.data, data.size);
	}
	if (CHECK_DBFLAG(self->mydb, DB_THREAD)) {
                if (key.data != NULL) free(key.data);
                if (data.data != NULL) free(data.data);
	}
	return retval;
}


/* --------------------------------------------------------------------- */
/* Allocators and deallocators */

static DBObject *
newDBObject(DBEnvObject *arg)
{
	DBObject *self;
	int err;

#if PYTHON_API_VERSION <= 1007
	/* 1.5 compatibility */
	self = PyObject_NEW(DBObject, &DB_Type);
#else
	self = PyObject_New(DBObject, &DB_Type);
#endif

	if (self == NULL)
		return NULL;

	self->size = -1;
	self->flags = 0;
	/* keep a reference to our python DbEnv object */
	Py_INCREF(arg);
	self->myenvobj = arg;

	err = db_create(&self->db, arg->db_env, 0);
	/* XXX this leaks self on an error */
	RETURN_IF_ERR();

	return self;
}

static void
DB_dealloc(DBObject *self)
{
	if (self->db != NULL) {
                MYDB_BEGIN_ALLOW_THREADS;
                self->db->close(self->db, 0);
		self->db = NULL;
                MYDB_END_ALLOW_THREADS;
	}
	if (self->myenvobj) {
                Py_DECREF(self->myenvobj);
                self->myenvobj = NULL;
	}
#if PYTHON_API_VERSION <= 1007
	PyMem_DEL(self);
#else
	PyObject_Del(self);
#endif
}

static DBCObject *
newDBCObject(void)
{
	DBCObject *self;
#if PYTHON_API_VERSION <= 1007
	self = PyObject_NEW(DBCObject, &DBC_Type);
#else
	self = PyObject_New(DBCObject, &DBC_Type);
#endif
	if (self == NULL)
		return NULL;
	self->dbc = NULL;
	self->mydb = NULL;
	return self;
}

static void
DBC_dealloc(DBCObject *self)
{
  int err;
	if (self->dbc != NULL) {
                MYDB_BEGIN_ALLOW_THREADS;
                err = self->dbc->c_close(self->dbc);
		self->dbc = NULL;
                MYDB_END_ALLOW_THREADS;
	}
	Py_XDECREF( self->mydb );
#if PYTHON_API_VERSION <= 1007
	PyMem_DEL(self);
#else
	PyObject_Del(self);
#endif
}

static DBEnvObject *
newDBEnvObject(void)
{
	int err;
	DBEnvObject *self;
#if PYTHON_API_VERSION <= 1007
	self = PyObject_NEW(DBEnvObject, &DBEnv_Type);
#else
	self = PyObject_New(DBEnvObject, &DBEnv_Type);
#endif

	if (self == NULL)
		return NULL;
	err = db_env_create(&self->db_env, 0);
	RETURN_IF_ERR();
	self->closed = 1;
	self->autoTrans = NULL;
	self->atRefCnt = 0;
	self->flags = 0;
	return self;
}

static void
DBEnv_dealloc(DBEnvObject *self)
{
	if (!self->closed) {
                self->db_env->close(self->db_env, 0);
                /* return value ignored in destructor, possibly bad...? */
	}
#if PYTHON_API_VERSION <= 1007
	PyMem_DEL(self);
#else
	PyObject_Del(self);
#endif
}

static TxnObject *
newTxnObject(DBEnvObject *myenv, DB_TXN *parent, int flags)
{
	int err;
	TxnObject *self;

#if PYTHON_API_VERSION <= 1007
	self = PyObject_NEW(TxnObject, &Txn_Type);
#else
	self = PyObject_New(TxnObject, &Txn_Type);
#endif
	if (self == NULL)
		return NULL;

	err = txn_begin(myenv->db_env, parent, &(self->txn), flags);
	RETURN_IF_ERR();
	return self;
}

static void
Txn_dealloc(TxnObject *self)
{
	/* XXX nothing to do for transaction objects?!? */
#if PYTHON_API_VERSION <= 1007
	PyMem_DEL(self);
#else
	PyObject_Del(self);
#endif
}

/* --------------------------------------------------------------------- */
/* DB methods */

/* XXX Don't forget items() and values()... get() has the wrong signature,
   too...*/



/* This class encapsulates the DB database file access methods, and also */
/* has an embedded DB_INFO object named "info" used for setting configuration */
/* parameters and flags prior to creation of the database.  See the docstring */
/* for the DB_INFO object for details. */
/* */
/* The Db object must be opened before any other methods can be called.  The */
/* only thing that can be done before opening is setting options and flags */
/* in the info object.  For example: */
/* */
/*      import db */
/*      env = db.DbEnv() */
/*      env.open(...) */
/*      data = db.Db(env) */
/*      data.set_db_pagesize(4096) */
/*      data.open("datafile", db.DB_BTREE, db.DB_CREATE) */
/* */
/* The Db class supports a dictionary-like interface, including the len, keys, */
/* has_attr methods, as well as the item reference, item assigment and item */
/* deletion.  Dictionary access methods can be involved in transactions by */
/* using the autoTrans functions. */
/* */
/* Various types of database files can be created, based on a flag to the */
/* open method.  The types are: */
/* */
/*  DB_BTREE */
/*       The btree data structure is a sorted, balanced tree structure storing */
/*       associated key/data pairs.  Searches, inserions, and deletions in the */
/*       btree will all complete in O(lg base N) where base is the average */
/*       number of keys per page.  Often, inserting ordered data into btrees */
/*       results in pages that are half-full.  This implementation has been */
/*       modified to make ordered (or inverse ordered) insertion the best case, */
/*       resulting in nearly perfect page space utilization. */
/* */
/*       Space freed by deleting key/data pairs from the database is never */
/*       reclaimed from the filesystem, although it is reused where possible. */
/*       This means that the btree storage structure is grow-only.  If */
/*       sufficiently many keys are deleted from a tree that shrinking the */
/*       underlying database file is desirable, this can be accomplished by */
/*       creating a new tree from a scan of the existing one. */
/* */
/*  DB_HASH */
/*       The hash data structure is an extensible, dynamic hashing scheme, */
/*       able to store variable length key/data pairs. */
/* */
/*  DB_RECNO */
/*       The recno access method provides support for fixed and variable length */
/*       records, optionally backed by a flat text (byte stream) file.  Both */
/*       fixed and variable length records are accessed by their logical record */
/*       number. */
/* */
/*       It is valid to create a record whose record number is more than one */
/*       greater than the last record currently in the database.  For example, */
/*       the creation of record number 8, when records 6 and 7 do not yet */
/*       exist, is not an error. However, any attempt to retrieve such records */
/*       (e.g., records 6 and 7) will raise db.error with a value of */
/*       DB_KEYEMPTY. */
/* */
/*       Deleting a record will not, by default, renumber records following the */
/*       deleted record (see DB_RENUMBER in the DB_INFO class for more */
/*       information).  Any attempt to retrieve deleted records will raise */
/*       db.error with a value of DB_KEYEMPTY. */


/* Db.close(flags=0) */
/* */
/* A pointer to a function to flush any cached information to disk, */
/* close any open cursors, free any allocated resources, and close */
/* any underlying files.  Since key/data pairs are cached in memory, */
/* failing to sync the file with the close or sync method may result */
/* in inconsistent or lost information.  (When the DB object's */
/* reference count reaches zero, the close method is called, but you */
/* should probably always call the close method just in case...) */
/* */
/* The flags parameter must be set to DB_NOSYNC, which specifies to */
/* not flush cached information to disk.  The DB_NOSYNC flag is a */
/* dangerous option.  It should only be set if the application is */
/* doing logging (with or without transactions) so that the database */
/* is recoverable after a system or application crash, or if the */
/* database is always generated from scratch after any system or */
/* application crash. */
/* */
/* When multiple threads are using the DB handle concurrently, only */
/* a single thread may call the DB handle close function. */

static PyObject *
DB_close(PyObject *dbobj, PyObject *args)
{
	int err, flags=0;
	DBObject *self = (DBObject *)dbobj;
	if(!PyArg_ParseTuple(args,"|i:close", &flags))
		return NULL;
	if (self->db != NULL) {
                MYDB_BEGIN_ALLOW_THREADS;
                err = self->db->close(self->db, flags);
		self->db = NULL;
                MYDB_END_ALLOW_THREADS;
		RETURN_IF_ERR();
	}
	RETURN_NONE();       
}

/* Db.cursor(txn=None, flags=0) */
/* */
/* Creates and returns a Dbc object used to provide sequential access */
/* to a database. */
/* */
/* If the file is being accessed under transaction protection, the */
/* txn parameter is a transaction ID returned from beginTrans, */
/* otherwise, the autoTrans (if any) is used.  If transaction */
/* protection is enabled, cursors must be opened and closed within */
/* the context of a transaction, and the txnid parameter specifies */
/* the transaction context in which the cursor may be used. */
/* */
/* The  flags value is specified by or'ing together one or more of */
/* the following values: */
/* */
/*   DB_WRITECURSOR */
/*      Specify that the cursor will be used to update the */
/*      database. This flag should only be set when the DB_INIT_CDB */
/*      flag was specified to db_env->open. */

static PyObject *
DB_cursor(PyObject *dbobj, PyObject *args)
{
	int err, flags=0;
	DBC* dbc;
	DBCObject* retval;
	TxnObject *txnobj = NULL;
	DB_TXN *txn;
	DBObject *self = (DBObject *)dbobj;

	if(!PyArg_ParseTuple(args,"|O!i:cursor", &Txn_Type, &txnobj, &flags))
		return NULL;

	if(NULL == self->db) {
		PyErr_SetString(dbError, 
				"Db object has been closed");
		return NULL;
	}

	if (!txnobj) txn = self->myenvobj->autoTrans;
	else         txn = txnobj->txn;
	MYDB_BEGIN_ALLOW_THREADS;
	err = self->db->cursor(self->db, txn, &dbc, flags);
	MYDB_END_ALLOW_THREADS;
	RETURN_IF_ERR();
	retval = newDBCObject();
	retval->dbc = dbc;
	retval->mydb = self; Py_INCREF(self);
	return (PyObject*) retval;             
}

/* Db.delete(key, txn=None) */
/* */
/* The key/data pair associated with the specified key is discarded */
/* from the database.  In the presence of duplicate key values, all */
/* records associated with the designated key will be discarded. */
/* */
/* If the file is being accessed under transaction protection, the */
/* txn parameter is a transaction ID returned from beginTrans, */
/* otherwise, the autoTrans (if any) is used. */
/* */
/* The delete method raises db.error with a value of DB_NOTFOUND if */
/* the specified key did not exist in the file. */
static PyObject *
DB_delete(PyObject *dbobj, PyObject *args)
{
	TxnObject *txnobj = NULL;
	PyObject *obj;
	DBT dbt;
	DBObject *self = (DBObject *)dbobj;
	DB_TXN *txn;

	if(!PyArg_ParseTuple(args,"O|O!:delete", &obj, &Txn_Type, &txnobj))
		return NULL;

	if (!parse_dbt(obj, &dbt)) 
		return NULL;

	if(NULL == self->db) {
		PyErr_SetString(dbError, 
				"Db object has been closed");
		return NULL;
	}
	
	if (!txnobj) txn = self->myenvobj->autoTrans;
	else         txn = txnobj->txn;

	if (-1 == _DB_delete(self, txn, &dbt, 0))
		return NULL;
	RETURN_NONE();
}

/* Db.fd() */
/* */
/* Returns a file descriptor representative of the underlying */
/* database.  A file descriptor referencing the same file will be */
/* returned to all processes that call db_open with the same file */
/* argument. This file descriptor may be safely used as an argument */
/* to the fcntl and flock locking functions. The file descriptor is */
/* not necessarily associated with any of the underlying files used */
/* by the access method. */
/* */
/* The fd function only supports a coarse-grained form of locking. */
/* Applications should use the lock manager where possible. */

static PyObject *
DB_fd(PyObject *dbobj, PyObject *args)
{
	int err, the_fd;
	DBObject *self = (DBObject *)dbobj;

	if(!PyArg_ParseTuple(args,":fd"))
		return NULL;
	if(NULL == self->db) {
		PyErr_SetString(dbError, 
				"Db object has been closed");
		return NULL;
	}

	MYDB_BEGIN_ALLOW_THREADS;
	err = self->db->fd(self->db, &the_fd);
	MYDB_END_ALLOW_THREADS;
	RETURN_IF_ERR();
	return PyInt_FromLong(the_fd);
}

/* Db.get(key, txn=None, flags=0) */
/* */
/* This method performs keyed retrievel from the database.  The data */
/* value coresponding to the given key is returned. */
/* */
/* In the presence of duplicate key values, get will return the */
/* first data item for the designated key. Duplicates are sorted by */
/* insert order except where this order has been overwritten by */
/* cursor operations. Retrieval of duplicates requires the use of */
/* cursor operations. */
/* */
/* If the file is being accessed under transaction protection, the */
/* txn parameter is a transaction ID returned from beginTrans, */
/* otherwise, the autoTrans (if any) is used. */
/* */
/* If the database is a recno database and the requested key exists, */
/* but was never explicitly created by the application or was later */
/* deleted, the get method raises db.error with a value of */
/* DB_KEYEMPTY.  Otherwise, if the requested key isn't in the */
/* database, the get method returns None. */

static PyObject *
DB_get(PyObject *dbobj, PyObject *args)
{
	int err, flags=0;
	DBObject *self = (DBObject *)dbobj;
	TxnObject *txnobj = NULL;
	PyObject *obj;
	PyObject *retval = NULL;
	DBT key, data;
	DB_TXN *txn;

	if(!PyArg_ParseTuple(args, "O|O!i:get", 
			     &obj, &Txn_Type, &txnobj, &flags))
		return NULL;
	if(!parse_dbt(obj, &key)) 
		return NULL;
	if(NULL == self->db) {
		PyErr_SetString(dbError, 
				"Db object has been closed");
		return NULL;
	}

        
	/* XXX RECNO databases could use another get interface */
	/* that accepts an integer instead of a string.  (for now, */
	/* RECNO users need to put the 32-bit integer into a */
	/* string before calling get) */
	memset(&data, 0, sizeof(DBT));
	if (!txnobj) txn = self->myenvobj->autoTrans;
	else         txn = txnobj->txn;

	if (CHECK_DBFLAG(self, DB_THREAD)) {
                /* Tell BerkeleyDB to malloc the return value (thread safe) */
                data.flags = DB_DBT_MALLOC;
	}
	MYDB_BEGIN_ALLOW_THREADS;
	err = self->db->get(self->db, txn, &key, &data, flags);
	MYDB_END_ALLOW_THREADS;

	/* emulate Python dict.get() behavior, return None if the key was not found */
	if (err == DB_NOTFOUND) {
                Py_INCREF(Py_None);
                retval = Py_None;
	} else {
                RETURN_IF_ERR();
	}
	if (retval == NULL) {  /* if we're not returning Py_None */
                retval = PyString_FromStringAndSize((char*)data.data, data.size);
	}
	if ((CHECK_DBFLAG(self, DB_THREAD)) && (data.data != NULL)) {
                free(data.data);
	}
	return retval;
}

/* Db.getRec(recno, txn=None) */
/* */
/* Retrieve a specific numbered record from a database.  Both the */
/* key and data item will be returned as a tuple.  In order to use */
/* this method, the underlying database must be of type btree, and it */
/* must have been created with the DB_RECNUM flag. */
/* */
/* If the file is being accessed under transaction protection, the */
/* txn parameter is a transaction ID returned from beginTrans, */
/* otherwise, the autoTrans (if any) is used. */

static PyObject *
DB_getRec(PyObject *dbobj, PyObject *args)
{
	/* XXX recno should be an unsigned int! */
	int err, int_recno;
	db_recno_t recno;
	DBObject *self = (DBObject *)dbobj;
	TxnObject *txnobj = NULL;
	PyObject *retval;
	DBT key, data;
	DB_TXN *txn;

	if(!PyArg_ParseTuple(args,"i|O!:getRec", 
			     &int_recno, &Txn_Type, &txnobj ))
		return NULL;
	recno = (db_recno_t)int_recno;

	if(NULL == self->db) {
		PyErr_SetString(dbError, 
				"Db object has been closed");
		return NULL;
	}

	key.data = &recno;
	key.size = sizeof(db_recno_t);
	key.ulen = key.size;
	key.flags = DB_DBT_USERMEM;
	memset(&data, 0, sizeof(data));
	if (CHECK_DBFLAG(self, DB_THREAD)) {
                /* Tell BerkeleyDB to malloc the return value (thread safe) */
                data.flags = DB_DBT_MALLOC;
	}
	if (!txnobj) txn = self->myenvobj->autoTrans;
	else         txn = txnobj->txn;

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

static PyObject *
DB_has_key(PyObject *dbobj, PyObject *args)
{
	int err;
	DBObject *self = (DBObject *)dbobj;
	PyObject *obj;
	DBT key, data;
	
	if(!PyArg_ParseTuple(args,"O:has_key", &obj ))
		return NULL;
	if(!parse_dbt(obj, &key)) return NULL;

	if(NULL == self->db) {
		PyErr_SetString(dbError, 
				"Db object has been closed");
		return NULL;
	}

	/* this causes ENOMEM to be returned when the db has the key */
	memset(&data, 0, sizeof(DBT));
	data.ulen = 0;
	data.data = NULL;
	data.flags = DB_DBT_USERMEM;

	MYDB_BEGIN_ALLOW_THREADS;
	err = self->db->get(self->db, self->myenvobj->autoTrans, &key, &data, 0);
	MYDB_END_ALLOW_THREADS;
	return PyInt_FromLong((err == ENOMEM) || (err == 0));
}

static PyObject *
DB_keys(PyObject *dbobj, PyObject *args)
{
	int err;
	DBObject *self = (DBObject *)dbobj;
	DBT key;
	DBT data;
	DBC *cursor;
	PyObject* list;
	PyObject* item;

	if(!PyArg_ParseTuple(args,":keys"))
		return NULL;

	if(NULL == self->db) {
		PyErr_SetString(dbError, 
				"Db object has been closed");
		return NULL;
	}

	list = PyList_New(0);
	if (list == NULL) {
                PyErr_SetString(PyExc_MemoryError, "PyList_New failed");
		return NULL;
	}
	memset(&key, 0, sizeof(DBT));
	memset(&data, 0, sizeof(DBT));
	MYDB_BEGIN_ALLOW_THREADS;
	err = self->db->cursor(self->db, self->myenvobj->autoTrans, &cursor, 0);
	MYDB_END_ALLOW_THREADS;
	RETURN_IF_ERR();
	
	while (1) {
                if (CHECK_DBFLAG(self, DB_THREAD)) {
			/* XXX tons of mallocs are highly inefficient */
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
		return NULL;
	}
	return list;
}

/* Db.open(filename, type=DB_UNKNOWN, flags=0, mode=0660) */
/* */
/* This method opens the database represented by file for both reading */
/* and writing by default.  Note, while most of the access methods use */
/* file as the name of an underlying file on disk, this is not */
/* guaranteed.  Also, calling open is a reasonably expensive operation. */
/* (This is based on a model where the DBMS keeps a set of files open */
/* (for a long time rather than opening and closing them on each query.) */
/* */
/* The type argument must be set to one of DB_BTREE, DB_HASH, DB_RECNO */
/* or DB_UNKNOWN.  If type is DB_UNKNOWN, the database must already */
/* exist and open will then determine if it is of type DB_BTREE, */
/* DB_HASH or DB_RECNO. */
/* */
/* The flags and mode arguments specify how files will be */
/* opened and/or created when they don't already exist.  The */
/* flags value is specified by or'ing together one or more of */
/* the following values: */
/* */
/*  DB_CREATE */
/*      Create any underlying files, as necessary.  If the */
/*      files do not already exist and the DB_CREATE flag is */
/*      not specified, the call will fail. */
/* */
/*  DB_NOMMAP */
/*      Do not memory-map this file. */
/* */
/*  DB_RDONLY */
/*      Open the database for reading only.  Any attempt to write the */
/*      database using the access methods will fail regardless of the */
/*      actual permissions of any underlying files. */
/* */
/*  DB_THREAD */
/*      Cause the DB handle returned by the open function to be useable */
/*      by multiple threads within a single address space, i.e., to be */
/*      "free-threaded". */
/* */
/*  DB_TRUNCATE */
/*      "Truncate" the database if it exists, i.e., behave as if the */
/*      database were just created, discarding any previous contents. */
/* */
/* All files created by the access methods are created with mode mode */
/* (see chmod) and modified by the process' umask value at the */
/* time of creation.  The group ownership of created files is based on */
/* the system and directory defaults. */

static PyObject *
DB_open(PyObject *dbobj, PyObject *args)
{
	int err, type = DB_UNKNOWN, flags=0, mode=0660;
	char *filename=NULL, *database=NULL;
	DBObject *self = (DBObject *)dbobj;

	if(!PyArg_ParseTuple(args,"ss|iii:open", &filename, &database,
			     &type, &flags, &mode)) {
	        PyErr_Clear();
	        if(!PyArg_ParseTuple(args,"|ziii:open", &filename, 
				     &type, &flags, &mode))
		        return NULL;
	}

	if(NULL == self->db) {
		PyErr_SetString(dbError, 
				"Cannot call open() twice for Db object");
		return NULL;
	}

	MYDB_BEGIN_ALLOW_THREADS;
	err = self->db->open(self->db, filename, database,
			     type, flags, mode);
	MYDB_END_ALLOW_THREADS;
	if (err) {self->db->close(self->db, 0); self->db=NULL;}
	RETURN_IF_ERR();
	self->flags = flags;
	RETURN_NONE();
}

/* Db.put(key, data, txn=None, flags=0) */
/* */
/* A method to store key/data pairs in the database.  If the */
/* database supports duplicates, the put method adds the new data */
/* value at the end of the duplicate set. */
/* */
/* If the file is being accessed under transaction protection, the */
/* txn parameter is a transaction ID returned from beginTrans, */
/* otherwise, the autoTrans (if any) is used. */
/* */
/* The flags value is specified by or'ing together one or more of */
/* the following values: */
/* */
/* DB_APPEND */
/*      Append the key/data pair to the end of the database.  For */
/*      DB_APPEND to be specified, the underlying database must be */
/*      of type recno.  The record number allocated to the record is */
/*      returned. */
/* */
/* DB_NOOVERWRITE */
/*      Enter the new key/data pair only if the key does not already */
/*      appear in the database. */
/* */
/* The default behavior of the put method is to enter the new */
/* key/data pair, replacing any previously existing key if */
/* duplicates are disallowed, or to add a duplicate entry if */
/* duplicates are allowed.  Even if the designated database allows */
/* duplicates, a call to put with the DB_NOOVERWRITE flag set will */
/* fail if the key already exists in the database. */
/* */
/* This method raises db.error with a value of DB_KEYEXIST if the */
/* DB_NOOVERWRITE flag was set and the key already exists in the */
/* file. */
static PyObject *
DB_put(PyObject *dbobj, PyObject *args)
{
	int flags=0;
	DBObject *self = (DBObject *)dbobj;
	TxnObject *txnobj = NULL;
	PyObject *keyobj, *dataobj;
	DBT key, data;
	DB_TXN *txn;

	if(!PyArg_ParseTuple(args,"OO|O!i:", 
			     &keyobj, &dataobj, &Txn_Type, &txnobj, &flags))
		return NULL;
	if(!parse_dbt(keyobj, &key))   return NULL;
	if(!parse_dbt(dataobj, &data)) return NULL;

	if(NULL == self->db) {
		PyErr_SetString(dbError, 
				"Db object has been closed");
		return NULL;
	}

	if (!txnobj) txn = self->myenvobj->autoTrans;
	else         txn = txnobj->txn;

	if (-1 == _DB_put(self, txn, &key, &data, flags))
		return NULL;
	return Py_BuildValue("s#", key.data, key.size);
}

/* Db.set_bt_minkey(integer) */
/* */
/* Set the minimum number of keys that will be stored on any single */
/* Btree page. */

static PyObject *
DB_set_bt_minkey(PyObject *dbobj, PyObject *args)
{
	int err, minkey;
	DBObject *self = (DBObject *)dbobj;
	if(!PyArg_ParseTuple(args,"i:set_bt_minkey", &minkey ))
		return NULL;
	if(NULL == self->db) {
		PyErr_SetString(dbError, 
				"Db object has been closed");
		return NULL;
	}
	err = self->db->set_bt_minkey(self->db, minkey);
	RETURN_IF_ERR();
	RETURN_NONE();
}

/* Set the size of the database's shared memory buffer pool, */
/* i.e., the cache, to gbytes gigabytes plus bytes. The */
/* cache should be the size of the normal working data set of the */
/* application, with some small amount of additional */
/* memory for unusual situations. (Note, the working set is */
/* not the same as the number of simultaneously referenced pages, */
/* and should be quite a bit larger!)  */

static PyObject *
DB_set_cachesize(PyObject *dbobj, PyObject *args)
{
	int err;
	DBObject *self = (DBObject *)dbobj;
	int gbytes = 0, bytes = 0, ncache = 0;

	if(!PyArg_ParseTuple(args,"|iii:set_cachesize",
			     &gbytes,&bytes,&ncache))
		return NULL;
	if(NULL == self->db) {
		PyErr_SetString(dbError, 
				"Db object has been closed");
		return NULL;
	}
	err = self->db->set_cachesize(self->db, gbytes, bytes, ncache);
	RETURN_IF_ERR();
	RETURN_NONE();


}

/* Db.set_flags(flags) */
/* */
/* Calling Db->set_flags is additive, there is no way to clear flags. */
/* */
/* The flags value must be set to 0 or by bitwise inclusively OR'ing */
/* together one or more of the following values. */
/* */
/*Btree */
/* */
/* The following flags may be specified for the Btree access method: */
/* DB_DUP */
/*    Permit duplicate data items in the tree, i.e. insertion when */
/*    the key of the key/data pair being inserted already exists in */
/*    the tree will be successful. The ordering of duplicates in the */
/*    tree is determined by the order of insertion, unless the */
/*    ordering is otherwise specified by use of a cursor or a */
/*    duplicate comparison function. It is an error to specify both */
/*    DB_DUP and DB_RECNUM. */
/* DB_DUPSORT */
/*    Sort duplicates within a set of data items. If the application */
/*    does not specify a comparison function using the */
/*    DB->set_dup_compare function, a default, lexical comparison */
/*    will be used. */
/*    Specifying that duplicates are to be sorted changes the */
/*    behavior of the DB->put operation as well as the */
/*    DBcursor->c_put operation when the DB_KEYFIRST, DB_KEYLAST and */
/*    DB_CURRENT flags are specified. */
/* DB_RECNUM */
/*    Support retrieval from the Btree using record numbers. For more */
/*    information, see the DB_GET_RECNO flag to the DB->get and */
/*    DBcursor->c_get methods. */
/*    Logical record numbers in Btree databases are mutable in the */
/*    face of record insertion or deletion. See the DB_RENUMBER flag */
/*    in the Recno access method information for further discussion. */
/*    Maintaining record counts within a Btree introduces a serious */
/*    point of contention, namely the page locations where the record */
/*    counts are stored. In addition, the entire tree must be locked */
/*    during both insertions and deletions, effectively */
/*    single-threading the tree for those operations. Specifying */
/*    DB_RECNUM can result in serious performance degradation for */
/*    some applications and data sets. */
/*    It is an error to specify both DB_DUP and DB_RECNUM. */
/* DB_REVSPLITOFF */
/*    Turn off reverse splitting in the Btree. As pages are emptied */
/*    in a database, the Berkeley DB Btree implementation attempts to */
/*    coalesce empty pages into higher-level pages in order to keep */
/*    the tree as small as possible and minimize tree search time. */
/*    This can hurt performance in applications with cyclical data */
/*    demands, that is, applications where the database grows and */
/*    shrinks repeatedly. For example, because Berkeley DB does */
/*    page-level locking, the maximum level of concurrency in a */
/*    database of 2 pages is far smaller than that in a database of */
/*    100 pages, and so a database that has shrunk to a minimal size */
/*    can cause severe deadlocking when a new cycle of data insertion */
/*    begins. */
/*Hash */
/* */
/* The following flags may be specified for the Hash access method: */
/* DB_DUP */
/*    Permit duplicate data items in the tree, i.e. insertion when */
/*    the key of the key/data pair being inserted already exists in */
/*    the tree will be successful. The ordering of duplicates in the */
/*    tree is determined by the order of insertion, unless the */
/*    ordering is otherwise specified by use of a cursor or a */
/*    duplicate comparison function. */
/* DB_DUPSORT */
/*    Sort duplicates within a set of data items. If the application */
/*    does not specify a comparison function using the */
/*    DB->set_dup_compare function, a default, lexical comparison */
/*    will be used. */
/*    Specifying that duplicates are to be sorted changes the */
/*    behavior of the DB->put operation as well as the */
/*    DBcursor->c_put operation when the DB_KEYFIRST, DB_KEYLAST and */
/*    DB_CURRENT flags are specified. */
/* */
/*Queue */
/* */
/* There are no additional flags that may be specified for the Queue */
/* access method. */
/* */
/*Recno */
/* */
/* The following flags may be specified for the Recno access method: */
/* DB_RENUMBER */
/*    Specifying the DB_RENUMBER flag causes the logical record */
/*    numbers to be mutable, and change as records are added to and */
/*    deleted from the database. For example, the deletion of record */
/*    number 4 causes records numbered 5 and greater to be renumbered */
/*    downward by 1. If a cursor was positioned to record number 4 */
/*    before the deletion, it will reference the new record number 4, */
/*    if any such record exists, after the deletion. If a cursor was */
/*    positioned after record number 4 before the deletion, it will */
/*    be shifted downward 1 logical record, continuing to reference */
/*    the same record as it did before. */
/*    Using the DB->put or DBcursor->c_put interfaces to create new */
/*    records will cause the creation of multiple records if the */
/*    record number is more than one greater than the largest record */
/*    currently in the database. For example, creating record 28, */
/*    when record 25 was previously the last record in the database, */
/*    will create records 26 and 27 as well as 28. Attempts to */
/*    retrieve records that were created in this manner will result */
/*    in an error return of DB_KEYEMPTY. */
/*    If a created record is not at the end of the database, all */
/*    records following the new record will be automatically */
/*    renumbered upward by 1. For example, the creation of a new */
/*    record numbered 8 causes records numbered 8 and greater to be */
/*    renumbered upward by 1. If a cursor was positioned to record */
/*    number 8 or greater before the insertion, it will be shifted */
/*    upward 1 logical record, continuing to reference the same */
/*    record as it did before. */
/*    For these reasons, concurrent access to a Recno database with */
/*    the DB_RENUMBER flag specified may be largely meaningless, */
/*    although it is supported. */
/* DB_SNAPSHOT */
/*    This flag specifies that any specified re_source file be read */
/*    in its entirety when DB->open is called. If this flag is not */
/*    specified, the re_source file may be read lazily. */

static PyObject *
DB_set_flags(PyObject *dbobj, PyObject *args)
{
	int err, flags;
	DBObject *self = (DBObject *)dbobj;
	if(!PyArg_ParseTuple(args,"i:set_flags", &flags))
		return NULL;
	if(NULL == self->db) {
		PyErr_SetString(dbError, 
				"Db object has been closed");
		return NULL;
	}
	err = self->db->set_flags(self->db, flags);
	RETURN_IF_ERR();
	RETURN_NONE();
}

/* Db.set_h_ffactor(integer) */
/* */
/* Set the desired density within the hash table. */
/* */
/* The density is an approximation of the number of keys allowed to */
/* accumulate in any one bucket, determining when the hash table */
/* grows or shrinks. If you know the average sizes of the keys */
/* and data in your dataset, setting the fill factor can enhance */
/* performance. A reasonable rule computing fill factor is to set */
/* it to: */
/* */
/* (pagesize - 32) / (average_key_size + average_data_size + 8) */
/* */
/* If no value is specified, the fill factor will be selected */
/* dynamically as pages are filled. */

static PyObject *
DB_set_h_ffactor(PyObject *dbobj, PyObject *args)
{
	int err, ffactor;
	DBObject *self = (DBObject *)dbobj;
	if(!PyArg_ParseTuple(args,"i:set_h_ffactor", &ffactor))
		return NULL;
	if(NULL == self->db) {
		PyErr_SetString(dbError, 
				"Db object has been closed");
		return NULL;
	}
	err = self->db->set_h_ffactor(self->db, ffactor);
	RETURN_IF_ERR();
	RETURN_NONE();
}

/* Db.set_h_nelem(integer) */
/* */
/* Set an estimate of the final size of the hash table. */
/* */
/* If not set or set too low, hash tables will still expand */
/* gracefully as keys are entered, although a slight performance */
/* degradation may be noticed. */

static PyObject *
DB_set_h_nelem(PyObject *dbobj, PyObject *args)
{
	int err, nelem;
	DBObject *self = (DBObject *)dbobj;
	if(!PyArg_ParseTuple(args,"i:set_h_nelem", &nelem))
		return NULL;
	if(NULL == self->db) {
		PyErr_SetString(dbError, 
				"Db object has been closed");
		return NULL;
	}
	err = self->db->set_h_nelem(self->db, nelem);
	RETURN_IF_ERR();
	RETURN_NONE();
}

/* Set the byte order for integers in the stored database metadata. */
/* The number should represent the order as an integer, for example, */
/* big endian order is the number 4,321, and little endian order is */
/* the number 1,234. If lorder is not explicitly set, the host order */
/* of the machine where the Berkeley DB library was compiled is used. */
/* */
/* The value of lorder is ignored except when databases are being */
/* created. */

static PyObject *
DB_set_lorder(PyObject *dbobj, PyObject *args)
{
	int err, lorder;
	DBObject *self = (DBObject *)dbobj;

	if(!PyArg_ParseTuple(args,"i:set_lorder",
			     &lorder))
		return NULL;
	if(NULL == self->db) {
		PyErr_SetString(dbError, 
				"Db object has been closed");
		return NULL;
	}

	err = self->db->set_lorder(self->db, lorder);
	RETURN_IF_ERR();
	RETURN_NONE();
}

/* Db.set_pagesize(integer) */
/* */
/* Set the size of the pages used to hold items in the database, */
/* in bytes. The minimum page size is 512 bytes and the maximum */
/* page size is 64K bytes. If the page size is not explicitly set, */
/* one is selected based on the underlying filesystem I/O block */
/* size. The automatically selected size has a lower limit of 512 */
/* bytes and an upper limit of 16K bytes. */

static PyObject *
DB_set_pagesize(PyObject *dbobj, PyObject *args)
{
	int err, pagesize;
	DBObject *self = (DBObject *)dbobj;
	if(!PyArg_ParseTuple(args,"i:set_pagesize", &pagesize))
		return NULL;
	if(NULL == self->db) {
		PyErr_SetString(dbError, 
				"Db object has been closed");
		return NULL;
	}
	err = self->db->set_pagesize(self->db, pagesize);
	RETURN_IF_ERR();
	RETURN_NONE();

}

/* Db.set_re_delim(integer) */
/* */
/* Set the delimiting byte used to mark the end of a record in the */
/* backing source file for the Recno access method. */
/* */
/* This byte is used for variable length records, if the re_source */
/* file is specified. If the re_source file is specified and no */
/* delimiting byte was specified, <newline> characters (i.e. ASCII */
/* 0x0a) are interpreted as end-of-record markers. */

static PyObject *
DB_set_re_delim(PyObject *dbobj, PyObject *args)
{
	int err, delim;
	DBObject *self = (DBObject *)dbobj;
	if(!PyArg_ParseTuple(args,"i:set_re_delim", &delim))
		return NULL;
	if(NULL == self->db) {
		PyErr_SetString(dbError, 
				"Db object has been closed");
		return NULL;
	}
	err = self->db->set_re_delim(self->db, delim);
	RETURN_IF_ERR();
	RETURN_NONE();

}

/* Db.set_re_len(integer) */
/* */
/* For the Queue access method, specify that the records are of */
/* length re_len. */
/* */
/* For the Recno access method, specify that the records are */
/* fixed-length, not byte delimited, and are of length re_len. */
/* */
/* Any records added to the database that are less than re_len */
/* bytes long are automatically padded (see DB->set_re_pad for */
/* more information). */

static PyObject *
DB_set_re_len(PyObject *dbobj, PyObject *args)
{
	int err, len;
	DBObject *self = (DBObject *)dbobj;
	if(!PyArg_ParseTuple(args,"i:set_re_len", &len))
		return NULL;
	if(NULL == self->db) {
		PyErr_SetString(dbError, 
				"Db object has been closed");
		return NULL;
	}
	err = self->db->set_re_len(self->db, len);
	RETURN_IF_ERR();
	RETURN_NONE();
}

/* Db.set_re_pad(string) */
/* */
/* Set the padding character for short, fixed-length records for the */
/* Queue and Recno access methods.  If no pad character is specified, */
/* <space> characters (i.e., ASCII 0x20) are used for padding. */
/* The DB->set_re_pad interface may only be used to configure */
/* Berkeley DB before the DB->open interface is called. */
/* */
/* The first character of the given string will be used. */

static PyObject *
DB_set_re_pad(PyObject *dbobj, PyObject *args)
{
	int err;
	char *pad;
	DBObject *self = (DBObject *)dbobj;
	if(!PyArg_ParseTuple(args,"s:set_re_pad", &pad))
		return NULL;
	if(NULL == self->db) {
		PyErr_SetString(dbError, 
				"Db object has been closed");
		return NULL;
	}
	err = self->db->set_re_pad(self->db, *pad);
	RETURN_IF_ERR();
	RETURN_NONE();
}

/* Db.set_re_source(string) */
/* */
/* Set the underlying source file for the Recno access method. The */
/* purpose of the re_source value is to provide fast access and */
/* modification to databases that are normally stored as flat */
/* text files. */
/* */
/* If the re_source field is set, it specifies an underlying flat */
/* text database file that is read to initialize a transient record */
/* number index. In the case of variable length records, the records */
/* are separated as specified by DB->set_re_delim. For example, */
/* standard UNIX byte stream files can be interpreted as a sequence */
/* of variable length records separated by <newline> characters. */
/* */
/* In addition, when cached data would normally be written back to */
/* the underlying database file (e.g., the DB->close or DB->sync */
/* methods are called), the in-memory copy of the database will be */
/* written back to the re_source file. */

static PyObject *
DB_set_re_source(PyObject *dbobj, PyObject *args)
{
	int err;
	char *re_source;
	DBObject *self = (DBObject *)dbobj;
	if(!PyArg_ParseTuple(args,"s:set_re_source", &re_source))
		return NULL;
	if(NULL == self->db) {
		PyErr_SetString(dbError, 
				"Db object has been closed");
		return NULL;
	}
	err = self->db->set_re_source(self->db, re_source);
	RETURN_IF_ERR();
	RETURN_NONE();
}

/* Db.sync() */
/* */
/* This method flushes any cached information to disk. */
static PyObject *
DB_sync(PyObject *dbobj, PyObject *args)
{
	int err;
	DBObject *self = (DBObject *)dbobj;
	if(!PyArg_ParseTuple(args,":sync" ))
		return NULL;
	if(NULL == self->db) {
		PyErr_SetString(dbError, 
				"Db object has been closed");
		return NULL;
	}
	MYDB_BEGIN_ALLOW_THREADS;
	err = self->db->sync(self->db, 0);
	MYDB_END_ALLOW_THREADS;
	RETURN_IF_ERR();
	RETURN_NONE();
}

/* Db.type() */
/* */
/* The type of the underlying access method (and file format).  Set to */
/* one of DB_BTREE, DB_HASH or DB_RECNO.  This field may be used to */
/* determine the type of the database after a return from open with */
/* the type argument set to DB_UNKNOWN. */

static PyObject *
DB_type(PyObject *dbobj, PyObject *args)
{
	int t;
	DBObject *self = (DBObject *)dbobj;
	if(!PyArg_ParseTuple(args,":type"))
		return NULL;
	if(NULL == self->db) {
		PyErr_SetString(dbError, 
				"Db object has been closed");
		return NULL;
	}
	MYDB_BEGIN_ALLOW_THREADS;
	t = self->db->get_type(self->db);
	MYDB_END_ALLOW_THREADS;
	return PyInt_FromLong(t);
}

/* Db.upgrade(string file, flags=0) */
/*   Upgrades all databases included in the file filename if necessary. */
/*   Upgrades are done in place and are destructive.  Unlike other */
/*   BerkeleyDB operations, upgrades may only be done on a system */
/*   with the same byte-order as the database. */
/*   ** Backups should be made before databases are upgraded! ** */

static PyObject *
DB_upgrade(PyObject *dbobj, PyObject *args)
{
	int err, flags=0;
	char *filename;
	DBObject *self = (DBObject *)dbobj;
	if(!PyArg_ParseTuple(args,"s|i:upgrade", &filename, &flags))
		return NULL;
	if(NULL == self->db) {
		PyErr_SetString(dbError, 
				"Db object has been closed");
		return NULL;
	}
	MYDB_BEGIN_ALLOW_THREADS;
	err = self->db->upgrade(self->db, filename, flags);
	MYDB_END_ALLOW_THREADS;
	RETURN_IF_ERR();
	RETURN_NONE();
}

/*----------------------------------------------------- */
/* Dictionary access routines */
/*----------------------------------------------------- */

int DB_length(DBObject *self) {
	int err;
	DBT key;
	DBT data;
	DBC *cursor = NULL;
	long size = 0;
	
	if(NULL == self->db) {
		PyErr_SetString(dbError, 
				"Db object has been closed");
		return -1;
	}
	if (self->size < 0) {       /* recompute */
                memset(&key, 0, sizeof(DBT));
                memset(&data, 0, sizeof(DBT));
                MYDB_BEGIN_ALLOW_THREADS;
                err = self->db->cursor(self->db, self->myenvobj->autoTrans, &cursor, 0);
                MYDB_END_ALLOW_THREADS;
		if (err != 0) {                                     
			PyErr_SetObject(dbError, makeDbError(err));     
			return -1;                                    
		}
                while (1) {
			if (CHECK_DBFLAG(self, DB_THREAD)) {
				/* XXX tons of mallocs are highly inefficient */
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
			return -1;
                }
                self->size = size;
	}
	if (cursor)
                cursor->c_close(cursor);
	return self->size;
}

PyObject* DB_subscript(PyObject* dbobj, PyObject *pyKey) {
	int err;
	DBObject *self = (DBObject *)dbobj;
	PyObject *retval;
	DBT key;
	DBT data;

	if(NULL == self->db) {
		PyErr_SetString(dbError, 
				"Db object has been closed");
		return NULL;
	}
	memset(&key, 0, sizeof(key));
	if (!PyArg_Parse(pyKey, "s#", &key.data, &key.size)) {
                PyErr_SetString(PyExc_TypeError, "Key must be a string.");
                return NULL;
	}

	memset(&data, 0, sizeof(DBT));
	if (CHECK_DBFLAG(self, DB_THREAD)) {
                /* Tell BerkeleyDB to malloc the return value (thread safe) */
                data.flags = DB_DBT_MALLOC;
	}
	MYDB_BEGIN_ALLOW_THREADS;
	err = self->db->get(self->db, self->myenvobj->autoTrans, &key, &data, 0);
	MYDB_END_ALLOW_THREADS;
	if (err) {
                if (err == DB_NOTFOUND)
			PyErr_SetObject(PyExc_KeyError, pyKey);
                else
			PyErr_SetObject(dbError, makeDbError(err));
                return NULL;
	}

	retval = PyString_FromStringAndSize((char*)data.data, data.size);
	if (CHECK_DBFLAG(self, DB_THREAD) && (data.data != NULL)) {
                free(data.data);  /* free any malloc'd return value */
	}

	return retval;
}

static int 
DB_ass_sub(DBObject *self, PyObject *keyobj, PyObject *dataobj) {
	DBT key, data;
	if(!parse_dbt(keyobj, &key))  return -1;

	if(NULL == self->db) {
		PyErr_SetString(dbError, 
				"Db object has been closed");
		return -1;
	}

	if (dataobj != NULL) {
		if(!parse_dbt(dataobj, &data)) return -1;
		return _DB_put(self, self->myenvobj->autoTrans, 
			       &key, &data, 0);
	}
	else {
		/* dataobj == NULL, so delete the key */
		return _DB_delete(self, self->myenvobj->autoTrans, &key, 0);
	}
}

/* --------------------------------------------------------------------- */
/* DBC methods */

/* class Dbc */
/* */
/*  The Dbc (Database Cursor) class supports sequential access to the records */
/*  stored in a given databse file.  Cursors are created by calling the cursor */
/*  method of an instance of the DB class. */
/* */
/*  Each cursor maintains positioning information within a set of key/data pairs. */
/*  In the presence of transactions, cursors are only valid within the context of */
/*  a single transaction, the one specified during the cursor method of the DB */
/*  class. All cursor operations will be executed in the context of that */
/*  transaction.  Before aborting or committing a transaction, all cursors used */
/*  within that transaction must be closed.  In the presence of transactions, the */
/*  application must call abortTrans() (or abortAutoTrans() as appropriate) if */
/*  any of the cursor operations raises an exception, indicating that a deadlock */
/*  (DB_LOCK_DEADLOCK) or system failure occurred. */
/* */
/*  When locking is enabled, page locks are retained between consecutive cursor */
/*  calls.  For this reason, in the presence of locking, applications should */
/*  discard cursors as soon as they are done with them.  Calling the DB.close */
/*  method discards any cursors opened from that DB. */
/* */

        /* Dbc.close() */
        /* */
        /* The cursor is discarded.  No further references to this cursor */
        /* should be made. */
        /* */

static PyObject *
DBC_close(PyObject *dbcobj, PyObject *args)
{
	int err = 0;
	DBCObject *self = (DBCObject *)dbcobj;
	if (!PyArg_ParseTuple(args, ":close")) 
		return NULL;
	MYDB_BEGIN_ALLOW_THREADS;
	if (self->dbc != NULL) {
	  err = self->dbc->c_close(self->dbc);
	  self->dbc = NULL;
	}
	MYDB_END_ALLOW_THREADS;
	RETURN_IF_ERR();
	RETURN_NONE();
}

/* Dbc.current() */
/* */
/* A convenience method.  Equivalent to calling get with DB_CURRENT. */
static PyObject *
DBC_current(PyObject *dbcobj, PyObject *args)
{
	DBCObject *self = (DBCObject *)dbcobj;
	if (!PyArg_ParseTuple(args, ":current")) 
		return NULL;
	return _DBC_get(self, DB_CURRENT);
}

/* Dbc.delete() */
/* */
/* The key/data pair currently referenced by the cursor is removed */
/* from the database. */
/* */
/* The cursor position is unchanged after a delete and subsequent */
/* calls to cursor functions expecting the cursor to reference an */
/* existing key will fail. */
static PyObject *
DBC_delete(PyObject *dbcobj, PyObject *args)
{
	int err, flags=0;
	DBCObject *self = (DBCObject *)dbcobj;
	if (!PyArg_ParseTuple(args, "|i:delete", &flags)) 
		return NULL;
	MYDB_BEGIN_ALLOW_THREADS;
	err = self->dbc->c_del(self->dbc, flags);
	MYDB_END_ALLOW_THREADS;
	RETURN_IF_ERR();
	self->mydb->size = -1;
	RETURN_NONE();
}

/* Dbc.first() */
/* */
/* A convenience method.  Equivalent to calling get with DB_FIRST. */
static PyObject *
DBC_first(PyObject *dbcobj, PyObject *args)
{
	DBCObject *self = (DBCObject *)dbcobj;
	if (!PyArg_ParseTuple(args, ":first")) 
		return NULL;
	return _DBC_get(self, DB_FIRST);
}

/* Dbc.get(flags) */
/* */
/* This function returns a tuple containing a key and data value from */
/* the database. */
/* */
/* Modifications to the database during a sequential scan will be */
/* reflected in the scan, i.e. records inserted behind a cursor will */
/* not be returned while records inserted in front of a cursor will */
/* be returned. */
/* */
/* If multiple threads or processes insert items into the same */
/* database file without using locking, the results are undefined. */
/* */
/* The parameter flags must be set to exactly one of the following */
/* values: */
/* */
/*    DB_FIRST */
/*        The cursor is set to reference the first key/data pair of the */
/*        database, and that pair is returned.  In the presence of */
/*        duplicate key values, the first data item in the set of */
/*        duplicates is returned.  If the database is empty, this */
/*        function will return None. */
/* */
/*    DB_LAST */
/*        The cursor is set to reference the last key/data pair of the */
/*        database, and that pair is returned. In the presence of */
/*        duplicate key values, the last data item in the set of */
/*        duplicates is returned.  If the database is empty, this */
/*        method will return None. */
/* */
/*    DB_NEXT */
/*        If the cursor is not yet initialized, DB_NEXT is identical to */
/*        DB_FIRST.  Otherwise, move the cursor to the next key/data */
/*        pair of the database, and that pair is returned. In the */
/*        presence of duplicate key values, the key may not change.  If */
/*        the cursor is already on the last record in the database, */
/*        this method will return None. */
/* */
/*    DB_PREV */
/*        If the cursor is not yet initialized, DB_PREV is identical to */
/*        DB_LAST. Otherwise, move the cursor to the previous key/data */
/*        pair of the database, and that pair is returned.  In the */
/*        presence of duplicate key values, the key may not change.  If */
/*        the cursor is already on the first record in the database, */
/*        this method will return None. */
/* */
/*    DB_CURRENT */
/*        Return the key/data pair currently referenced by the cursor. */
/*        If the cursor key/data pair has been deleted, this method */
/*        will return DB_KEYEMPTY.  If the cursor is not yet */
/*        initialized, the get method will raise db.error with a value */
/*        of EINVAL. */
static PyObject *
DBC_get(PyObject *dbcobj, PyObject *args)
{
	int flags;
	DBCObject *self = (DBCObject *)dbcobj;
	if (!PyArg_ParseTuple(args, "i:get", &flags)) 
		return NULL;
	return _DBC_get(self, flags);
}

/* Dbc.getRecno() */
/* */
/* Return the record number associated with the cursor.  For this */
/* method to be used, the underlying database must be of type btree */
/* and it must have been created with the DB_RECNUM flag. */
static PyObject *
DBC_getRecno(PyObject *dbcobj, PyObject *args)
{
	int err;
	DBCObject *self = (DBCObject *)dbcobj;
	db_recno_t recno;
	DBT key;
	DBT data;
	if (!PyArg_ParseTuple(args, ":getRecno")) 
		return NULL;
	memset(&key, 0, sizeof(key));
	memset(&data, 0, sizeof(data));
	if (CHECK_DBFLAG(self->mydb, DB_THREAD)) {
                /* Tell BerkeleyDB to malloc the return value (thread safe) */
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

/* Dbc.last() */
/* */
/* A convenience method.  Equivalent to calling get with DB_LAST. */
static PyObject *
DBC_last(PyObject *dbcobj, PyObject *args)
{
	DBCObject *self = (DBCObject *)dbcobj;
	if (!PyArg_ParseTuple(args, ":last")) 
		return NULL;
	return _DBC_get(self, DB_LAST);
}

/* Dbc.next() */
/* */
/* A convenience method.  Equivalent to calling get with DB_NEXT. */
static PyObject *
DBC_next(PyObject *dbcobj, PyObject *args)
{
	DBCObject *self = (DBCObject *)dbcobj;
	if (!PyArg_ParseTuple(args, ":next")) 
		return NULL;
	return _DBC_get(self, DB_NEXT);
}

/* Dbc.prev() */
/* */
/* A convenience method.  Equivalent to calling get with DB_PREV. */
static PyObject *
DBC_prev(PyObject *dbcobj, PyObject *args)
{
	DBCObject *self = (DBCObject *)dbcobj;
	if (!PyArg_ParseTuple(args, ":prev")) 
		return NULL;
	return _DBC_get(self, DB_PREV);
}

/* Dbc.put(key, data, flags) */
/* */
/* This method stores key/data pairs into the database.  The flags */
/* parameter must be set to exactly one of the following values: */
/* */
/*    DB_AFTER */
/*            In the case of the btree and hash access methods, insert the */
/*            data element as a duplicate element of the key referenced by */
/*            the cursor.  The new element appears immediately after the */
/*            current cursor position.  It is an error to specify DB_AFTER */
/*            if the underlying btree or hash database was not created */
/*            with the DB_DUP flag. The key parameter is ignored. */
/* */
/*            In the case of the recno access method, it is an error to */
/*            specify DB_AFTER if the underlying recno database was not */
/*            created with the DB_RENUMBER flag.  If the DB_RENUMBER flag */
/*            was specified, a new key is created, all records after the */
/*            inserted item are automatically renumbered.  The initial */
/*            value of the key parameter is ignored. */
/* */
/*    DB_BEFORE */
/*            Identical to DB_AFTER except the new element appears */
/*            immediately before the current cursor position. */
/* */
/*    DB_CURRENT */
/*            Overwrite the data of the key/data pair referenced by the */
/*            cursor with the specified data item.  The key parameter is */
/*            ignored. */
/* */
/*    DB_KEYFIRST */
/*            In the case of the btree and hash access methods, insert the */
/*            specified key/data pair into the database.  If the key */
/*            already exists in the database, the inserted data item is */
/*            added as the first of the data items for that key. */
/* */
/*            The DB_KEYFIRST flag may not be specified to the recno access */
/*            method. */
/* */
/*    DB_KEYLAST */
/*            Insert the specified key/data pair into the database.  If */
/*            the key already exists in the database, the inserted data */
/*            item is added as the last of the data items for that key. */
/* */
/*            The DB_KEYLAST flag may not be specified to the recno access */
/*            method. */
/* */
/* If the cursor record has been deleted, the put method raises */
/* db.error with value of DB_KEYEMPTY. */
/* */
/* If the put method fails for any reason, the state of the cursor */
/* will be unchanged.  If put succeeds and an item is inserted */
/* into the database, the cursor is always positioned to reference */
/* the newly inserted item. */

static PyObject *
DBC_put(PyObject *dbcobj, PyObject *args)
{
	int err, flags;
	PyObject *keyobj, *dataobj;
	DBCObject *self = (DBCObject *)dbcobj;
	DBT key, data;

	if (!PyArg_ParseTuple(args, "OOi:put", &keyobj, &dataobj, &flags)) 
		return NULL;
	if (!parse_dbt(keyobj,  &key)) return NULL;
	if (!parse_dbt(dataobj, &data)) return NULL;

	MYDB_BEGIN_ALLOW_THREADS;
	err = self->dbc->c_put(self->dbc, &key, &data, flags);
	MYDB_END_ALLOW_THREADS;
	RETURN_IF_ERR();
	self->mydb->size = -1;
	RETURN_NONE();

}

/* Dbc.set(key) */
/* */
/* Move the cursor to the specified key of the database, and return */
/* the given key/data pair. In the presence of duplicate key values, */
/* the method will return the first key/data pair for the given key. */
/* */
/* If the database is a recno database and the requested key exists, */
/* but was never explicitly created by the application or was later */
/* deleted, the set method raises db.error with a value of */
/* DB_KEYEMPTY. */
/* */
/* The range parameter can be set to true in BTREE databases to set */
/* the position to the smallest key greater than or equal too the */
/* specified key.  This allows for partial key matches and range */
/* searches. */
/* */
/* If no matching keys are found, this method will raise db.error */
/* with a value of DB_NOTFOUND. */
static PyObject *
DBC_set(PyObject *dbcobj, PyObject *args)
{
	int err;
	DBCObject *self = (DBCObject *)dbcobj;
	DBT key, data;
	PyObject *retval, *obj;
	
	if (!PyArg_ParseTuple(args, "O:set", &obj)) 
		return NULL;
	if (!parse_dbt(obj, &key)) 
		return NULL;

	memset(&data, 0, sizeof(data));
	if (CHECK_DBFLAG(self->mydb, DB_THREAD)) {
                /* Tell BerkeleyDB to malloc the return value (thread safe) */
                data.flags = DB_DBT_MALLOC;
                key.flags = DB_DBT_MALLOC;
	}
	MYDB_BEGIN_ALLOW_THREADS;
	err = self->dbc->c_get(self->dbc, &key, &data, DB_SET);
	MYDB_END_ALLOW_THREADS;
	RETURN_IF_ERR();
	retval = Py_BuildValue("s#s#", key.data, key.size,
			       data.data, data.size);
	if (CHECK_DBFLAG(self->mydb, DB_THREAD)) {
                if (key.data != NULL) free(key.data);
                if (data.data != NULL) free(data.data);
	}
	return retval;
}

/* Dbc.setRange(key) */
/* */
/* Identical to the set method, except in the case of the btree access */
/* method, the returned key/data pair is the smallest key greater than */
/* or equal to the specified key, permitting partial key matches and */
/* range searches. */
static PyObject *
DBC_setRange(PyObject *dbcobj, PyObject *args)
{
	int err;
	DBCObject *self = (DBCObject *)dbcobj;
	DBT key, data;
	PyObject *retval, *obj;

	if (!PyArg_ParseTuple(args, "O:setRange", &obj)) 
		return NULL;
	if (!parse_dbt(obj, &key)) 
		return NULL;

	memset(&data, 0, sizeof(data));
	if (CHECK_DBFLAG(self->mydb, DB_THREAD)) {
                /* Tell BerkeleyDB to malloc the return value (thread safe) */
                data.flags = DB_DBT_MALLOC;
                key.flags = DB_DBT_MALLOC;
	}
	MYDB_BEGIN_ALLOW_THREADS;
	err = self->dbc->c_get(self->dbc, &key, &data, DB_SET_RANGE);
	MYDB_END_ALLOW_THREADS;
	RETURN_IF_ERR();
	retval = Py_BuildValue("s#s#", key.data, key.size,
			       data.data, data.size);
	if (CHECK_DBFLAG(self->mydb, DB_THREAD)) {
                if (key.data != NULL) free(key.data);
                if (data.data != NULL) free(data.data);
	}
	return retval;
}

/* Dbc.getBoth(key, value) */
/* */
/* Identical to the set method, except that both the key and the data
       arguments must be matched by the key and data item in the
       database. This is handy for deleting a record in a set of
       duplicate-key records.  */
static PyObject *
DBC_getBoth(PyObject *dbcobj, PyObject *args)
{
	int err;
	DBCObject *self = (DBCObject *)dbcobj;
	DBT key, data;
	PyObject *retval, *obj, *oval;

	if (!PyArg_ParseTuple(args, "OO:getBoth", &obj, &oval)) 
		return NULL;
	if (!parse_dbt(obj, &key)) 
		return NULL;
	if (!parse_dbt(oval, &data)) 
		return NULL;

	if (CHECK_DBFLAG(self->mydb, DB_THREAD)) {
                /* Tell BerkeleyDB to malloc the return value (thread safe) */
                data.flags = DB_DBT_MALLOC;
                key.flags = DB_DBT_MALLOC;
	}
	MYDB_BEGIN_ALLOW_THREADS;
	err = self->dbc->c_get(self->dbc, &key, &data, DB_GET_BOTH);
	MYDB_END_ALLOW_THREADS;
	RETURN_IF_ERR();
	retval = Py_BuildValue("s#s#", key.data, key.size,
			       data.data, data.size);
	if (CHECK_DBFLAG(self->mydb, DB_THREAD)) {
                if (key.data != NULL) free(key.data);
                if (data.data != NULL) free(data.data);
	}
	return retval;
}

/* Dbc.setRecno(recno) */
/* */
/* Move the cursor to the specific numbered record of the database, and */
/* return the associated key/data pair.  For this method to be used, the */
/* underlying database must be of type btree and it must have been */
/* created with the DB_RECNUM flag. */
static PyObject *
DBC_setRecno(PyObject *dbcobj, PyObject *args)
{
	int err, int_recno;
	db_recno_t recno;
	DBCObject *self = (DBCObject *)dbcobj;
	DBT key, data;
	PyObject *retval;
	    
	if (!PyArg_ParseTuple(args, "i:setRecno", &int_recno)) 
		return NULL;
	recno = (db_recno_t) int_recno;
	key.data = &recno;
	key.size = sizeof(db_recno_t);
	key.ulen = key.size;
	key.flags = DB_DBT_USERMEM;
	memset(&data, 0, sizeof(data));
	if (CHECK_DBFLAG(self->mydb, DB_THREAD)) {
                /* Tell BerkeleyDB to malloc the return value (thread safe) */
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

/* --------------------------------------------------------------------- */
/* DBEnv methods */

/* abortAutoTrans() */
/* */
/* Aborts and rolls-back the active automatic transaction. */
static PyObject *
DBEnv_abortAutoTrans(PyObject *dbenvobj, PyObject *args)
{
	int err;
	DBEnvObject *self = (DBEnvObject *)dbenvobj;
	if (!PyArg_ParseTuple(args, ":abortAutoTrans")) return NULL;
	if (self->atRefCnt) {
                err = txn_abort(self->autoTrans);
                self->autoTrans = NULL;
                self->atRefCnt = 0;
                RETURN_IF_ERR();
	}
	RETURN_NONE();
}

/* beginAutoTrans(flags=0) */
/* */
/* This function begins an "Automatic Transaction."  An automatic */
/* transaction automatically involves all DB method calls including the */
/* dictionary simulation routines, until the transaction is commited or */
/* aborted.  There can only be one automatic transaction in any process */
/* at a time, however nested calls can be made to beginAutoTrans and */
/* commitAutoTrans are supported via reference counting.  abortAutoTrans */
/* ignores the nesting count and performs the abort. */
static PyObject *
DBEnv_beginAutoTrans(PyObject *dbenvobj, PyObject *args)
{
	int err, flags=0;
	DBEnvObject *self = (DBEnvObject *)dbenvobj;
	if (!PyArg_ParseTuple(args, "i:beginAutoTrans", &flags)) 
		return NULL;
	if (self->atRefCnt == 0) {
                err = txn_begin(self->db_env, NULL, &self->autoTrans, flags);
                RETURN_IF_ERR();
	}
	self->atRefCnt += 1;
	RETURN_NONE();
}

/* close() */
/*   Close this database environment by freeing any allocated resources */
/*   and closing any underlying subsystems. */
static PyObject *
DBEnv_close(PyObject *dbenvobj, PyObject *args)
{
	int err;
	DBEnvObject *self = (DBEnvObject *)dbenvobj;
	if (!PyArg_ParseTuple(args, ":close")) 
		return NULL;
	if (!self->closed) {      /* Don't close more than once */
                err = self->db_env->close(self->db_env, 0);
                RETURN_IF_ERR();
                self->closed = 1;
	}
	RETURN_NONE();
}

/* commitAutoTrans(flags=0) */
/* */
/* This function ends the active automatic transaction, commiting the */
/* changes to the database. */
static PyObject *
DBEnv_commitAutoTrans(PyObject *dbenvobj, PyObject *args)
{
	int err, flags=0;
	DBEnvObject *self = (DBEnvObject *)dbenvobj;
	if (!PyArg_ParseTuple(args, "|i:commitAutoTrans", &flags)) 
		return NULL;
	self->atRefCnt -= 1;
	if (self->atRefCnt == 0) {
                err = txn_commit(self->autoTrans, flags);
                RETURN_IF_ERR();
	}
	RETURN_NONE();
}

/* open(string db_home, integer flags) */
/*   Open/initialize the database environment. */
static PyObject *
DBEnv_open(PyObject *dbenvobj, PyObject *args)
{
	int err, flags;
	char *db_home;
	PyObject *db_homeobj;
	DBEnvObject *self = (DBEnvObject *)dbenvobj;

	if (!PyArg_ParseTuple(args, "Oi:open", &db_homeobj, &flags)) 
		return NULL;
	if (db_homeobj == Py_None) {
	  db_home = NULL;
	}
	else if (PyString_Check(db_homeobj) ) {
	  db_home = PyString_AsString( db_homeobj );
	}
	else {
	  PyErr_SetString(PyExc_ValueError, "first argument must be string or None");
	  return NULL;
	}

	err = self->db_env->open(self->db_env, db_home, flags, 0);
	RETURN_IF_ERR();
	self->closed = 0;
	self->flags = flags;
	RETURN_NONE();
}

/* prepareAutoTrans() */
/* */
/* If the active automatic transaction is involved in a distributed */
/* transaction system, this function should be called to begin the */
/* two-phase commit. */
static PyObject *
DBEnv_prepareAutoTrans(PyObject *dbenvobj, PyObject *args)
{
	int err;
	DBEnvObject *self = (DBEnvObject *)dbenvobj;
	if (!PyArg_ParseTuple(args, ":prepareAutoTrans")) return NULL;
	if (self->atRefCnt) {
                err = txn_prepare(self->autoTrans);
                RETURN_IF_ERR();
	}
	RETURN_NONE();
}

/* set_cachesize(gbytes=0, bytes=0, ncache=0) */
/* */
/* Set the size of this database's shared memory buffer pool, */
/* i.e., the cache, to gbytes gigabytes plus bytes. The */
/* cache should be the size of the normal working data set of the */
/* application, with some small amount of additional */
/* memory for unusual situations. (Note, the working set is */
/* not the same as the number of simultaneously referenced pages, */
/* and should be quite a bit larger!)  */
static PyObject *
DBEnv_set_cachesize(PyObject *dbenvobj, PyObject *args)
{
	int err, gbytes=0, bytes=0, ncache=0;
	DBEnvObject *self = (DBEnvObject *)dbenvobj;
	if (!PyArg_ParseTuple(args, "|iii:set_cachesize",
			      &gbytes, &bytes, &ncache))
		return NULL;
	err = self->db_env->set_cachesize(self->db_env, gbytes, bytes, ncache);
	RETURN_IF_ERR();
	RETURN_NONE();
}

/* set_data_dir(string dir) */
/*   Set the path of a directory to be used as the location of the */
/*   access method database files.  See BerkeleyDB docs for */
/*   more detailed info. */
static PyObject *
DBEnv_set_data_dir(PyObject *dbenvobj, PyObject *args)
{
	int err;
	char *dir;
	DBEnvObject *self = (DBEnvObject *)dbenvobj;
	if (!PyArg_ParseTuple(args, "s:set_data_dir", &dir)) 
		return NULL;
	err = self->db_env->set_data_dir(self->db_env, dir);
	RETURN_IF_ERR();
	RETURN_NONE();
}

/* set_lg_bsize(integer) */
/* */
/* Set the size of the in-memory log buffer, in bytes. */
static PyObject *
DBEnv_set_lg_bsize(PyObject *dbenvobj, PyObject *args)
{
	int err, lg_bsize;
	DBEnvObject *self = (DBEnvObject *)dbenvobj;
	if (!PyArg_ParseTuple(args, "i:set_lg_bsize", &lg_bsize)) 
		return NULL;
	err = self->db_env->set_lg_bsize(self->db_env, lg_bsize);
	RETURN_IF_ERR();
	RETURN_NONE();
}

/* set_lg_dir(string dir) */
/*   The path of a directory to be used as the location of logging files. */
static PyObject *
DBEnv_set_lg_dir(PyObject *dbenvobj, PyObject *args)
{
	int err;
	char *dir;
	DBEnvObject *self = (DBEnvObject *)dbenvobj;
	if (!PyArg_ParseTuple(args, "s:set_lg_dir", &dir))
		return NULL;
	err = self->db_env->set_lg_dir(self->db_env, dir);
	RETURN_IF_ERR();
	RETURN_NONE();
}

/* set_lg_max(integer) */
/* */
/* Set the maximum size of a single file in the log, in bytes. Because */
/* DbLsn file offsets are unsigned 4-byte values, the set value may not */
/* be larger than the maximum unsigned 4-byte value. */
static PyObject *
DBEnv_set_lg_max(PyObject *dbenvobj, PyObject *args)
{
	int err, lg_max;
	DBEnvObject *self = (DBEnvObject *)dbenvobj;
	if (!PyArg_ParseTuple(args, "i:set_lg_max", &lg_max)) return NULL;
	err = self->db_env->set_lg_max(self->db_env, lg_max);
	RETURN_IF_ERR();
	RETURN_NONE();
}

/* set_lk_detect(integer) */
/* */
/* Set if the deadlock detector is to be run whenever a lock conflict */
/* occurs, and specify which transaction should be aborted in the case */
/* of a deadlock. The specified value must be one of the following list: */
/* DB_LOCK_DEFAULT */
/*       Use the default policy as specified by db_deadlock. */
/* DB_LOCK_OLDEST */
/*       Abort the oldest transaction. */
/* DB_LOCK_RANDOM */
/*       Abort a random transaction involved in the deadlock. */
/* DB_LOCK_YOUNGEST */
/*       Abort the youngest transaction. */
static PyObject *
DBEnv_set_lk_detect(PyObject *dbenvobj, PyObject *args)
{
	int err, lk_detect;
	DBEnvObject *self = (DBEnvObject *)dbenvobj;
	if (!PyArg_ParseTuple(args, "i:set_lk_detect", &lk_detect)) 
		return NULL;
	err = self->db_env->set_lk_detect(self->db_env, lk_detect);
	RETURN_IF_ERR();
	RETURN_NONE();
}

/* set_mp_mmapsize(integer) */
/*  */
/* Set the maximum file size, in bytes, for a file to be mapped into the */
/* process address space. If no value is specified, it defaults to 10MB. */
static PyObject *
DBEnv_set_mp_mmapsize(PyObject *dbenvobj, PyObject *args)
{
	int err, mp_mmapsize;
	DBEnvObject *self = (DBEnvObject *)dbenvobj;
	if (!PyArg_ParseTuple(args, "i:set_mp_mmapsize", &mp_mmapsize)) 
		return NULL;
	err = self->db_env->set_mp_mmapsize(self->db_env, mp_mmapsize);
	RETURN_IF_ERR();
	RETURN_NONE();
}

/* set_tmp_dir(string dir) */
/*   The path of a directory to be used as the location of temporary files. */
static PyObject *
DBEnv_set_tmp_dir(PyObject *dbenvobj, PyObject *args)
{
	int err;
	char *dir;
	DBEnvObject *self = (DBEnvObject *)dbenvobj;
	if (!PyArg_ParseTuple(args, "s:set_tmp_dir", &dir)) return NULL;
	err = self->db_env->set_tmp_dir(self->db_env, dir);
	RETURN_IF_ERR();
	RETURN_NONE();
}

/* txn_begin(parent=None, flags=0) */
/* */
/* This function starts a new explicit transaction.  An explicit */
/* transaction must be passed to each of the database access routines */
/* that need to be involved in the transaction, and therefore cannot */
/* include the dictionary simulation routines.  On the other hand, */
/* there can be more than one explicit transaction active in any one */
/* process at once.  (You should also be able to mix explicit and */
/* automatic transactions.) */
/* */
/* This function returns a Txn object that must be passed along to */
/* any function that needs to be involved in the transaction. */
/* */
/* Notes: */
/*  * transactions may not span threads, i.e., each */
/*    transaction must begin and end in the same thread, and each */
/*    transaction may only be used by a single thread.  */
/*  * cursors may not span transactions, i.e., each cursor */
/*    must be opened and closed within a single transaction.  */
/*  * a parent transaction may not issue any Berkeley DB */
/*    operations, except for txn_begin and txn_abort, while it */
/*    has active child transactions (transactions that have not */
/*    yet been committed or aborted). */
static PyObject *
DBEnv_txn_begin(PyObject *dbenvobj, PyObject *args)
{
	int flags=0;
	DBEnvObject *self = (DBEnvObject *)dbenvobj;
	TxnObject *txnobj = NULL;
	DB_TXN *txn;

	if (!PyArg_ParseTuple(args, "|O!i:txn_begin", 
			      &Txn_Type, &txnobj, &flags)) 
		return NULL;
	if (!txnobj) txn = self->autoTrans;
	else         txn = txnobj->txn;
	return (PyObject*)newTxnObject(self, txn, flags);
}

/* txn_checkpoint(min=0) */
/* */
/* The txn_checkpoint function flushes the underlying memory */
/* pool, writes a checkpoint record to the log and then */
/* flushes the log.  If min is non-zero, a checkpoint is only */
/* done if more than min minutes have passed since the last */
/* previous checkpoint. */
/* The only valid flag is DB_FORCE which forces a checkpoint */
/* record even if there has been no activity since the */
/* previous checkpoint. */

static PyObject *
DBEnv_txn_checkpoint(PyObject *dbenvobj, PyObject *args)
{
	int err, min=0, flags=0;
	DBEnvObject *self = (DBEnvObject *)dbenvobj;
	if (!PyArg_ParseTuple(args, "|ii:txn_checkpoint", &min, &flags)) 
		return NULL;
	err = txn_checkpoint(self->db_env, 0, min, flags);
	RETURN_IF_ERR();
	RETURN_NONE();
}

/* --------------------------------------------------------------------- */
/* Txn methods */

/* An explicit transaction must have its ID explicitly passed to the DB method */
/* calls, and therefore cannot be passed to the dictionary simulation routines. */
/* On the other hand, there can be more than one explicit transaction active in */
/* any one process at once. */
/* (You should also be able to mix explicit and automatic transactions.) */
/* */
/* Txn objects are created using the DbEnv.txn_begin() method. */
/* */

static PyObject *
Txn_commit(PyObject *txnobj, PyObject *args)
{
	TxnObject *self = (TxnObject *)txnobj;
	int flags=0, err;
	if (!PyArg_ParseTuple(args, "|i", &flags)) return NULL;
	err = txn_commit(self->txn, flags);
	RETURN_IF_ERR();
	RETURN_NONE();
}

/* If this transaction is involved in a distributed transaction system, */
/* this function should be called to begin the two-phase commit. */
static PyObject *
Txn_prepare(PyObject *txnobj, PyObject *args)
{
	TxnObject *self = (TxnObject *)txnobj;
	int err = txn_prepare(self->txn);
	RETURN_IF_ERR();
	RETURN_NONE();
}

/* This function causes an abnormal termination of the transaction.  The */
/* log is played backwards and any necessary recovery operations are */
/* initiated. */

static PyObject *
Txn_abort(PyObject *txnobj, PyObject *args)
{
	TxnObject *self = (TxnObject *)txnobj;
	int err;
	err = txn_abort(self->txn);
	RETURN_IF_ERR();
	RETURN_NONE();

}

/* --------------------------------------------------------------------- */
/* Method definition tables and type objects */

static PyMethodDef DB_methods[] = {
	{"close",	(PyCFunction)DB_close,	METH_VARARGS},
	{"cursor",	(PyCFunction)DB_cursor,	METH_VARARGS},
	{"delete",	(PyCFunction)DB_delete,	METH_VARARGS},
	{"fd",	(PyCFunction)DB_fd,	METH_VARARGS},
	{"get",	(PyCFunction)DB_get,	METH_VARARGS},
	{"getRec",	(PyCFunction)DB_getRec,	METH_VARARGS},
	{"has_key",	(PyCFunction)DB_has_key,	METH_VARARGS},
	{"keys",	(PyCFunction)DB_keys,	METH_VARARGS},
	{"open",	(PyCFunction)DB_open,	METH_VARARGS},
	{"put",	(PyCFunction)DB_put,	METH_VARARGS},
	{"set_bt_minkey",	(PyCFunction)DB_set_bt_minkey,	METH_VARARGS},
	{"set_cachesize",	(PyCFunction)DB_set_cachesize,	METH_VARARGS},
	{"set_flags",	(PyCFunction)DB_set_flags,	METH_VARARGS},
	{"set_h_ffactor",	(PyCFunction)DB_set_h_ffactor,	METH_VARARGS},
	{"set_h_nelem",	(PyCFunction)DB_set_h_nelem,	METH_VARARGS},
	{"set_lorder",	(PyCFunction)DB_set_lorder,	METH_VARARGS},
	{"set_pagesize",	(PyCFunction)DB_set_pagesize,	METH_VARARGS},
	{"set_re_delim",	(PyCFunction)DB_set_re_delim,	METH_VARARGS},
	{"set_re_len",	(PyCFunction)DB_set_re_len,	METH_VARARGS},
	{"set_re_pad",	(PyCFunction)DB_set_re_pad,	METH_VARARGS},
	{"set_re_source",	(PyCFunction)DB_set_re_source,	METH_VARARGS},
	{"sync",	(PyCFunction)DB_sync,	METH_VARARGS},
	{"type",	(PyCFunction)DB_type,	METH_VARARGS},
	{"upgrade",	(PyCFunction)DB_upgrade,	METH_VARARGS},
	{NULL,		NULL}		/* sentinel */
};

static PyMappingMethods DB_mapping = {
        (inquiry)DB_length,          /*mp_length*/
        (binaryfunc)DB_subscript,    /*mp_subscript*/
        (objobjargproc)DB_ass_sub,   /*mp_ass_subscript*/
};


static PyMethodDef DBC_methods[] = {
	{"close",	(PyCFunction)DBC_close,	METH_VARARGS},
	{"current",	(PyCFunction)DBC_current,	METH_VARARGS},
	{"delete",	(PyCFunction)DBC_delete,	METH_VARARGS},
	{"first",	(PyCFunction)DBC_first,	METH_VARARGS},
	{"get",	(PyCFunction)DBC_get,	METH_VARARGS},
	{"getRecno",	(PyCFunction)DBC_getRecno,	METH_VARARGS},
	{"last",	(PyCFunction)DBC_last,	METH_VARARGS},
	{"next",	(PyCFunction)DBC_next,	METH_VARARGS},
	{"prev",	(PyCFunction)DBC_prev,	METH_VARARGS},
	{"put",	(PyCFunction)DBC_put,	METH_VARARGS},
	{"set",	(PyCFunction)DBC_set,	METH_VARARGS},
	{"setRange",	(PyCFunction)DBC_setRange,	METH_VARARGS},
	{"getBoth",	(PyCFunction)DBC_getBoth,	METH_VARARGS},
	{"setRecno",	(PyCFunction)DBC_setRecno,	METH_VARARGS},
	{NULL,		NULL}		/* sentinel */
};

static PyMethodDef DBEnv_methods[] = {
	{"abortAutoTrans",	(PyCFunction)DBEnv_abortAutoTrans,	METH_VARARGS},
	{"beginAutoTrans",	(PyCFunction)DBEnv_beginAutoTrans,	METH_VARARGS},
	{"close",	(PyCFunction)DBEnv_close,	METH_VARARGS},
	{"commitAutoTrans",	(PyCFunction)DBEnv_commitAutoTrans,	METH_VARARGS},
	{"open",	(PyCFunction)DBEnv_open,	METH_VARARGS},
	{"prepareAutoTrans",	(PyCFunction)DBEnv_prepareAutoTrans,	METH_VARARGS},
	{"set_cachesize",	(PyCFunction)DBEnv_set_cachesize,	METH_VARARGS},
	{"set_data_dir",	(PyCFunction)DBEnv_set_data_dir,	METH_VARARGS},
	{"set_lg_bsize",	(PyCFunction)DBEnv_set_lg_bsize,	METH_VARARGS},
	{"set_lg_dir",	(PyCFunction)DBEnv_set_lg_dir,	METH_VARARGS},
	{"set_lg_max",	(PyCFunction)DBEnv_set_lg_max,	METH_VARARGS},
	{"set_lk_detect",	(PyCFunction)DBEnv_set_lk_detect,	METH_VARARGS},
	{"set_mp_mmapsize",	(PyCFunction)DBEnv_set_mp_mmapsize,	METH_VARARGS},
	{"set_tmp_dir",	(PyCFunction)DBEnv_set_tmp_dir,	METH_VARARGS},
	{"txn_begin",	(PyCFunction)DBEnv_txn_begin,	METH_VARARGS},
	{"txn_checkpoint",	(PyCFunction)DBEnv_txn_checkpoint,	METH_VARARGS},
	{NULL,		NULL}		/* sentinel */
};

static PyMethodDef Txn_methods[] = {
	{"commit",	(PyCFunction)Txn_commit,	METH_VARARGS},
	{"prepare",	(PyCFunction)Txn_prepare,	METH_VARARGS},
	{"abort",	(PyCFunction)Txn_abort,	METH_VARARGS},
	{NULL,		NULL}		/* sentinel */
};

static PyObject *
DB_getattr(DBObject *self, char *name)
{
	return Py_FindMethod(DB_methods, (PyObject *)self, name);
}

static PyObject *
DBEnv_getattr(DBEnvObject *self, char *name)
{
	return Py_FindMethod(DBEnv_methods, (PyObject *)self, name);
}

static PyObject *
DBC_getattr(DBCObject *self, char *name)
{
	return Py_FindMethod(DBC_methods, (PyObject *)self, name);
}

static PyObject *
Txn_getattr(TxnObject *self, char *name)
{
	return Py_FindMethod(Txn_methods, (PyObject *)self, name);
}

statichere PyTypeObject DB_Type = {
	PyObject_HEAD_INIT(NULL)
	0,			/*ob_size*/
	"DB",			/*tp_name*/
	sizeof(DBObject),	/*tp_basicsize*/
	0,			/*tp_itemsize*/
	/* methods */
	(destructor)DB_dealloc, /*tp_dealloc*/
	0,			/*tp_print*/
	(getattrfunc)DB_getattr, /*tp_getattr*/
	0,                      /*tp_setattr*/
	0,			/*tp_compare*/
	0,			/*tp_repr*/
	0,			/*tp_as_number*/
	0,			/*tp_as_sequence*/
	&DB_mapping,		/*tp_as_mapping*/
	0,			/*tp_hash*/
};

statichere PyTypeObject DBC_Type = {
	PyObject_HEAD_INIT(NULL)
	0,			/*ob_size*/
	"DBC",			/*tp_name*/
	sizeof(DBCObject),	/*tp_basicsize*/
	0,			/*tp_itemsize*/
	/* methods */
	(destructor)DBC_dealloc,/*tp_dealloc*/
	0,			/*tp_print*/
	(getattrfunc)DBC_getattr, /*tp_getattr*/
	0,                      /*tp_setattr*/
	0,			/*tp_compare*/
	0,			/*tp_repr*/
	0,			/*tp_as_number*/
	0,			/*tp_as_sequence*/
	0,			/*tp_as_mapping*/
	0,			/*tp_hash*/
};

statichere PyTypeObject DBEnv_Type = {
	PyObject_HEAD_INIT(NULL)
	0,			/*ob_size*/
	"DBEnv",			/*tp_name*/
	sizeof(DBEnvObject),	/*tp_basicsize*/
	0,			/*tp_itemsize*/
	/* methods */
	(destructor)DBEnv_dealloc, /*tp_dealloc*/
	0,			/*tp_print*/
	(getattrfunc)DBEnv_getattr, /*tp_getattr*/
	0,                      /*tp_setattr*/
	0,			/*tp_compare*/
	0,			/*tp_repr*/
	0,			/*tp_as_number*/
	0,			/*tp_as_sequence*/
	0,			/*tp_as_mapping*/
	0,			/*tp_hash*/
};

statichere PyTypeObject Txn_Type = {
	PyObject_HEAD_INIT(NULL)
	0,			/*ob_size*/
	"Txn",			/*tp_name*/
	sizeof(TxnObject),	/*tp_basicsize*/
	0,			/*tp_itemsize*/
	/* methods */
	(destructor)Txn_dealloc, /*tp_dealloc*/
	0,			/*tp_print*/
	(getattrfunc)Txn_getattr, /*tp_getattr*/
	0,                      /*tp_setattr*/
	0,			/*tp_compare*/
	0,			/*tp_repr*/
	0,			/*tp_as_number*/
	0,			/*tp_as_sequence*/
	0,			/*tp_as_mapping*/
	0,			/*tp_hash*/
};

/* --------------------------------------------------------------------- */
/* Module-level functions */

static char bsddb_version_doc[] = 
"Returns a tuple of major, minor, and patch release numbers of the\n\
underlying DB library.";

static PyObject *
DB_construct(PyObject *self, PyObject *args)
{
	DBEnvObject *dbenvobj;
	if (!PyArg_ParseTuple(args, "O!:Db", &DBEnv_Type, &dbenvobj)) 
		return NULL;
	return (PyObject *)newDBObject( dbenvobj );
}

static PyObject *
DBEnv_construct(PyObject *self, PyObject *args)
{
	if (!PyArg_ParseTuple(args, ":DbEnv")) return NULL;
	return (PyObject *)newDBEnvObject();
}

static PyObject *
bsddb_version(PyObject *self, PyObject *args)
{
	int major, minor, patch;

        if (!PyArg_ParseTuple(args, ":version"))
		return NULL;
        db_version(&major, &minor, &patch);
        return Py_BuildValue("(iii)", major, minor, patch);
}


/* List of functions defined in the module */

static PyMethodDef bsddb_methods[] = {
	{"Db",	(PyCFunction)DB_construct,	METH_VARARGS},
	{"DbEnv",	(PyCFunction)DBEnv_construct,	METH_VARARGS},
	{"version", bsddb_version, METH_VARARGS, bsddb_version_doc},
	{NULL,		NULL}		/* sentinel */
};

/* --------------------------------------------------------------------- */
/* Module initialization */


/* Convenience routine to export an integer value.
 *
 * Errors are silently ignored, for better or for worse...
 */
static void
insint(PyObject *d, char *name, int value)
{
	PyObject *v = PyInt_FromLong((long) value);
	if (!v || PyDict_SetItemString(d, name, v))
		PyErr_Clear();

	Py_XDECREF(v);
}

DL_EXPORT(void)
	init_bsddb(void)
{
	PyObject *m, *d;

	/* Initialize the type of the new type object here; doing it here
	 * is required for portability to Windows without requiring C++. */
	DB_Type.ob_type = &PyType_Type;
	DBC_Type.ob_type = &PyType_Type;
	DBEnv_Type.ob_type = &PyType_Type;
	Txn_Type.ob_type = &PyType_Type;

	/* Create the module and add the functions */
	m = Py_InitModule("_bsddb", bsddb_methods);

	/* Add some symbolic constants to the module */
	d = PyModule_GetDict(m);
	dbError = PyErr_NewException("_bsddb.error", NULL, NULL);
	PyDict_SetItemString(d, "error", dbError);

	PyDict_SetItemString(d, "__version__", 
			     PyString_FromString(PY_BSDDB_VERSION));
	PyDict_SetItemString(d, "cvsid", PyString_FromString(rcs_id));
	PyDict_SetItemString(d, "DB_VERSION_STRING", 
			     PyString_FromString( DB_VERSION_STRING ));

        insint(d, "DB_VERSION_MAJOR", DB_VERSION_MAJOR);
        insint(d, "DB_VERSION_MINOR", DB_VERSION_MINOR);
        insint(d, "DB_VERSION_PATCH", DB_VERSION_PATCH);

        insint(d, "DB_MAX_PAGES", DB_MAX_PAGES);
        insint(d, "DB_MAX_RECORDS", DB_MAX_RECORDS);

        insint(d, "DB_DBT_PARTIAL", DB_DBT_PARTIAL);

        insint(d, "DB_XA_CREATE", DB_XA_CREATE);

        insint(d, "DB_CREATE", DB_CREATE);
        insint(d, "DB_NOMMAP", DB_NOMMAP);
        insint(d, "DB_THREAD", DB_THREAD);

        insint(d, "DB_INIT_CDB", DB_INIT_CDB);
        insint(d, "DB_INIT_LOCK", DB_INIT_LOCK);
        insint(d, "DB_INIT_LOG", DB_INIT_LOG);
        insint(d, "DB_INIT_MPOOL", DB_INIT_MPOOL);
        insint(d, "DB_INIT_TXN", DB_INIT_TXN);
        insint(d, "DB_RECOVER", DB_RECOVER);
        insint(d, "DB_RECOVER_FATAL", DB_RECOVER_FATAL);
        insint(d, "DB_TXN_NOSYNC", DB_TXN_NOSYNC);
        insint(d, "DB_USE_ENVIRON", DB_USE_ENVIRON);
        insint(d, "DB_USE_ENVIRON_ROOT", DB_USE_ENVIRON_ROOT);

        insint(d, "DB_LOCKDOWN", DB_LOCKDOWN);
        insint(d, "DB_PRIVATE", DB_PRIVATE);

        insint(d, "DB_TXN_SYNC", DB_TXN_SYNC);
        insint(d, "DB_TXN_NOWAIT", DB_TXN_NOWAIT);
        insint(d, "DB_FORCE", DB_FORCE);

        insint(d, "DB_EXCL", DB_EXCL);
        insint(d, "DB_RDONLY", DB_RDONLY);
        insint(d, "DB_TRUNCATE", DB_TRUNCATE);

        insint(d, "DB_LOCK_NORUN", DB_LOCK_NORUN);
        insint(d, "DB_LOCK_DEFAULT", DB_LOCK_DEFAULT);
        insint(d, "DB_LOCK_OLDEST", DB_LOCK_OLDEST);
        insint(d, "DB_LOCK_RANDOM", DB_LOCK_RANDOM);
        insint(d, "DB_LOCK_YOUNGEST", DB_LOCK_YOUNGEST);

        insint(d, "DB_BTREE", DB_BTREE);
        insint(d, "DB_HASH", DB_HASH);
        insint(d, "DB_RECNO", DB_RECNO);
        insint(d, "DB_QUEUE", DB_QUEUE);
        insint(d, "DB_UNKNOWN", DB_UNKNOWN);

        insint(d, "DB_DUP", DB_DUP);
        insint(d, "DB_DUPSORT", DB_DUPSORT);
        insint(d, "DB_RECNUM", DB_RECNUM);
        insint(d, "DB_RENUMBER", DB_RENUMBER);
        insint(d, "DB_REVSPLITOFF", DB_REVSPLITOFF);
        insint(d, "DB_SNAPSHOT", DB_SNAPSHOT);

        insint(d, "DB_AFTER", DB_AFTER);
        insint(d, "DB_APPEND", DB_APPEND);
        insint(d, "DB_BEFORE", DB_BEFORE);
        insint(d, "DB_CHECKPOINT", DB_CHECKPOINT);
        insint(d, "DB_CONSUME", DB_CONSUME);
        insint(d, "DB_CURLSN", DB_CURLSN);
        insint(d, "DB_CURRENT", DB_CURRENT);
        insint(d, "DB_FIRST", DB_FIRST);
        insint(d, "DB_FLUSH", DB_FLUSH);
        insint(d, "DB_GET_BOTH", DB_GET_BOTH);
        insint(d, "DB_GET_RECNO", DB_GET_RECNO);
        insint(d, "DB_JOIN_ITEM", DB_JOIN_ITEM);
        insint(d, "DB_KEYFIRST", DB_KEYFIRST);
        insint(d, "DB_KEYLAST", DB_KEYLAST);
        insint(d, "DB_LAST", DB_LAST);
        insint(d, "DB_NEXT", DB_NEXT);
        insint(d, "DB_NEXT_DUP", DB_NEXT_DUP);
        insint(d, "DB_NEXT_NODUP", DB_NEXT_NODUP);
        insint(d, "DB_NOOVERWRITE", DB_NOOVERWRITE);
        insint(d, "DB_NOSYNC", DB_NOSYNC);
        insint(d, "DB_POSITION", DB_POSITION);
        insint(d, "DB_PREV", DB_PREV);
        insint(d, "DB_RECORDCOUNT", DB_RECORDCOUNT);
        insint(d, "DB_SET", DB_SET);
        insint(d, "DB_SET_RANGE", DB_SET_RANGE);
        insint(d, "DB_SET_RECNO", DB_SET_RECNO);
        insint(d, "DB_WRITECURSOR", DB_WRITECURSOR);

        insint(d, "DB_OPFLAGS_MASK", DB_OPFLAGS_MASK);
        insint(d, "DB_RMW", DB_RMW);

        insint(d, "DB_INCOMPLETE", DB_INCOMPLETE);
        insint(d, "DB_KEYEMPTY", DB_KEYEMPTY);
        insint(d, "DB_KEYEXIST", DB_KEYEXIST);
        insint(d, "DB_LOCK_DEADLOCK", DB_LOCK_DEADLOCK);
        insint(d, "DB_LOCK_NOTGRANTED", DB_LOCK_NOTGRANTED);
        insint(d, "DB_NOTFOUND", DB_NOTFOUND);
        insint(d, "DB_OLD_VERSION", DB_OLD_VERSION);
        insint(d, "DB_RUNRECOVERY", DB_RUNRECOVERY);

	/* Check for errors */
	if (PyErr_Occurred())
		Py_FatalError("can't initialize module _bsddb");
}
