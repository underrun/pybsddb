#!/usr/bin/python
#
# This provides a simple database table interface built on top of
# the Python BerkeleyDB 3 interface.
#
cvsid = '$Id$'

# standard modules
import string
import sys
try:
    import cPickle
    pickle = cPickle
except ImportError:
    sys.stderr.write("bsddb3.dbtables warning: couldn't import cPickle module\n")
    import pickle
import whrandom
import xdrlib
from threading import *
import re

# custom modules
from bsddb3.db import *

class TableDbError(StandardError) : pass


def PrefixCond(prefix) :
    """Returns a condition function for matching a string prefix"""
    return lambda s, p=prefix: s[:len(p)] == p

def LikeCond(likestr) :
    """Returns a function that will match using an SQL 'LIKE' style
    string.  Case insensitive and % signs are wild cards.
    This isn't perfect but it should work for the simple common cases.
    """
    # escape python re characters
    chars_to_escape = '.*+()[]?'
    for char in chars_to_escape :
        likestr = string.replace(likestr, char, '\\'+char)
    # convert %s to wildcards
    likestr = string.replace(likestr, '%', '.*')
    return re.compile('^'+likestr+'$', re.IGNORECASE).match

#
# keys used to store database metadata
#
_table_names_key = '__TABLE_NAMES__'  # list of the tables in this db
_columns = '._COLUMNS__'  # table_name+this key contains a list of columns
def _columns_key(table) : return table + _columns

#
# these keys are found within table sub databases
#
_data =  '._DATA_.'  # this+column+this+rowid key contains table data
_rowid = '._ROWID_.' # this+rowid+this key contains a unique entry for each
                     # row in the table.  (no data is stored)
_rowid_str_len = 8   # length in bytes of the unique rowid strings
def _data_key(table, col, rowid) : return table + _data + col + _data + rowid
def _search_col_data_key(table, col) : return table + _data + col + _data
def _search_all_data_key(table) : return table + _data
def _rowid_key(table, rowid) : return table + _rowid + rowid + _rowid
def _search_rowid_key(table) : return table + _rowid

def contains_metastrings(s) :
    """Verify that the given string does not contain any
    metadata strings that might interfere with dbtables database operation.
    """
    if string.find(s, _table_names_key) >= 0 or \
       string.find(s, _columns) >= 0 or \
       string.find(s, _data) >= 0 or \
       string.find(s, _rowid) >= 0 :
        return 1
    else :
        return 0


