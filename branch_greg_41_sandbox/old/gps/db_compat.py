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
    d.set_cachesize(cachesize)
    d.set_pagesize(pgsize)
    d.set_lorder(lorder)
    d.set_flags(hflags)
    d.set_h_ffactor(ffactor)
    d.set_h_nelem(nelem)
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
    d.set_cachesize(cachesize)
    d.set_pagesize(pgsize)
    d.set_lorder(lorder)
    d.set_flags(btflags)
    d.set_bt_minkey(minkeypage)
    d.set_bt_maxkey(maxkeypage)
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
    d.set_cachesize(cachesize)
    d.set_pagesize(pgsize)
    d.set_lorder(lorder)
    d.set_flags(rnflags)
    d.set_re_delim(delim)
    d.set_re_len(rlen)
    d.set_re_source(source)
    d.set_re_pad(pad)
    d.open(file, DB_RECNO, flags, mode)
    return d

#---------------------------------------------------------------------------

