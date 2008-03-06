# This file was created automatically by SWIG.
import dbc
class DB_INFOPtr :
    def __init__(self,this):
        self.this = this
        self.thisown = 0
    def __setattr__(self,name,value):
        if name == "db_lorder" :
            dbc.DB_INFO_db_lorder_set(self.this,value)
            return
        if name == "db_cachesize" :
            dbc.DB_INFO_db_cachesize_set(self.this,value)
            return
        if name == "db_pagesize" :
            dbc.DB_INFO_db_pagesize_set(self.this,value)
            return
        if name == "bt_maxkey" :
            dbc.DB_INFO_bt_maxkey_set(self.this,value)
            return
        if name == "bt_minkey" :
            dbc.DB_INFO_bt_minkey_set(self.this,value)
            return
        if name == "h_ffactor" :
            dbc.DB_INFO_h_ffactor_set(self.this,value)
            return
        if name == "h_nelem" :
            dbc.DB_INFO_h_nelem_set(self.this,value)
            return
        if name == "re_pad" :
            dbc.DB_INFO_re_pad_set(self.this,value)
            return
        if name == "re_delim" :
            dbc.DB_INFO_re_delim_set(self.this,value)
            return
        if name == "re_len" :
            dbc.DB_INFO_re_len_set(self.this,value)
            return
        if name == "re_source" :
            dbc.DB_INFO_re_source_set(self.this,value)
            return
        if name == "flags" :
            dbc.DB_INFO_flags_set(self.this,value)
            return
        self.__dict__[name] = value
    def __getattr__(self,name):
        if name == "db_lorder" : 
            return dbc.DB_INFO_db_lorder_get(self.this)
        if name == "db_cachesize" : 
            return dbc.DB_INFO_db_cachesize_get(self.this)
        if name == "db_pagesize" : 
            return dbc.DB_INFO_db_pagesize_get(self.this)
        if name == "bt_maxkey" : 
            return dbc.DB_INFO_bt_maxkey_get(self.this)
        if name == "bt_minkey" : 
            return dbc.DB_INFO_bt_minkey_get(self.this)
        if name == "h_ffactor" : 
            return dbc.DB_INFO_h_ffactor_get(self.this)
        if name == "h_nelem" : 
            return dbc.DB_INFO_h_nelem_get(self.this)
        if name == "re_pad" : 
            return dbc.DB_INFO_re_pad_get(self.this)
        if name == "re_delim" : 
            return dbc.DB_INFO_re_delim_get(self.this)
        if name == "re_len" : 
            return dbc.DB_INFO_re_len_get(self.this)
        if name == "re_source" : 
            return dbc.DB_INFO_re_source_get(self.this)
        if name == "flags" : 
            return dbc.DB_INFO_flags_get(self.this)
        raise AttributeError,name
    def __repr__(self):
        return "<C DB_INFO instance>"
