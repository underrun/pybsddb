#!/bin/env python
#------------------------------------------------------------------------
#               Copyright (c) 1998 by Total Control Software
#                         All Rights Reserved
#------------------------------------------------------------------------
#
# Module Name:  dbShelveClient.py
#
# Description:  Essentially a dbShelve that exports its methods to a
#               server process running elsewhere.
#
# Creation Date:    1/17/98 4:43:33PM
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
Implements the Client interface to the ShelveServer.  The SelveServer
is a process running at the other end of socket that has exclusive access
to one or more Shelve files.  Enables multi-process (multi-user) access to
the shelves.

The interface is a superset of the standard Shelve interface.  See docs there
for a description of how to use.
"""

#------------------------------------------------------------------------

import socket, string, time

import  db

from    cPickle     import Pickler, Unpickler
from    cStringIO   import StringIO

import  cPickle          # we need the module names in scope too.
import  cStringIO

from    dbShelveGlobals import *

#------------------------------------------------------------------------

error = "ShelveClient.error"
__version__ = '1.1.0'

#------------------------------------------------------------------------

class ShelveClient:
    def __init__(self, sock, connectArgs):
        self.sock = sock
        self.saveKey = None
        self.connectArgs = connectArgs

    def keys(self):
        t = (s_KEYS, "")
        return self.request(t)

    def __len__(self):
        t = (s_LEN, "")
        return self.request(t)

    def has_key(self, key):
        t = (s_HASKEY, str(key))
        return self.request(t)

    def __getitem__(self, key):
        t = (s_GETITEM, str(key))
        return self.request(t)

    def __setitem__(self, key, value):
        t = (s_SETITEM, (str(key), value))
        return self.request(t)

    def __delitem__(self, key):
        t = (s_DELITEM, str(key))
        return self.request(t)

    def close(self):
        if self.sock != None:
            t = (s_CLOSE, "")
            self.request(t)
            self.sock.close()
            self.sock = None

    def __del__(self):
        self.close()

    #----------------------------------------

    def setCursor(self, key):
        t = (s_SETCUR, str(key))
        (self.saveKey, value) = self.request(t)
        return (self.saveKey, value)

    def next(self):
        t = (s_NEXT, self.saveKey)
        (self.saveKey, value) = self.request(t)
        return (self.saveKey, value)

    def previous(self):
        t = (s_PREVIOUS, self.saveKey)
        (self.saveKey, value) = self.request(t)
        return (self.saveKey, value)

    def first(self):
        t = (s_FIRST, "")
        (self.saveKey, value) = self.request(t)
        return (self.saveKey, value)

    def last(self):
        t = (s_LAST, "")
        (self.saveKey, value) = self.request(t)
        return (self.saveKey, value)

    def sync(self):
        t = (s_SYNC, "")
        return self.request(t)

    def lock(self, key):
        pass

    #----------------------------------------

    def request(self, t):
        # pickle the request tuple
        f = StringIO()
        Pickler(f, 1).dump(t)
        ibuf = f.getvalue()

        while 1:
            try:
                # send it to the server
                self.sock.send(SIZEFMT % (len(ibuf), ))
                while ibuf:
                    numSent = self.sock.send(ibuf[:BLOCKSIZE])
                    ibuf = ibuf[numSent:]

                # wait for the response size
                size = self.sock.recv(SIZELEN)
                if not size:
                    raise error, ""
                size = string.atoi(size)

                # wait for the rest of the response
                data = []
                numRead = 0
                while numRead < size:
                    buf = self.sock.recv(size - numRead)
                    if not buf:
                        raise error, ""
                    data.append(buf)
                    numRead = numRead + len(buf)
                resp = string.join(data, '')
                break

            except (error, socket.error), val:
                # attempt one time to reconnect to the ShelveServer.
                self.sock.close()
                time.sleep(1)
                self.sock = apply(_connectHelper, self.connectArgs)



        # unpack the response and check for error
        (result, data) = Unpickler(StringIO(resp)).load()
        if result == 1:      # ShelveServer error
            raise error, data

        elif result == 2:   # some other error, get exception and val from data
            if type(data[0]) == type(''):
                raise eval(data[0]), data[1] # raise error from ShelveServer
            else:
                raise data[0], data[1]

        else:               # all is well
            return data

#------------------------------------------------------------------------

def _connectHelper(filename, dbtype, host, port, path):
    # Make the connection...
    try:
        if host:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect(host, port)
        else:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.connect(path)
    except socket.error, val:
        raise error, ("Unable to connect to ShelveServer.", val)


    # Open the file on the server, get a flag for result.
    f = StringIO()
    Pickler(f, 1).dump((filename, dbtype))

    sock.send(f.getvalue())
    flag = sock.recv(32)
    flag = string.atoi(flag)
    if flag == -1:
        raise error, "Unable to open shelve file"

    return sock

#---------------------------------------------------------------------------


def open(filename, dbtype=db.DB_HASH, host=None, port=DEF_INETPORT, path=None):
    """
    Open a socket connection to the ShelveServer.  If successful, create
    and return a ShelveClient object.
    """
    sock = _connectHelper(filename, dbtype, host, port, path)
    return ShelveClient(sock, (filename, dbtype, host, port, path))

#------------------------------------------------------------------------
#------------------------------------------------------------------------


def _test():
    sf = open('test.db', path='sock')   #host='localhost')
    sf[123] = 123
    sf['this is a string'] = 'This is another String. askfh aksj ajskdf kjasdf skjdf'
    sf['list'] = ['This', 'is', 'a', 'list', 'of', 'strings']

    sf.sync()
    print sf.keys()
    for k in sf.keys():
        print k, ' = ', sf[k]


if __name__ == '__main__':
    import pdb
    #pdb.run('_test()')
    _test()