class bsdTableDb :
    def __init__(self, filename, dbhome, create=0, truncate=0, mode=0600) :
        """bsdTableDb.open(filename, dbhome, create=0, truncate=0, mode=0600)
        Open database name in the dbhome BerkeleyDB directory.
        Use keyword arguments when calling this constructor.
        """
        myflags = DB_THREAD
        if create :
            myflags = myflags | DB_CREATE
        self.env = DbEnv()
        self.env.set_lk_detect(DB_LOCK_DEFAULT)  # enable auto deadlock avoidance
        self.env.open(dbhome, myflags | 
            DB_INIT_MPOOL | DB_INIT_LOCK | DB_INIT_LOG | DB_INIT_TXN)
        if truncate :
            myflags = myflags | DB_TRUNCATE
        self.db = Db(self.env)
        self.db.set_flags(DB_DUP)  # allow duplicate entries [warning: be careful w/ metadata]
        self.db.open(filename, DB_BTREE, myflags, mode)

        self.dbfilename = filename

        # Initialize the table names list if this is a new database
        if not DeadlockWrap(self.db.has_key, _table_names_key) :
            DeadlockWrap(self.db.put, _table_names_key, pickle.dumps([], 1))

        # TODO verify more of the database's metadata?

        self.__tablecolumns = {}


    def _db_print(self) :
        """Print the database to stdout for debugging"""
        print "******** Printing raw database for debugging ********"
        cur = self.db.cursor()
        try:
            key, data = DeadlockWrap(cur.first)
            while 1 :
                print `{key: data}`
                key, data = DeadlockWrap(cur.next)
        except error, dberror:
            if dberror[0] != DB_NOTFOUND :
                raise
            cur.close()


    def CreateTable(self, table, columns) :
        """CreateTable(table, columns) - Create a new table in the database
        raises TableDBError if it already exists or for other Db errors.
        """
        assert type(columns) == type([])
        txn = None
        try:
            # checking sanity of the table and column names here on
            # table creation will prevent problems elsewhere.
            if contains_metastrings(table) :
                raise ValueError, "bad table name: contains reserved metastrings"
            for column in columns :
                if contains_metastrings(column) :
                    raise ValueError, "bad column name: contains reserved metastrings"

            columnlist_key = _columns_key(table)
            if DeadlockWrap(self.db.has_key, columnlist_key) :
                raise TableDbError, "table already exists"

            txn = self.env.txn_begin()
            # store the table's column info
            DeadlockWrap(self.db.put, columnlist_key, pickle.dumps(columns, 1), txn)

            # add the table name to the tablelist
            tablelist = pickle.loads(DeadlockWrap(self.db.get, _table_names_key, txn, DB_RMW))
            tablelist.append(table)
            DeadlockWrap(self.db.delete, _table_names_key, txn)  # delete 1st, incase we opened with DB_DUP
            DeadlockWrap(self.db.put, _table_names_key, pickle.dumps(tablelist, 1), txn)

            DeadlockWrap(txn.commit)
            txn = None

        except error, dberror:
            if txn :
                txn.abort()
            raise TableDbError, dberror[1]


    def __load_column_info(self, table) :
        """initialize the self.__tablecolumns dict"""
        # check the column names
        try:
            tcolpickles = DeadlockWrap(self.db.get, _columns_key(table))
        except error, dberror:
            if dberror[0] != DB_NOTFOUND :
                raise
            raise TableDbError, "unknown table"
        self.__tablecolumns[table] = pickle.loads(tcolpickles)
    
    def __new_rowid(self, table, txn=None) :
        """Create a new unique row identifier"""
        unique = 0
        while not unique :
            # Generate a random 64-bit row ID string
            # (note: this code has <64 bits of randomness
            # but it's plenty for our database id needs!)
            p = xdrlib.Packer()
            p.pack_int(int(whrandom.random()*2147483647))
            p.pack_int(int(whrandom.random()*2147483647))
            newid = p.get_buffer()

            # Guarantee uniqueness by adding this key to the database
            try:
                DeadlockWrap(self.db.put,
                    _rowid_key(table, newid), None, txn, DB_NOOVERWRITE)
            except error, dberror:
                if dberror[0] != DB_KEYEXISTS :
                    raise
            else:
                unique = 1

        return newid

    
    def Insert(self, table, rowdict) :
        """Insert(table, datadict) - Insert a new row into the table
        using the keys+values from rowdict as the column values.
        """
        txn = None
        try:
            if not DeadlockWrap(self.db.has_key, _columns_key(table)) :
                raise TableDbError, "unknown table"

            # check the validity of each column name
            if not self.__tablecolumns.has_key(table) :
                self.__load_column_info(table)
            for column in rowdict.keys() :
                if not self.__tablecolumns[table].count(column) :
                    raise TableDbError, "unknown column: "+`column`

            # get a unique row identifier for this row
            rowid = self.__new_rowid(table)

            txn = self.env.txn_begin()

            # insert the row values into the table database
            for column, dataitem in rowdict.items() :
                # store the value
                DeadlockWrap(self.db.put,
                    _data_key(table, column, rowid),
                    dataitem, txn)

            DeadlockWrap(txn.commit)
            txn = None

        except error, dberror:
            if txn :
                txn.abort()
                DeadlockWrap(self.db.delete, _rowid_key(table, rowid))
            raise TableDbError, dberror[1]
 

    def Delete(self, table, conditions={}) :
        """Delete(table, conditions) - Delete items matching the given
        conditions from the table.
        * conditions is a dictionary keyed on column names
        containing condition functions expecting the data string as an
        argument and returning a boolean.
        """
        try:
            matching_rowids = self.__Select(table, [], conditions)

            # delete row data from all columns
            columns = self.__tablecolumns[table]
            for rowid in matching_rowids.keys() :
                txn = None
                try:
                    txn = DeadlockWrap(self.env.txn_begin)
                    for column in columns :
                        # delete the data key
                        DeadlockWrap(self.db.delete,
                            _data_key(table, column, rowid), txn)

                    DeadlockWrap(self.db.delete, _rowid_key(table, rowid), txn)
                    DeadlockWrap(txn.commit)
                except error, dberror:
                    if txn :
                        txn.abort()
                    raise

        except error, dberror:
            raise TableDbError, dberror[1]


    def Select(self, table, columns, conditions={}) :
        """Select(table, conditions) - retrieve specific row data
        Returns a list of row column->value mapping dictionaries.
        * columns is a list of which column data to return.  If
          columns is None, all columns will be returned.
        * conditions is a dictionary keyed on column names
        containing condition functions expecting the data string as an
        argument and returning a boolean.
        """
        try:
            if not self.__tablecolumns.has_key(table) :
                self.__load_column_info(table)
            if columns is None :
                columns = self.__tablecolumns[table]
            matching_rowids = self.__Select(table, columns, conditions)
        except error, dberror:
            raise TableDbError, dberror[1]
        
        # return the matches as a list of dictionaries
        return matching_rowids.values()


    def __Select(self, table, columns, conditions) :
        """__Select() - Used to implement Select and Delete (above)
        Returns a dictionary keyed on rowids containing dicts
        holding the row data for columns listed in the columns param
        that match the given conditions.
        * conditions is a dictionary keyed on column names
        containing condition functions expecting the data string as an
        argument and returning a boolean.
        """
        # check the validity of each column name
        if not self.__tablecolumns.has_key(table) :
            self.__load_column_info(table)
        if columns is None :
            columns = self.tablecolumns[table]
        for column in (columns + conditions.keys()) :
            if not self.__tablecolumns[table].count(column) :
                raise TableDbError, "unknown column: "+`column`

        # keyed on rows that match so far, containings dicts keyed on
        # column names containing the data for that row and column.
        matching_rowids = {}

        rejected_rowids = {} # keys are rowids that do not match

        # Apply conditions to column data to find what we want
        cur = self.db.cursor()
        column_num = -1
        for column, condition in conditions.items() :
            column_num = column_num + 1
            searchkey = _search_col_data_key(table, column)
            # speedup: don't linear search columns within loop
            if column in columns :
                savethiscolumndata = 1  # save the data for return
            else :
                savethiscolumndata = 0  # data only used for selection

            try:
                key, data = DeadlockWrap(cur.setRange, searchkey)
                while key[:len(searchkey)] == searchkey :
                    # extract the rowid from the key
                    rowid = key[-_rowid_str_len:]

                    if not rejected_rowids.has_key(rowid) :
                        # if no condition was specified or the condition
                        # succeeds, add row to our match list.
                        if not condition or condition(data) :
                            # only create new entries in matcing_rowids on
                            # the first pass, otherwise reject the
                            # rowid as it must not have matched
                            # the previous passes
                            if column_num == 0 :
                                if not matching_rowids.has_key(rowid) :
                                    matching_rowids[rowid] = {}
                                if savethiscolumndata :
                                    matching_rowids[rowid][column] = data
                            else :
                                rejected_rowids[rowid] = rowid
                        else :
                            if matching_rowids.has_key(rowid) :
                                del matching_rowids[rowid]
                            rejected_rowids[rowid] = rowid

                    key, data = DeadlockWrap(cur.next)

            except error, dberror:
                if dberror[0] != DB_NOTFOUND :
                    raise
                continue

        cur.close()

        # we're done selecting rows, garbage collect the reject list
        del rejected_rowids

        # extract any remaining desired column data from the
        # database for the matching rows.
        if len(columns) > 0 :
            for rowid, rowdata in matching_rowids.items() :
                for column in columns :
                    if rowdata.has_key(column) :
                        continue
                    try:
                        rowdata[column] = DeadlockWrap(self.db.get,
                            _data_key(table, column, rowid))
                    except error, dberror:
                        if dberror[0] != DB_NOTFOUND :
                            raise
                        rowdata[column] = None
            
        # return the matches
        return matching_rowids


    def Drop(self, table) :
        """Remove an entire table from the database
        """
        txn = None
        try:
            txn = self.env.txn_begin()

            # delete the column list
            DeadlockWrap(self.db.delete, _columns_key(table), txn)

            cur = self.db.cursor(txn)

            # delete all keys containing this tables column and row info
            table_key = _search_all_data_key(table)
            while 1 :
                key, data = DeadlockWrap(cur.setRange, table)
                # only delete items in this table
                if key[:len(table_key)] != table_key :
                    break
                DeadlockWrap(cur.delete)

            # delete all rowids used by this table
            table_key = _search_rowid_key(table)
            while 1 :
                key, data = DeadlockWrap(cur.setRange, table)
                # only delete items in this table
                if key[:len(table_key)] != table_key :
                    break
                DeadlockWrap(cur.delete)

            DeadlockWrap(cur.close)

            # delete the tablename from the table name list
            tablelist = pickle.loads(DeadlockWrap(self.db.get, _table_names_key, txn, DB_RMW))
            tablelist.remove(table)
            DeadlockWrap(self.db.delete, _table_names_key, txn)  # delete 1st, incase we opened with DB_DUP
            DeadlockWrap(self.db.put, _table_names_key, pickle.dumps(tablelist, 1), txn)

            DeadlockWrap(txn.commit)
            txn = None

            if self.__tablecolumns.has_key(table) :
                del self.__tablecolumns[table]

        except error, dberror:
            if txn :
                txn.abort()
            raise TableDbError, dberror[1]