class DB_INFO(DB_INFOPtr):
    """  
   class DB_INFO
  
   Objects of this type are used for setting initialization options and flags
   for DB files upon their creation.  Each DB object has a DB_INFO object
   contained within it named "info" for the purpose of setting its options
   before it is opened the first time.  The following options are available,
   (all default to zero):
  
   db_cachesize (integer)
          A suggested maximum size of the memory pool cache, in bytes.  If
          db_cachesize is 0, an appropriate default is used.
  
          Note, the minimum number of pages in the cache should be no less
          than 10, and the access methods will fail if an insufficiently
          large cache is specified.  In addition, for applications that
          exhibit strong locality in their data access patterns,
          increasing the size of the cache can significantly improve
          application performance.
  
   db_lorder (integer)
          The byte order for integers in the stored database metadata.  The
          number should represent the order as an integer, for example, big
          endian order is the number 4321, and little endian order is the
          number 1234.  If db_lorder is 0, the host order of the machine where
          the DB library was compiled is used.
  
          The value of db_lorder is ignored except when databases are being
          created.  If a database already exists, the byte order it uses is
          determined when the file is read.
  
          The access methods provide no guarantees about the byte ordering of
          the application data stored in the database, and applications are
          responsible for maintaining any necessary ordering.
  
   db_pagesize (integer)
          The size of the pages used to hold items in the database, in bytes.
          The minimum page size is 512 bytes and the maximum page size is 64K
          bytes.  If db_pagesize is 0, a page size is selected based on the
          underlying filesystem I/O block size.  The selected size has a lower
          limit of 512 bytes and an upper limit of 16K bytes.
  
   bt_minkey (integer) BTREE only
          The minimum number of keys that will be stored on any single
          page. This value is used to determine which keys will be stored
          on overflow pages, i.e. if a key or data item is larger than the
          pagesize divided by the bt_minkey value, it will be stored on
          overflow pages instead of in the page itself.  The bt_minkey
          value specified must be at least 2; if bt_minkey is 0, a value of
          2 is used.
  
   bt_maxkey (integer) BTREE only
          The maximum number of keys that will be stored on any single page.
  
  
   h_ffactor (integer) HASH only
          The desired density within the hash table.  It is an
          approximation of the number of keys allowed to accumulate in
          any one bucket, determining when the hash table grows or shrinks.
          The default value is 0, indicating that the fill factor will be
          selected dynamically as pages are filled.
  
   h_nelem (integer) HASH only
          An estimate of the final size of the hash table.  If not set or
          set too low, hash tables will expand gracefully as keys are
          entered, although a slight performance degradation may be
          noticed.  The default value is 1.
  
  
   re_delim (integer) RECNO only
          For variable length records, if the re_source file is specified
          and the DB_DELIMITER flag is set, the delimiting byte used to
          mark the end of a record in the source file.  If the re_source
          file is specified and the DB_DELIMITER flag is not set, <newline>
          characters (i.e. "\\n", 0x0a) are interpreted as
          end-of-record markers.
  
   re_len (integer) RECNO only
          The length of a fixed-length record.
  
   re_pad (integer) RECNO only
          For fixed length records, if the DB_PAD flag is set, the pad
          character for short records.  If the DB_PAD flag is not set,
          <space> characters (i.e., 0x20) are used for padding.
  
   re_source (string) RECNO only
          The purpose of the re_source field is to provide fast access and
          modification to databases that are normally stored as flat text
          files.
  
          If the re_source field is non-NULL, it specifies an underlying
          flat text database file that is read to initialize a transient
          record number index.  In the case of variable length records, the
          records are separated by the byte value re_delim.  For example,
          standard UNIX byte stream files can be interpreted as a sequence
          of variable length records separated by <newline> characters.
  
          In addition, when cached data would normally be written back to
          the underlying database file (e.g., the close or sync functions
          are called), the in-memory copy of the database will be written
          back to the re_source file.
  
          By default, the backing source file is read lazily, i.e., records
          are not read from the file until they are requested by the
          application.  If multiple processes (not threads) are accessing a
          recno database concurrently and either inserting or deleting
          records, the backing source file must be read in its entirety
          before more than a single process accesses the database, and only
          that process should specify the backing source file as part of
          the db_open call. See the DB_SNAPSHOT flag below for more
          information.
  
          Reading and writing the backing source file specified by
          re_source cannot be transactionally protected because it involves
          filesystem operations that are not part of the DB transaction
          methodology.  For this reason, if a temporary database is used to
          hold the records, i.e., a NULL was specified as the file argument
          to db_open, it is possible to lose the contents of the re_source
          file, e.g., if the system crashes at the right instant. If a file
          is used to hold the database, i.e., a file name was specified as
          the file argument to db_open, normal database recovery on that
          file can be used to prevent information loss, although it is
          still possible that the contents of re_source will be lost if the
          system crashes.
  
          The re_source file must already exist (but may be zero-length)
          when db_open is called.
  
          For all of the above reasons, the re_source field is generally
          used to specify databases that are read-only for DB
          applications, and that are either generated on the fly by
          software tools, or modified using a different mechanism, e.g., a
          text editor.
  
  
   flags (integer)
          May be set to a combination of the following flags or'ed together,
          as appropriate for the access method (BTREE, HASH or RECNO).
  
          DB_DUP (BTREE or HASH)
              Permit duplicate keys in the tree, i.e. insertion when the
              key of the key/data pair being inserted already exists in the
              tree will be successful.  The ordering of duplicates in the
              tree is determined by the order of insertion, unless the
              ordering is otherwise specified by use of a cursor.  It is an
              error to specify both DB_DUP and DB_RECNUM.
  
          DB_RECNUM (BTREE)
              Support retrieval from btrees using record numbers.  For
              more information, see the DB.getRec and DBC.getRec methods.
  
              Logical record numbers in btrees are mutable in the face of
              record insertion or deletion.  See the DB_RENUMBER flag in
              the RECNO section below for further discussion.
  
              Maintaining record counts within a btree introduces a
              serious point of contention, namely the page locations where
              the record counts are stored.  In addition, the entire tree
              must be locked during both insertions and deletions,
              effectively single-threading the tree for those operations.
              Specifying DB_RECNUM can result in serious performance
              degradation for some applications and data sets.
  
              It is an error to specify both DB_DUP and DB_RECNUM.
  
          DB_DELIMITER (RECNO)
              The re_delim field is set.
  
          DB_FIXEDLEN (RECNO)
              The records are fixed-length, not byte delimited.  The
              structure element re_len specifies the length of the record,
              and the structure element re_pad is used as the pad
              character.
  
              Any records added to the database that are less than re_len
              bytes long are automatically padded. Any attempt to insert
              records into the database that are greater than re_len bytes
              long will cause the call to fail immediately and return an
              error.
  
           DB_PAD (RECNO)
              The re_pad field is set.
  
           DB_RENUMBER (RECNO)
              Specifying the DB_RENUMBER flag causes the logical record
              numbers to be mutable, and change as records are added to
              and deleted from the database.  For example, the deletion of
              record number 4 causes records numbered 5 and greater to be
              renumbered downward by 1.  If a cursor was positioned to
              record number 4 before the deletion, it will reference the
              new record number 4, if any such record exists, after the
              deletion. If a cursor was positioned after record number 4
              before the deletion, it will be shifted downward 1 logical
              record, continuing to reference the same record as it did
              before.
  
              Using the put methods to create new records will cause the
              creation of multiple records if the record number is more than
              one greater than the largest record currently in the database.
              For example, creating record 28, when record 25 was previously
              the last record in the database, will create records 26 and 27 as
              well as 28.  Attempts to retrieve records that were created in
              this manner will result in an error return of DB_KEYEMPTY.
  
              If a created record is not at the end of the database, all
              records following the new record will be automatically
              renumbered upward by 1. For example, the creation of a new
              record numbered 8 causes records numbered 8 and greater to
              be renumbered upward by 1.  If a cursor was positioned to
              record number 8 or greater before the insertion, it will be
              shifted upward 1 logical record, continuing to reference the
              same record as it did before.
  
              For these reasons, concurrent access to a recno database
              with the DB_RENUMBER flag specified may be largely
              meaningless, although it is supported.
  
           DB_SNAPSHOT (RECNO)
              This flag specifies that any specified re_source file be read
              in its entirety when db_open is called.  If this flag is not
              specified, the re_source file may be read lazily.
  
"""
    def __init__(self,this):
        self.this = this




