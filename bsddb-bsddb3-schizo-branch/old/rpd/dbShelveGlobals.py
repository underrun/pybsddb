#!/bin/env python
#------------------------------------------------------------------------
#               Copyright (c) 1998 by Total Control Software
#                         All Rights Reserved
#------------------------------------------------------------------------
#
# Module Name:  dbShelveGlobals.py
#
# Description:  Common values for use between the client and server...
#
# Creation Date:    1/15/98 11:11:18PM
#
# License:      This is free software.  You may use this software for any
#               purpose including modification/redistribution, so long as
#               this header remains intact and that you do not claim any
#               rights of ownership or authorship of this software.  This
#               software has been tested, but no warranty is expressed or
#               implied.
#
#------------------------------------------------------------------------



SIZEFMT = '%09d'
SIZELEN = 9

BLOCKSIZE = 8192

DEF_INETPORT = 5055

s_KEYS      = 101
s_LEN       = 102
s_HASKEY    = 103
s_SETITEM   = 104
s_GETITEM   = 105
s_DELITEM   = 106
s_CLOSE     = 107
s_SETCUR    = 108
s_NEXT      = 109
s_PREVIOUS  = 110
s_FIRST     = 111
s_LAST      = 112
s_SYNC      = 113

sMethodMap = {
    s_KEYS      : 's_KEYS',
    s_LEN       : 's_LEN',
    s_HASKEY    : 's_HASKEY',
    s_SETITEM   : 's_SETITEM',
    s_GETITEM   : 's_GETITEM',
    s_DELITEM   : 's_DELITEM',
    s_CLOSE     : 's_CLOSE',
    s_SETCUR    : 's_SETCUR',
    s_NEXT      : 's_NEXT',
    s_PREVIOUS  : 's_PREVIOUS',
    s_FIRST     : 's_FIRST',
    s_LAST      : 's_LAST',
    s_SYNC      : 's_SYNC',

    }


#------------------------------------------------------------------------
#------------------------------------------------------------------------
