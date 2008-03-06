#!/bin/env python
#------------------------------------------------------------------------
#               Copyright (c) 1997 by Total Control Software
#                         All Rights Reserved
#------------------------------------------------------------------------
#
# Module Name:  dbShelve.py
#
# Description:  A reimplementation of the standard shelve.py that
#               forces the use of cPickle, cStringIO, and DB.
#
# Creation Date:    11/3/97 3:39:04PM
#
# License:      This is free software.  You may use this software for any
#               purpose including modification/redistribution, so long as
#               this header remains intact and that you do not claim any
#               rights of ownership or authorship of this software.  This
#               software has been tested, but no warranty is expressed or
#               implied.
#
#------------------------------------------------------------------------


"""
Manage shelves of pickled objects.

A "shelf" is a persistent, dictionary-like object.  The difference
with db databases is that the values (not the keys!) in a shelf can
be essentially arbitrary Python objects -- anything that the "pickle"
module can handle.  This includes most class instances, recursive data
types, and objects containing lots of shared sub-objects.  The keys
are ordinary strings.

To summarize the interface (key is a string, data is an arbitrary
object):

    import dbShelve
    d = dbShelve.open(filename) # open, with bsddb filename -- no suffix

    d[key] = data   # store data at key (overwrites old data if
                    # using an existing key)
    data = d[key]   # retrieve data at key (raise KeyError if no
                    # such key)
    del d[key]      # delete data stored at key (raises KeyError
                    # if no such key)
    flag = d.has_key(key)   # true if the key exists
    list = d.keys()         # a list of all existing keys (slow!)

    d.close()   # close it

Dependent on the implementation, closing a persistent dictionary may
or may not be necessary to flush changes to disk.
"""
#------------------------------------------------------------------------

from    cPickle import Pickler, Unpickler
from    cStringIO import StringIO
import  db

__version__ = '1.1.0'


#------------------------------------------------------------------------

class dbShelf:
    def __init__(self, theDB):
        self.theDB = theDB
        self.cursor = None

    def keys(self):
        return self.theDB.keys()

    def __len__(self):
        return len(self.theDB)

    def has_key(self, key):
        return self.theDB.has_key(str(key))

    def __getitem__(self, key):
        f = StringIO(self.theDB[str(key)])
        return Unpickler(f).load()

    def __setitem__(self, key, value):
        f = StringIO()
        p = Pickler(f, 1)
        p.dump(value)
        self.theDB[str(key)] = f.getvalue()

    def __delitem__(self, key):
        del self.theDB[str(key)]

    def __del__(self):
        self.close()

    #----------------------------------------------
    # non-dictionary methods

    def setCursor(self, key):
        if not self.cursor:
            self.cursor = self.theDB.cursor()
        (key, value) = self.cursor.set(str(key))
        f = StringIO(value)
        return (key, Unpickler(f).load())

    def next(self):
        if not self.cursor:
            self.cursor = self.theDB.cursor()
        (key, value) = self.cursor.next()
        f = StringIO(value)
        return (str(key), Unpickler(f).load())

    def previous(self):
        if not self.cursor:
            self.cursor = self.theDB.cursor()
        (key, value) = self.cursor.previous()
        f = StringIO(value)
        return (key, Unpickler(f).load())

    def first(self):
        if not self.cursor:
            self.cursor = self.theDB.cursor()
        (key, value) = self.cursor.first()
        f = StringIO(value)
        return (key, Unpickler(f).load())

    def last(self):
        if not self.cursor:
            self.cursor = self.theDB.cursor()
        (key, value) = self.cursor.last()
        f = StringIO(value)
        return (key, Unpickler(f).load())

    def sync(self):
        return self.theDB.sync()

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.theDB:
            self.theDB.close()
        self.theDB = None


#---------------------------------------------------------------------------


def open(filename, flags=db.DB_CREATE, mode=0666, cache=0, filetype=db.DB_HASH):
    if type(flags) == type(''):
        sflag = flags
        if sflag == 'r':
            flags = db.DB_READONLY
        elif sflag == 'rw':
            flags = 0
        elif sflag == 'w':
            flags =  db.DB_CREATE
        elif sflag == 'c':
            flags =  db.DB_CREATE
        elif sflag == 'n':
            flags = db.DB_TRUNCATE
        else:
            raise error, "flags should be one of 'r', 'w', 'c' or 'n' or use the db.DB_* flags"

    d = db.DB()
    d.info.db_cache = cache
    d.open(filename, filetype, flags, mode)
    return dbShelf(d)

#---------------------------------------------------------------------------
#---------------------------------------------------------------------------