class DBCPtr :
    def __init__(self,this):
        self.this = this
        self.thisown = 0
    def __del__(self):
        if self.thisown == 1 :
            dbc.delete_DBC(self.this)
    def close(self):
        """  
   DBC.close()
  
   The cursor is discarded.  No further references to this cursor
   should be made.
  
"""
        val = dbc.DBC_close(self.this)
        return val
    def delete(self,*args):
        """  
   DBC.delete()
  
   The key/data pair currently referenced by the cursor is removed
   from the database.
  
   The cursor position is unchanged after a delete and subsequent
   calls to cursor functions expecting the cursor to reference an
   existing key will fail.
  
"""
        val = apply(dbc.DBC_delete,(self.this,)+args)
        return val
    def get(self,arg0):
        """  
   DBC.get(flags)
  
   This function returns a tuple containing a key and data value from
   the database.
  
   Modifications to the database during a sequential scan will be
   reflected in the scan, i.e. records inserted behind a cursor will
   not be returned while records inserted in front of a cursor will
   be returned.
  
   If multiple threads or processes insert items into the same
   database file without using locking, the results are undefined.
  
   The parameter flags must be set to exactly one of the following
   values:
  
      DB_FIRST
          The cursor is set to reference the first key/data pair of the
          database, and that pair is returned.  In the presence of
          duplicate key values, the first data item in the set of
          duplicates is returned.  If the database is empty, this
          function will raise db.error with a value of DB_NOTFOUND.
  
      DB_LAST
          The cursor is set to reference the last key/data pair of the
          database, and that pair is returned. In the presence of
          duplicate key values, the last data item in the set of
          duplicates is returned.  If the database is empty, this
          method will raise db.error with a value of DB_NOTFOUND.
  
      DB_NEXT
          If the cursor is not yet initialized, DB_NEXT is identical to
          DB_FIRST.  Otherwise, move the cursor to the next key/data
          pair of the database, and that pair is returned. In the
          presence of duplicate key values, the key may not change.  If
          the cursor is already on the last record in the database,
          this method will raise db.error with a value of DB_NOTFOUND.
  
      DB_PREV
          If the cursor is not yet initialized, DB_PREV is identical to
          DB_LAST. Otherwise, move the cursor to the previous key/data
          pair of the database, and that pair is returned.  In the
          presence of duplicate key values, the key may not change.  If
          the cursor is already on the first record in the database,
          this method will raise db.error with a value of DB_NOTFOUND.
  
      DB_CURRENT
          Return the key/data pair currently referenced by the cursor.
          If the cursor key/data pair has been deleted, this method
          will return DB_KEYEMPTY.  If the cursor is not yet
          initialized, the get method will raise db.error with a value
          of EINVAL.
  
"""
        val = dbc.DBC_get(self.this,arg0)
        return val
    def first(self):
        """  
   DBC.first()
  
   A convenience method.  Equivalent to calling get with DB_FIRST.
  
"""
        val = dbc.DBC_first(self.this)
        return val
    def last(self):
        """  
   DBC.last()
  
   A convenience method.  Equivalent to calling get with DB_LAST.
  
"""
        val = dbc.DBC_last(self.this)
        return val
    def next(self):
        """  
   DBC.next()
  
   A convenience method.  Equivalent to calling get with DB_NEXT.
  
"""
        val = dbc.DBC_next(self.this)
        return val
    def prev(self):
        """  
   DBC.prev()
  
   A convenience method.  Equivalent to calling get with DB_PREV.
  
"""
        val = dbc.DBC_prev(self.this)
        return val
    def current(self):
        """  
   DBC.current()
  
   A convenience method.  Equivalent to calling get with DB_CURRENT.
  
"""
        val = dbc.DBC_current(self.this)
        return val
    def set(self,arg0):
        """  
   DBC.set(key)
  
   Move the cursor to the specified key of the database, and return
   the given key/data pair. In the presence of duplicate key values,
   the method will return the first key/data pair for the given key.
  
   If the database is a recno database and the requested key exists,
   but was never explicitly created by the application or was later
   deleted, the set method raises db.error with a value of
   DB_KEYEMPTY.
  
   If no matching keys are found, this method will raise db.error
   with a value of DB_NOTFOUND.
  
"""
        val = dbc.DBC_set(self.this,arg0)
        return val
    def setRange(self,arg0):
        """  
   DBC.setRange(key)
  
   Identical to the set method, except in the case of the btree access
   method, the returned key/data pair is the smallest key greater than
   or equal to the speci- fied key, permitting partial key matches and
   range searches.
  
"""
        val = dbc.DBC_setRange(self.this,arg0)
        return val
    def setRecno(self,arg0):
        """  
   DBC.setRecno(record_number)
  
   Move the cursor to the specific numbered record of the database, and
   return the associated key/data pair.  For this method to be used, the
   underlying database must be of type btree and it must have been
   created with the DB_RECNUM flag.
  
"""
        val = dbc.DBC_setRecno(self.this,arg0)
        return val
    def getRecno(self):
        """  
   DBC.getRecno()
  
   Return the record number associated with the cursor.  For this
   method to be used, the underlying database must be of type btree
   and it must have been created with the DB_RECNUM flag.
  
"""
        val = dbc.DBC_getRecno(self.this)
        return val
    def put(self,arg0,arg1,arg2):
        """  
   DBC.put(key, data, flags)
  
   This method stores key/data pairs into the database.  The flags
   parameter must be set to exactly one of the following values:
  
      DB_AFTER
              In the case of the btree and hash access methods, insert the
              data element as a duplicate element of the key referenced by
              the cursor.  The new element appears immediately after the
              current cursor position.  It is an error to specify DB_AFTER
              if the underlying btree or hash database was not created
              with the DB_DUP flag. The key parameter is ignored.
  
              In the case of the recno access method, it is an error to
              specify DB_AFTER if the underlying recno database was not
              created with the DB_RENUMBER flag.  If the DB_RENUMBER flag
              was specified, a new key is created, all records after the
              inserted item are automatically renumbered.  The initial
              value of the key parameter is ignored.
  
      DB_BEFORE
              Identical to DB_AFTER except the new element appears
              immediately before the current cursor position.
  
      DB_CURRENT
              Overwrite the data of the key/data pair referenced by the
              cursor with the specified data item.  The key parameter is
              ignored.
  
      DB_KEYFIRST
              In the case of the btree and hash access methods, insert the
              specified key/data pair into the database.  If the key
              already exists in the database, the inserted data item is
              added as the first of the data items for that key.
  
              The DB_KEYFIRST flag may not be specified to the recno access
              method.
  
      DB_KEYLAST
              Insert the specified key/data pair into the database.  If
              the key already exists in the database, the inserted data
              item is added as the last of the data items for that key.
  
              The DB_KEYLAST flag may not be specified to the recno access
              method.
  
   If the cursor record has been deleted, the put method raises
   db.error with value of DB_KEYEMPTY.
  
   If the put method fails for any reason, the state of the cursor
   will be unchanged.  If put succeeds and an item is inserted
   into the database, the cursor is always positioned to reference
   the newly inserted item.
  
"""
        val = dbc.DBC_put(self.this,arg0,arg1,arg2)
        return val
    def __repr__(self):
        return "<C DBC instance>"
