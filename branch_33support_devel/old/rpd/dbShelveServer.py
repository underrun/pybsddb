#!/bin/env python
#------------------------------------------------------------------------
#               Copyright (c) 1998 by Total Control Software
#                         All Rights Reserved
#------------------------------------------------------------------------
#
# Module Name:  dbShelveServer.py
#
# Description:  A ShelveServer is a single-process, multiple-connection,
#               pseudo-asyncronous server that serves up access to dbShelve
#               files.
#
# Creation Date:    1/15/98 11:16:13PM
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
A ShelveServer is a single-process, multiple-connection, pseudo-asyncronous
server that serves up access to dbShelve files.
"""

#------------------------------------------------------------------------

import sys, os, socket, signal, getopt

from    cPickle     import Pickler, Unpickler
from    cStringIO   import StringIO
import  db
import  dbShelve

from dbShelveGlobals import *
from TCS.Dispatcher  import *
from TCS.logger      import *

__version__ = '1.1.2'

#------------------------------------------------------------------------

shelveNames = {}


class ShelfRef:
    shelve   = None
    refCount = 0
    def incRef(self):
        self.refCount = self.refCount + 1
    def decRef(self):
        self.refCount = self.refCount - 1



def newShelve(filename, dbtype):
    sr        = ShelfRef()
    sr.shelve = dbShelve.open(filename, 'w', filetype=dbtype)
    sr.incRef()
    shelveNames[filename] = sr
    return sr


#------------------------------------------------------------------------
#------------------------------------------------------------------------

class ListeningSocket(DispatchableSocket):
    readEvents  = 1
    writeEvents = 0

    def __init__(self, port=0, path=None):
        if port:
            listenSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            listenSock.bind('', port)

        elif path:
            listenSock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            try:    os.unlink(path)
            except  os.error:    pass
            listenSock.bind(path)

        listenSock.listen(5)
        DispatchableSocket.__init__(self, listenSock)

    def handleClose(self):
        self.sock.close()
        self.dispatcher.removeDispatchable(self)


    def handleReadReady(self):
        (conn, addr) = self.sock.accept()
        nc = NewConnection(conn)
        self.dispatcher.addDispatchable(nc)

    def handleWriteReady(self):
        pass

#---------------------------------------------------------------------------

#
# Since we only have to read the filename at the begining of the connection
# this class is used to do that and nothing else.  It makes the ongoing
# requests more efficient to not have to check for that state on each read.
# When this class has finished setting up the new client, it creates a
# ConnectedClient object to take over the socket.
#
class NewConnection(DispatchableSocket):
    readEvents  = 1
    writeEvents = 0

    def handleReadReady(self):
        buf = self.recv(1024)
        filename, dbtype = Unpickler(StringIO(buf)).load()

        log.msg(INFO, "Got connection request for " + filename, name='dbShelveServer')

        # find it if we already have it open
        if shelveNames.has_key(filename):
            sRef = shelveNames[filename]
            sRef.incRef()

        else:   # otherwise open it and add to the list
            try:
                sRef = newShelve(filename, dbtype)
            except:
                log.msg(WARNING, "Can't make new shelve: %s %s-%s",
                        filename, str(sys.exc_type), str(sys.exc_value),
                        name='dbShelveServer')
                self.send("-1")
                self.dispatcher.removeDispatchable(self)
                return

        # Now that we have the dbShelve, switch this socket to a new
        # handler type and get rid of this one...
        cc = ConnectedClient(self.sock, sRef, filename)
        self.dispatcher.addDispatchable(cc)
        self.dispatcher.removeDispatchable(self)
        self.send("0")

    #----------------------------------------
    # in case the other side closes before we
    # get the startup data...
    def handleClose(self):
        self.sock.close()
        self.dispatcher.removeDispatchable(self)

#---------------------------------------------------------------------------

WAITINGFORSIZE = 1
WAITINGFORDATA = 2

class ConnectedClient(DispatchableSocket):
    readEvents  = 1
    writeEvents = 0

    def __init__(self, sock, sRef, filename):
        self.sRef = sRef
        self.filename = filename
        DispatchableSocket.__init__(self, sock)
        self.initialState()

    def initialState(self):
        self.state   = WAITINGFORSIZE
        self.numRead = 0
        self.data    = []
        self.reqSize = SIZELEN

    #----------------------------------------
    def handleReadReady(self):
        buf = self.recv(self.reqSize - self.numRead)
        self.data.append(buf)
        self.numRead = self.numRead + len(buf)
        log.msg(DEBUG, "got block, size: %d  waiting for: %d", len(buf), self.reqSize)

        # do we have the whole block yet?
        if self.numRead == self.reqSize:

            if self.state == WAITINGFORSIZE:
                # change state
                self.reqSize = string.atoi(string.join(self.data, ''))
                self.state   = WAITINGFORDATA
                self.data    = []
                self.numRead = 0

            elif self.state == WAITINGFORDATA:
                req = StringIO(string.join(self.data, ''))
                self.initialState()
                (cmd, data) = Unpickler(req).load()
                method      = getattr(self, sMethodMap[cmd])
                method(data)


    #----------------------------------------
    def handleClose(self):
        self.doClose()
        self.sock.close()
        self.dispatcher.removeDispatchable(self)


    #----------------------------------------
    def handleWriteReady(self):
        buf = self.response[:BLOCKSIZE]
        numSent = self.send(buf)
        log.msg(DEBUG, "sent block, size: %d", numSent)

        self.response = self.response[numSent:]
        if not self.response:
            self.writeEvents = 0
            self.writeBlocked = 0


    #----------------------------------------
    def s_KEYS(self, data):
        try:
            keys = self.sRef.shelve.keys()
            self.sendResponse((0, keys))
        except:
            self.sendResponse((2, (sys.exc_type, sys.exc_value)))

    #----------------------------------------
    def s_LEN(self, data):
        try:
            length = len(self.sRef.shelve)
            self.sendResponse((0, length))
        except:
            self.sendResponse((2, (sys.exc_type, sys.exc_value)))

    #----------------------------------------
    def s_HASKEY(self, key):
        try:
            rv = self.sRef.shelve.has_key(key)
            self.sendResponse((0, rv))
        except:
            self.sendResponse((2, (sys.exc_type, sys.exc_value)))

    #----------------------------------------
    def s_SETITEM(self, data):
        (key, value) = data
        try:
            self.sRef.shelve[key] = value
            self.sendResponse((0, None))
        except:
            self.sendResponse((2, (sys.exc_type, sys.exc_value)))

    #----------------------------------------
    def s_GETITEM(self, key):
        try:
            rv = self.sRef.shelve[key]
            self.sendResponse((0, rv))
        except:
            self.sendResponse((2, (sys.exc_type, sys.exc_value)))

    #----------------------------------------
    def s_DELITEM(self, key):
        try:
            del self.sRef.shelve[key]
            self.sendResponse((0, None))
        except:
            self.sendResponse((2, (sys.exc_type, sys.exc_value)))

    #----------------------------------------
    def doClose(self):
        log.msg(INFO, "Closing connection for " + self.filename, name='dbShelveServer')
        self.sRef.decRef()
        if self.sRef.refCount == 0:
            self.sRef.shelve.close()
            del shelveNames[self.filename]
        self.dispatcher.removeDispatchable(self)

    def s_CLOSE(self, data):
        try:
            self.doClose()
            self.sendResponse((0, None))
        except:
            self.sendResponse((2, (sys.exc_type, sys.exc_value)))

    #----------------------------------------
    def s_SETCUR(self, key):
        try:
            (key, value) = self.sRef.shelve.setCursor(key)
            self.sendResponse((0, (key, value)))
        except:
            self.sendResponse((2, (sys.exc_type, sys.exc_value)))

    #----------------------------------------
    def s_NEXT(self, key):
        try:
            self.sRef.shelve.setCursor(key)
            (key, value) = self.sRef.shelve.next()
            self.sendResponse((0, (key, value)))
        except:
            self.sendResponse((2, (sys.exc_type, sys.exc_value)))

    #----------------------------------------
    def s_PREVIOUS(self, key):
        try:
            self.sRef.shelve.setCursor(key)
            (key, value) = self.sRef.shelve.previous()
            self.sendResponse((0, (key, value)))
        except:
            self.sendResponse((2, (sys.exc_type, sys.exc_value)))

    #----------------------------------------
    def s_FIRST(self, data):
        try:
            (key, value) = self.sRef.shelve.first()
            self.sendResponse((0, (key, value)))
        except:
            self.sendResponse((2, (sys.exc_type, sys.exc_value)))

    #----------------------------------------
    def s_LAST(self, data):
        try:
            (key, value) = self.sRef.shelve.last()
            self.sendResponse((0, (key, value)))
        except:
            self.sendResponse((2, (sys.exc_type, sys.exc_value)))

    #----------------------------------------
    def s_SYNC(self, data):
        try:
            rv = self.sRef.shelve.sync()
            self.sendResponse((0, rv))
        except:
            self.sendResponse((2, (sys.exc_type, sys.exc_value)))

    #----------------------------------------

    def sendResponse(self, t):
        # pickle the response tuple
        f = StringIO()
        p = Pickler(f, 1)       # use binary mode
        p.dump(t)

        # send it to the client
        self.response = f.getvalue()
        self.send(SIZEFMT % len(self.response))
        if len(self.response) < BLOCKSIZE:
            self.send(self.response)
            self.response = ''
        else:
            # enable ourselves to be dispatched on write events
            self.writeEvents = 1
            self.writeBlocked = 1


#------------------------------------------------------------------------
#------------------------------------------------------------------------

def usage():
    print "Usage:  dbShelveServer.py  [-p port] [-u path] [-h dir] [-f file] [-l level]"
    print
    print "           -p port     = port to bind to for inet sockets [%s]" % (DEF_INETPORT,)
    print "           -u path     = path to bind to for unix sockets [None]"
    print "           -h dir      = DB home directory [.]"
    print "           -f file     = Log file [stderr]"
    print "           -l loglevel = DEBUG | INFO | WARNING | CRITICAL | FATAL | LOG"
    print

#---------------------------------------------------------------------------

TERMSignal = 'TERMSignal'

def raiseTERM(a, b):
    raise TERMSignal

#------------------------------------------------------------------------
# Main function
#------------------------------------------------------------------------

def main():
    inetport = DEF_INETPORT
    unixpath = None
    homedir  = '.'
    logfile  = None
    level    = WARNING

    # Get the command-line args
    try:
        optlist, args = getopt.getopt(sys.argv[1:], 'p:u:h:f:l:')
    except getopt.error:
        usage()
        sys.exit(1)
    if args:
        usage()
        sys.exit(1)

    try:
        for flag,value in optlist:
            if flag == '-p':    inetport = string.atoi(value)
            elif flag == '-u':  unixpath = value
            elif flag == '-h':  homedir = value
            elif flag == '-f':  logfile = value
            elif flag == '-l':  level = levelMap[value]
    except (KeyError, ValueError):
        usage()
        sys.exit(1)

    if logfile:
        log.setOutputHandler(open(logfile, 'a'))
    log.setLogLevel(level)

    db.appinit(homedir, db.DB_CREATE|db.DB_INIT_LOCK|db.DB_INIT_MPOOL)

    # create the dispatcher
    d  = Dispatcher()
    d.setTimeout(15)

    # create the listening socket(s) and add to dispatcher
    if inetport:
        d.addDispatchable(ListeningSocket(port=inetport))
    if unixpath:
        d.addDispatchable(ListeningSocket(path=unixpath))

    signal.signal(signal.SIGTERM, raiseTERM)

    while 1:
        try:
            log.msg(LOG, 'Starting dbShelveServer:\n\t'
                         'inetport = %d\n\t'
                         'unixpath = %s\n\t'
                         'homedir  = %s\n\t'
                         'logfile  = %s\n\t'
                         'loglevel = %s',
                         inetport, unixpath, homedir, logfile, levelMap[level],
                         name='dbShelveServer')
            d.mainLoop()

        except KeyboardInterrupt:
            log.msg(FATAL, 'Got INT signal, shutting down', name='dbShelveServer')
            break

        except TERMSignal:
            log.msg(FATAL, 'Got TERM signal, shutting down', name='dbShelveServer')
            break


    d.shutdown()
    if unixpath:
        try:    os.unlink(unixpath)
        except  os.error:    pass

    for k,v in shelveNames.items():
        v.shelve.sync()
        v.shelve.close()
        del shelveNames[k]


    db.appexit()

#------------------------------------------------------------------------

if __name__ == "__main__":
    #import pdb
    #pdb.run('main()')
    main()
