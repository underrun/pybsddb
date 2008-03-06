#----------------------------------------------------------------------
#  Copyright (c) 1999-2001, Digital Creations, Fredericksburg, VA, USA
#  and Andrew Kuchling. All rights reserved.
#
#  Redistribution and use in source and binary forms, with or without
#  modification, are permitted provided that the following conditions are
#  met:
#
#    o Redistributions of source code must retain the above copyright
#      notice, this list of conditions, and the disclaimer that follows.
#
#    o Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions, and the following disclaimer in
#      the documentation and/or other materials provided with the
#      distribution.
#
#    o Neither the name of Digital Creations nor the names of its
#      contributors may be used to endorse or promote products derived
#      from this software without specific prior written permission.
#
#  THIS SOFTWARE IS PROVIDED BY DIGITAL CREATIONS AND CONTRIBUTORS *AS
#  IS* AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED
#  TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A
#  PARTICULAR PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL DIGITAL
#  CREATIONS OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
#  INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
#  BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS
#  OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
#  ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR
#  TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
#  USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH
#  DAMAGE.
#----------------------------------------------------------------------


"""
This package initialization module provides a compatibility interface
that should enable bsddb3 to be a near drop-in replacement for the original
old bsddb module.  The functions and classes provided here are all
wrappers around the new functionality provided in the bsddb3.db module.

People interested in the more advanced capabilites of Berkeley DB 3.x
should use the bsddb3.db module directly.
"""

import _db
__version__ = _db.__version__

error = _db.DBError  # So bsddb3.error will mean something...

#----------------------------------------------------------------------


class _DBWithCursor:
    """
    A simple wrapper around DB that makes it look like the bsddbobject in
    the old module.  It uses a cursor as needed to provide DB traversal.
    """
    def __init__(self, db):
        self.db = db
        self.dbc = None
        self.db.set_get_returns_none(0)

    def __del__(self):
        self.close()

    def _checkCursor(self):
        if self.dbc is None:
            self.dbc = self.db.cursor()

    def __len__(self):                 return len(self.db)
    def __getitem__(self, key):        return self.db[key]
    def __setitem__(self, key, value): self.db[key] = value
    def __delitem__(self, key):        del self.db[key]

    def close(self):
        if self.dbc is not None:
            self.dbc.close()
        if self.db is not None:
            v = self.db.close()
        self.dbc = None
        self.db = None

    def keys(self):
        return self.db.keys()

    def has_key(self, key):
        return self.db.has_key(key)

    def set_location(self, key):
        self._checkCursor()
        return self.dbc.set(key)

    def next(self):
        self._checkCursor()
        rv = self.dbc.next()
        return rv

    def previous(self):
        self._checkCursor()
        rv = self.dbc.prev()
        return rv

    def first(self):
        self._checkCursor()
        rv = self.dbc.first()
        return rv

    def last(self):
        self._checkCursor()
        rv = self.dbc.last()
        return rv

    def sync(self):
        return self.db.sync()


#----------------------------------------------------------------------
# Compatibility object factory functions

def hashopen(file, flag='c', mode=0666, pgsize=None, ffactor=None, nelem=None,
            cachesize=None, lorder=None, hflags=0):

    flags = _checkflag(flag)
    d = _db.DB()
    d.set_flags(hflags)
    if cachesize is not None: d.set_cachesize(cachesize)
    if pgsize is not None:    d.set_pagesize(pgsize)
    if lorder is not None:    d.set_lorder(lorder)
    if ffactor is not None:   d.set_h_ffactor(ffactor)
    if nelem is not None:     d.set_h_nelem(nelem)
    d.open(file, _db.DB_HASH, flags, mode)
    return _DBWithCursor(d)

#----------------------------------------------------------------------

def btopen(file, flag='c', mode=0666,
            btflags=0, cachesize=None, maxkeypage=None, minkeypage=None,
            pgsize=None, lorder=None):

    flags = _checkflag(flag)
    d = _db.DB()
    if cachesize is not None: d.set_cachesize(cachesize)
    if pgsize is not None: d.set_pagesize(pgsize)
    if lorder is not None: d.set_lorder(lorder)
    d.set_flags(btflags)
    if minkeypage is not None: d.set_bt_minkey(minkeypage)
    if maxkeypage is not None: d.set_bt_maxkey(maxkeypage)
    d.open(file, _db.DB_BTREE, flags, mode)
    return _DBWithCursor(d)

#----------------------------------------------------------------------


def rnopen(file, flag='c', mode=0666,
            rnflags=0, cachesize=None, pgsize=None, lorder=None,
            rlen=None, delim=None, source=None, pad=None):

    flags = _checkflag(flag)
    d = _db.DB()
    if cachesize is not None: d.set_cachesize(cachesize)
    if pgsize is not None: d.set_pagesize(pgsize)
    if lorder is not None: d.set_lorder(lorder)
    d.set_flags(rnflags)
    if delim is not None: d.set_re_delim(delim)
    if rlen is not None: d.set_re_len(rlen)
    if source is not None: d.set_re_source(source)
    if pad is not None: d.set_re_pad(pad)
    d.open(file, _db.DB_RECNO, flags, mode)
    return _DBWithCursor(d)

#----------------------------------------------------------------------


def _checkflag(flag):
    if flag == 'r':
        flags = _db.DB_READONLY
    elif flag == 'rw':
        flags = 0
    elif flag == 'w':
        flags =  _db.DB_CREATE
    elif flag == 'c':
        flags =  _db.DB_CREATE
    elif flag == 'n':
        flags = _db.DB_TRUNCATE
    else:
        raise error, "flags should be one of 'r', 'w', 'c' or 'n'"
    return flags | _db.DB_THREAD

#----------------------------------------------------------------------


# This is a silly little hack that allows apps to continue to use the
# DB_THREAD flag even on systems without threads without freaking out
# BerkeleyDB.
#
# This assumes that if Python was built with thread support then
# BerkeleyDB was too.

try:
    import thread
    del thread
except ImportError:
    _db.DB_THREAD = 0


#----------------------------------------------------------------------