class DBC(DBCPtr):
    """  
   class DBC
  
    The DBC (DataBase Cursor) class supports sequential access to the records
    stored in a given databse file.  Cursors are created by calling the cursor
    method of an instance of the DB class.
  
    Each cursor maintains positioning information within a set of key/data pairs.
    In the presence of transactions, cursors are only valid within the context of
    a single transaction, the one specified during the cursor method of the DB
    class. All cursor operations will be executed in the context of that
    transaction.  Before aborting or committing a transaction, all cursors used
    within that transaction must be closed.  In the presence of transactions, the
    application must call abortTrans() (or abortAutoTrans() as appropriate) if
    any of the cursor operations raises an exception, indicating that a deadlock
    (EAGAIN) or system failure occurred.
  
    When locking is enabled, page locks are retained between consecutive cursor
    calls.  For this reason, in the presence of locking, applications should
    discard cursors as soon as they are done with them.  Calling the DB.close
    method discards any cursors opened from that DB.
  
"""
    def __init__(self,this):
        self.this = this




class DBPtr :
    def __init__(self,this):
        self.this = this
        self.thisown = 0
    def __del__(self):
        if self.thisown == 1 :
            dbc.delete_DB(self.this)
    def open(self,arg0,*args):
        """  
   DB.open(filename, type, flags=0, mode=0660)
  
   This method opens the database represented by file for both reading
   and writing by default.  Note, while most of the access methods use
   file as the name of an underlying file on disk, this is not
   guaranteed.  Also, calling open is a reasonably expensive operation.
   (This is based on a model where the DBMS keeps a set of files open
   (for a long time rather than opening and closing them on each query.)
  
   The type argument must be set to one of DB_BTREE, DB_HASH, DB_RECNO
   or DB_UNKNOWN.  If type is DB_UNKNOWN, the database must already
   exist and open will then determine if it is of type DB_BTREE,
   DB_HASH or DB_RECNO.
  
   The flags and mode arguments specify how files will be
   opened and/or created when they don't already exist.  The
   flags value is specified by or'ing together one or more of
   the following values:
  
      DB_CREATE
          Create any underlying files, as necessary.  If the
          files do not already exist and the DB_CREATE flag is
          not specified, the call will fail.
  
      DB_NOMMAP
          Do not memory-map this file.
  
      DB_RDONLY
          Open the database for reading only.  Any attempt to write the
          database using the access methods will fail regardless of the
          actual permissions of any underlying files.
  
      DB_THREAD
          Cause the DB handle returned by the open function to be useable
          by multiple threads within a single address space, i.e., to be
          "free-threaded".
  
      DB_TRUNCATE
          "Truncate" the database if it exists, i.e., behave as if the
          database were just created, discarding any previous contents.
  
   All files created by the access methods are created with mode mode (as
   described in chmod) and modified by the process' umask value at the
   time of creation.  The group ownership of created files is based on
   the system and directory defaults, and is not further specified by DB.
  
"""
        val = apply(dbc.DB_open,(self.this,arg0,)+args)
        return val
    def type(self):
        """  
   DB.type()
  
   The type of the underlying access method (and file format).  Set to
   one of DB_BTREE, DB_HASH or DB_RECNO.  This field may be used to
   determine the type of the database after a return from open with
   the type argument set to DB_UNKNOWN.
  
"""
        val = dbc.DB_type(self.this)
        return val
    def close(self,*args):
        """  
   DB.close(flags=0)
  
   A pointer to a function to flush any cached information to disk,
   close any open cursors, free any allocated resources, and close
   any underlying files.  Since key/data pairs are cached in memory,
   failing to sync the file with the close or sync method may result
   in inconsistent or lost information.  (When the DB object's
   reference count reaches zero, the close method is called, but you
   should probably always call the close method just in case...)
  
   The flags parameter must be set to DB_NOSYNC, which specifies to
   not flush cached information to disk.  The DB_NOSYNC flag is a
   dangerous option.  It should only be set if the application is
   doing logging (with or without transactions) so that the database
   is recoverable after a system or application crash, or if the
   database is always generated from scratch after any system or
   application crash.
  
   When multiple threads are using the DB handle concurrently, only
   a single thread may call the DB handle close function.
  
"""
        val = apply(dbc.DB_close,(self.this,)+args)
        return val
    def cursor(self,*args):
        """  
   DB.cursor(txn=None, flags=0)
  
   Creates and returns a DBC object used to provide sequential access
   to a database.
  
   If the file is being accessed under transaction protection, the
   txn parameter is a transaction ID returned from beginTrans,
   otherwise, the autoTrans (if any) is used.  If transaction
   protection is enabled, cursors must be opened and closed within
   the context of a transaction, and the txnid parameter specifies
   the transaction context in which the cursor may be used.
  
   The  flags value is specified by or'ing together one or more of
   the following values:
  
        DB_RMW
          Specify that the cursor will be used to update the
          database. This flag should only be set when the DB_INIT_CDB
          flag was specified to db_appinit.
  
"""
        val = apply(dbc.DB_cursor,(self.this,)+args)
        val = DBCPtr(val)
        val.thisown = 1
        return val
    def delete(self,arg0,*args):
        """  
   DB.delete(key, txn=None)
  
   The key/data pair associated with the specified key is discarded
   from the database.  In the presence of duplicate key values, all
   records associated with the designated key will be discarded.
  
   If the file is being accessed under transaction protection, the
   txn parameter is a transaction ID returned from beginTrans,
   otherwise, the autoTrans (if any) is used.
  
   The delete method raises db.error with a value of DB_NOTFOUND if
   the specified key did not exist in the file.
  
"""
        val = apply(dbc.DB_delete,(self.this,arg0,)+args)
        return val
    def get(self,arg0,*args):
        """  
   DB.get(key, txn=None)
  
   This method performs keyed retrievel from the database.  The data
   value coresponding to the given key is returned.
  
   In the presence of duplicate key values, get will return the
   first data item for the designated key. Duplicates are sorted by
   insert order except where this order has been overwritten by
   cursor operations. Retrieval of duplicates requires the use of
   cursor operations.
  
   If the file is being accessed under transaction protection, the
   txn parameter is a transaction ID returned from beginTrans,
   otherwise, the autoTrans (if any) is used.
  
   If the database is a recno database and the requested key exists,
   but was never explicitly created by the application or was later
   deleted, the get method raises db.error with a value of
   DB_KEYEMPTY.  Otherwise, if the requested key isn't in the
   database, the get function method raises db.error with a value of
   DB_NOTFOUND.
  
"""
        val = apply(dbc.DB_get,(self.this,arg0,)+args)
        return val
    def getRec(self,arg0,*args):
        """  
   DB.getRec(recno, txn=None)
  
   Retrieve a specific numbered record from a database.  Both the
   key and data item will be returned as a tuple.  In order to use
   this method, the underlying database must be of type btree, and it
   must have been created with the DB_RECNUM flag.
  
   If the file is being accessed under transaction protection, the
   txn parameter is a transaction ID returned from beginTrans,
   otherwise, the autoTrans (if any) is used.
  
"""
        val = apply(dbc.DB_getRec,(self.this,arg0,)+args)
        return val
    def fd(self):
        """  
   DB.fd()
  
   Returns a file descriptor representative of the underlying
   database.  A file descriptor referencing the same file will be
   returned to all processes that call db_open with the same file
   argument. This file descriptor may be safely used as an argument
   to the fcntl and flock locking functions. The file descriptor is
   not necessarily associated with any of the underlying files used
   by the access method.
  
   The fd function only supports a coarse-grained form of locking.
   Applications should use the lock manager where possible.
  
"""
        val = dbc.DB_fd(self.this)
        return val
    def put(self,arg0,arg1,*args):
        """  
   DB.put(key, data, flags=0, txn=None)
  
   A method to store key/data pairs in the database.  If the
   database supports duplicates, the put method adds the new data
   value at the end of the duplicate set.
  
   If the file is being accessed under transaction protection, the
   txn parameter is a transaction ID returned from beginTrans,
   otherwise, the autoTrans (if any) is used.
  
   The flags value is specified by or'ing together one or more of
   the following values:
  
   DB_APPEND
        Append the key/data pair to the end of the database.  For
        DB_APPEND to be specified, the underlying database must be
        of type recno.  The record number allocated to the record is
        returned.
  
   DB_NOOVERWRITE
        Enter the new key/data pair only if the key does not already
        appear in the database.
  
   The default behavior of the put method is to enter the new
   key/data pair, replacing any previously existing key if
   duplicates are disallowed, or to add a duplicate entry if
   duplicates are allowed.  Even if the designated database allows
   duplicates, a call to put with the DB_NOOVERWRITE flag set will
   fail if the key already exists in the database.
  
   This method raises db.error with a value of DB_KEYEXIST if the
   DB_NOOVERWRITE flag was set and the key already exists in the
   file.
  
"""
        val = apply(dbc.DB_put,(self.this,arg0,arg1,)+args)
        return val
    def sync(self):
        """  
   DB.sync()
  
   This method flushes any cached information to disk.
  
"""
        val = dbc.DB_sync(self.this)
        return val
    def __len__(self):
        """"""
        val = dbc.DB___len__(self.this)
        return val
    def __getitem__(self,arg0):
        """"""
        val = dbc.DB___getitem__(self.this,arg0)
        return val
    def __setitem__(self,arg0,arg1):
        """"""
        val = dbc.DB___setitem__(self.this,arg0,arg1)
        return val
    def __delitem__(self,arg0):
        """"""
        val = dbc.DB___delitem__(self.this,arg0)
        return val
    def keys(self):
        """"""
        val = dbc.DB_keys(self.this)
        return val
    def has_key(self,arg0):
        """"""
        val = dbc.DB_has_key(self.this,arg0)
        return val
    def __setattr__(self,name,value):
        if name == "info" :
            dbc.DB_info_set(self.this,value.this)
            return
        self.__dict__[name] = value
    def __getattr__(self,name):
        if name == "info" : 
            return DB_INFOPtr(dbc.DB_info_get(self.this))
        raise AttributeError,name
    def __repr__(self):
        return "<C DB instance>"
class DB(DBPtr):
    """  
   class DB
  
   This class encapsulates the DB database file access methods, and also
   has an embedded DB_INFO object named "info" used for setting configuration
   parameters and flags prior to creation of the database.  See the docstring
   for the DB_INFO object for details.
  
   The DB object must be opened before any other methods can be called.  The
   only thing that can be done before opening is setting options and flags
   in the info object.  For example:
  
        import db
        data = db.DB()
        data.info.db_pagesize = 4096
        data.open("datafile", db.DB_BTREE, db.DB_CREATE)
  
   The DB class supports a dictionary-like interface, including the len, keys,
   has_attr methods, as well as the item reference, item assigment and item
   deletion.  Dictionary access methods can be involved in transactions by
   using the autoTrans functions.
  
   Various types of database files can be created, based on a flag to the
   open method.  The types are:
  
    DB_BTREE
         The btree data structure is a sorted, balanced tree structure storing
         associated key/data pairs.  Searches, inserions, and deletions in the
         btree will all complete in O(lg base N) where base is the average
         number of keys per page.  Often, inserting ordered data into btrees
         results in pages that are half-full.  This implementation has been
         modified to make ordered (or inverse ordered) insertion the best case,
         resulting in nearly perfect page space utilization.
  
         Space freed by deleting key/data pairs from the database is never
         reclaimed from the filesystem, although it is reused where possible.
         This means that the btree storage structure is grow-only.  If
         sufficiently many keys are deleted from a tree that shrinking the
         underlying database file is desirable, this can be accomplished by
         creating a new tree from a scan of the existing one.
  
    DB_HASH
         The hash data structure is an extensible, dynamic hashing scheme,
         able to store variable length key/data pairs.
  
    DB_RECNO
         The recno access method provides support for fixed and variable length
         records, optionally backed by a flat text (byte stream) file.  Both
         fixed and variable length records are accessed by their logical record
         number.
  
         It is valid to create a record whose record number is more than one
         greater than the last record currently in the database.  For example,
         the creation of record number 8, when records 6 and 7 do not yet
         exist, is not an error. However, any attempt to retrieve such records
         (e.g., records 6 and 7) will raise db.error with a value of
         DB_KEYEMPTY.
  
         Deleting a record will not, by default, renumber records following the
         deleted record (see DB_RENUMBER in the DB_INFO class for more
         information).  Any attempt to retrieve deleted records will raise
         db.error with a value of DB_KEYEMPTY.
  
"""
    def __init__(self) :
        """"""
        self.this = dbc.new_DB()
        self.thisown = 1






#-------------- FUNCTION WRAPPERS ------------------

def version():
    """  
   version()
  
   Returns a tuple of major, minor, and patch release numbers of the
   underlying DB library.
  
"""
    val = dbc.version()
    return val

def appinit(arg0,arg1):
    """  
   appinit(db_home, flags)
  
   The appinit function provides a simple way to initialize and configure the
   DB environment.  It is not necessary that it be called, but it provides a
   method of creating a consistent environment for processes using one or more
   of the features of DB.
  
        db_home     The database home directory.  Files named in DB.open are
                    relative to this directory.
  
        flags       0 or any of the following flags, or'ed together:
  
                    DB_CREATE
                      Cause subsystems to create any underlying files, as
                      necessary.
  
                    DB_INIT_CDB
                      Initialize locking for the Berkeley DB Concurrent
                      Access Methods product. In this mode, Berkeley DB
                      provides multiple reader/single writer access. No
                      other locking should be specified (e.g., do not set
                      DB_INIT_LOCK). Access method calls are largely
                      unchanged when using the DB_INIT_CDB flag, although
                      any cursors through which update operations (e.g.,
                      DBcursor.put, DBcursor.delete) will be made, must
                      have the DB_RMW value set in the flags parameter to
                      the cursor call that creates the cursor. See
                      DB.cursor for more information.
  
                    DB_INIT_LOCK
                      Initialize the lock subsystem.  This subsystem should
                      be used when multiple processes or threads are going to
                      be reading or writing a DB database, so that they do
                      not interfere with each other.  When the DB_INIT_LOCK
                      flag is specified, it is usually necessary to run the
                      deadlock detector, db_deadlock, as well.
  
                    DB_INIT_LOG
                      Initialize the log subsystem. This subsystem is used
                      when recovery from application or system failure is
                      important.
  
                    DB_INIT_MPOOL
                      Initialize the mpool subsystem. This subsystem is used
                      whenever the application is using the DB access methods
                      for any purpose.
  
                    DB_INIT_TXN
                      Initialize the transaction subsystem. This subsystem is
                      used when atomicity of multiple operations and recovery
                      are important.  The DB_INIT_TXN flag implies the
                      DB_INIT_LOG flag.
  
                    DB_MPOOL_PRIVATE
                      Create a private memory pool.  Ignored unless
                      DB_INIT_MPOOL is also specified.
  
                    DB_NOMMAP
                      Do not map any files within this environment.  Ignored
                      unless DB_INIT_MPOOL is also specified.
  
                    DB_RECOVER
                      Run normal recovery on this environment before opening it
                      for normal use.  If this flag is set, the DB_CREATE,
                      DB_INIT_TXN, and DB_INIT_LOG flags must also be set since
                      the regions will be removed and recreated.  For further
                      information, consult the man page for db_recover(1).
  
                    DB_RECOVER_FATAL
                      Run catastrophic recovery on this environment before
                      opening it for normal use.  If this flag is set, the
                      DB_CREATE, DB_INIT_TXN, and DB_INIT_LOG flags must also
                      be set since the regions will be removed and recreated.
                      For further information, consult the man page for
                      db_recover(1).
  
                    DB_THREAD
                      Ensure that handles returned by the DB subsystems are
                      useable by multiple threads within a single process,
                      i.e., that the system is "free-threaded".
  
                    DB_TXN_NOSYNC
                      On transaction commit, do not synchronously flush the
                      log.  Ignored unless DB_INIT_TXN is also specified.
  
                    DB_USE_ENVIRON
                      The Berkeley DB process' environment may be
                      permitted to specify information to be used when
                      naming files; see Berkeley DB File Naming. As
                      permitting users to specify which files are used can
                      create security problems, environment information
                      will be used in file naming for all users only if
                      the DB_USE_ENVIRON flag is set.
  
                    DB_USE_ENVIRON_ROOT
                      The Berkeley DB process' environment may be
                      permitted to specify information to be used when
                      naming files; see Berkeley DB File Naming. As
                      permitting users to specify which files are used can
                      create security problems, if the DB_USE_ENVIRON_ROOT
                      flag is set, environment information will be used
                      for file naming only for users with a user-ID
                      matching that of the superuser (specifically, users
                      for whom the getuid(2) system call returns the
                      user-ID 0).
  
"""
    val = dbc.appinit(arg0,arg1)
    return val

def appexit():
    """  
   appexit()
  
   The db_appexit function closes the initialized DB subsystems, freeing
   any allocated resources and closing any underlying subsystems.
  
"""
    val = dbc.appexit()
    return val

def beginAutoTrans():
    """  
   beginAutoTrans()
  
   This function begins an "Automatic Transaction."  An automatic
   transaction automatically involves all DB method calls including the
   dictionary simulation routines, until the transaction is commited or
   aborted.  There can only be one automatic transaction in any process
   at a time, however nested calls can be made to beginAutoTrans and
   commitAutoTrans are supported via reference counting.  abortAutoTrans
   ignores the nesting count and performs the abort.
  
"""
    val = dbc.beginAutoTrans()
    return val

def abortAutoTrans():
    """  
   abortAutoTrans()
  
   Aborts and rolls-back the active automatic transaction.
  
"""
    val = dbc.abortAutoTrans()
    return val

def prepareAutoTrans():
    """  
   prepareAutoTrans()
  
   If the active automatic transaction is involved in a distributed
   transaction system, this function should be called to begin the
   two-phase commit.
  
"""
    val = dbc.prepareAutoTrans()
    return val

def commitAutoTrans():
    """  
   commitAutoTrans()
  
   This function ends the active automatic transaction, commiting the
   changes to the database.
  
"""
    val = dbc.commitAutoTrans()
    return val

def beginTrans():
    """  
   beginTrans()
  
   This function starts a new explicit transaction.  An explicit
   transaction must be explicitly passed to each of the database access
   routines that need to be involved in the transaction, and therefore
   cannot include the dictionary  simulation routines.  On the other hand,
   there can be more than one explicit transaction active in any one
   process at once.  (You should also be able to mix explicit and
   automatic transactions.)
  
   This function returns a DB_TXN object that must be passed along to
   any function that needs to be involved in the transaction, and to the
   abort and commit functions described below.
  
"""
    val = dbc.beginTrans()
    return val

def abortTrans(arg0):
    """  
   abortTrans(DB_TXN)
  
   This function causes an abnormal termination of the transaction.  The
   log is played backwards and any necessary recovery operations are
   initiated.
  
"""
    val = dbc.abortTrans(arg0)
    return val

def prepareTrans(arg0):
    """  
   prepareTrans(DB_TXN)
  
   If this transaction is involved in a distributed transaction system,
   this function should be called to begin the two-phase commit.
  
"""
    val = dbc.prepareTrans(arg0)
    return val

def commitTrans(arg0):
    """  
   commitTrans(DB_TXN)
  
   This function ends the transaction, commiting the changes to the
   database.
  
"""
    val = dbc.commitTrans(arg0)
    return val



#-------------- VARIABLE WRAPPERS ------------------

__version__ = dbc.__version__
DB_MAX_PAGES = dbc.DB_MAX_PAGES
DB_MAX_RECORDS = dbc.DB_MAX_RECORDS
DB_CREATE = dbc.DB_CREATE
DB_NOMMAP = dbc.DB_NOMMAP
DB_THREAD = dbc.DB_THREAD
DB_INIT_CDB = dbc.DB_INIT_CDB
DB_INIT_LOCK = dbc.DB_INIT_LOCK
DB_INIT_LOG = dbc.DB_INIT_LOG
DB_INIT_MPOOL = dbc.DB_INIT_MPOOL
DB_INIT_TXN = dbc.DB_INIT_TXN
DB_MPOOL_PRIVATE = dbc.DB_MPOOL_PRIVATE
DB_RECOVER = dbc.DB_RECOVER
DB_RECOVER_FATAL = dbc.DB_RECOVER_FATAL
DB_TXN_NOSYNC = dbc.DB_TXN_NOSYNC
DB_USE_ENVIRON = dbc.DB_USE_ENVIRON
DB_USE_ENVIRON_ROOT = dbc.DB_USE_ENVIRON_ROOT
DB_EXCL = dbc.DB_EXCL
DB_RDONLY = dbc.DB_RDONLY
DB_SEQUENTIAL = dbc.DB_SEQUENTIAL
DB_TEMPORARY = dbc.DB_TEMPORARY
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
DB_DELIMITER = dbc.DB_DELIMITER
DB_DUP = dbc.DB_DUP
DB_FIXEDLEN = dbc.DB_FIXEDLEN
DB_PAD = dbc.DB_PAD
DB_RECNUM = dbc.DB_RECNUM
DB_RENUMBER = dbc.DB_RENUMBER
DB_SNAPSHOT = dbc.DB_SNAPSHOT
DB_AFTER = dbc.DB_AFTER
DB_APPEND = dbc.DB_APPEND
DB_BEFORE = dbc.DB_BEFORE
DB_CHECKPOINT = dbc.DB_CHECKPOINT
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
DB_NOOVERWRITE = dbc.DB_NOOVERWRITE
DB_NOSYNC = dbc.DB_NOSYNC
DB_PREV = dbc.DB_PREV
DB_RECORDCOUNT = dbc.DB_RECORDCOUNT
DB_SET = dbc.DB_SET
DB_SET_RANGE = dbc.DB_SET_RANGE
DB_SET_RECNO = dbc.DB_SET_RECNO
DB_OPFLAGS_MASK = dbc.DB_OPFLAGS_MASK
DB_RMW = dbc.DB_RMW
DB_INCOMPLETE = dbc.DB_INCOMPLETE
DB_KEYEMPTY = dbc.DB_KEYEMPTY
DB_KEYEXIST = dbc.DB_KEYEXIST
DB_LOCK_DEADLOCK = dbc.DB_LOCK_DEADLOCK
DB_LOCK_NOTGRANTED = dbc.DB_LOCK_NOTGRANTED
DB_LOCK_NOTHELD = dbc.DB_LOCK_NOTHELD
DB_NOTFOUND = dbc.DB_NOTFOUND
DB_RUNRECOVERY = dbc.DB_RUNRECOVERY


#-------------- USER INCLUDE -----------------------

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
    d.info.db_cachesize = cachesize
    d.info.db_pagesize = pgsize
    d.info.db_lorder = lorder
    d.info.flags = hflags
    d.info.h_ffactor = ffactor
    d.info.h_nelem = nelem
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
    d.info.db_cachesize = cachesize
    d.info.db_pagesize = pgsize
    d.info.db_lorder = lorder
    d.info.flags = btflags
    d.info.bt_minkey = minkeypage
    d.info.bt_maxkey = maxkeypage
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
    d.info.db_cachesize = cachesize
    d.info.db_pagesize = pgsize
    d.info.db_lorder = lorder
    d.info.flags = rnflags
    d.info.re_delim = delim
    d.info.re_len = rlen
    d.info.re_source = source
    d.info.re_pad = pad
    d.open(file, DB_RECNO, flags, mode)
    return d

#---------------------------------------------------------------------------

