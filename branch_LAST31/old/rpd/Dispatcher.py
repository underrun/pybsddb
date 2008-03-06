#!/bin/env python
#------------------------------------------------------------------------
#               Copyright (c) 1998 by Total Control Software
#                         All Rights Reserved
#------------------------------------------------------------------------
#
# Module Name:  Dispatcher.py
#
# Description:  Classes to implement an event dispatcher, with socket,
#               file, timer, and idle-time events
#
# Creation Date:    3/27/97 12:22:32PM
#
# License:      This is free software.  You may use this software for any
#               purpose including modification/redistribution, so long as
#               this header remains intact and that you do not claim any
#               rights of ownership or authorship of this software.  This
#               software has been tested, but no warranty is expressed or
#               implied.
#
#------------------------------------------------------------------------

import  sys, os, socket, select, time
from    cStringIO   import StringIO
from    errno       import *
from    logger      import *

#------------------------------------------------------------------------

READ_EVENT  = 1
WRITE_EVENT = 2
EXCP_EVENT  = 3

__version__ = '1.0.1'

#------------------------------------------------------------------------

class IdleTimeProcessor:
    """
    If the main loop in the dispatcher times out with no incoming messages or
    timers, then there is an opprotunity for IdleTime functions to do thier
    thing.  Derive from this class and overload the handleIdle method.

    A data memeber named dispatcher is added to any instances of this class
    that are added to the Dispatcher.
    """

    def handleIdle(self):
        log.msg(WARNING, "Unhandled event", name="IdleTimeProcessor.handleIdle")

    def handleClose(self):
        pass

    def handlePyExcept(self):
        import traceback
        f = StringIO()
        traceback.print_exc(file = f)
        log.msg(WARNING, "%s", f.getvalue(), name="IdleTimeProcessor.handlePyExcept")

#------------------------------------------------------------------------

class Timer:
    """
    An object that is able to be loaded into the Dispatcher and act as either
    a one-shot or a recurring timer.  You can either supply a handleTimeout
    method in derived classes to receive control when the timer expires, or supply
    a function (or other callable) object and a tuple of args to be called as a
    callback function.

    A data memeber named dispatcher is added to any instances of this class
    that are added to the Dispatcher.
    """

    def __init__(self, when, oneShot=0, duration=1, callback=None, cbArgs=()):
        """
        Build a Timer object.  Parameters are:
            when        UTC time in seconds (as from time() of when to fire timer.
            oneShot     Flag specifiying if this timer only happens once or is
                        recurring.  If oneShot, then the dispatcher will automatically
                        remove the timer after it fires.
            duration    How many seconds between each recurring timer.

            callback    a function or other callable object to be used as a callback,
                        instead of dispatching through the handleTimeout method in a
                        derived class.
            cbArgs      A tuple of args to pass to the callback function.  It will have
                        a reference to the timer object inserted in the first position,
                        (so the callback can have access to the dispatcher, duration time,
                        etc.)
        """
        self.when       = when
        self.oneShot    = oneShot
        self.duration   = duration
        self.callback   = callback
        self.cbArgs     = cbArgs

    #-----------------------------------
    def __cmp__(self, o):
        """ Allows list of Timers to be sorted. """
        return int(self.when) - int(o.when)

    #-----------------------------------
    def handleTimeout(self):
        if self.callback:
            apply(self.callback, ( self, ) + self.cbArgs )
        else:
            log.msg(WARNING, "Unhandled event", name="Timer.handleTimeout")


    #-----------------------------------
    def handleClose(self):
        pass

    #-----------------------------------
    def handlePyExcept(self):
        import traceback
        f = StringIO()
        traceback.print_exc(file = f)
        log.msg(WARNING, "%s", f.getvalue(), name="Timer.handlePyExcept")

#------------------------------------------------------------------------

class DispatchableSocket:
    """
    This is the base class for sockets that will be handled by the
    Dispatcher class.  Other classes should derive from this and override
    the empty handle*** methods for real functionality.

    A data memeber named dispatcher is added to any instances of this class
    that are added to the Dispatcher.
    """

    # Set these in derived classes to specify what you are looking for
    readEvents   = 0
    writeEvents  = 0
    writeBlocked = 0

    def __init__(self, sock, callback=None, cbArgs=()):
        """
        Create a new DispatchableSocket.  Parameters are:
            sock        A socket or socket-like object to dispatch read
                        and/or write events for.

            callback    a function or other callable object to be used as a callback,
                        instead of dispatching through the handle*** methods in a
                        derived class.
            cbArgs      A tuple of args to pass to the callback function.  It will have
                        a reference to this object inserted in the first position,
                        (so the callback can have access to the socker, etc.)
                        and in the second position there will be a flag indicating
                        what kind of event was recieved, (READ_EVENT, WRITE_EVENT,
                        EXCP_EVENT)
        """
        self.sock = sock
        self.sock.setblocking(0)
        self.callback     = callback
        self.cbArgs       = cbArgs
        self.writeBlocked = 0

    #-----------------------------------
    def fileno(self):
        return self.sock.fileno()

    #-----------------------------------
    def handleReadReady(self):
        if self.callback:
            apply(self.callback, (self, READ_EVENT) + self.cbArgs)
        else:
            log.msg(WARNING, "Unhandled event", name="DispatchableSocket.handleReadReady")

    def handleWriteReady(self):
        if self.callback:
            apply(self.callback, (self, WRITE_EVENT) + self.cbArgs)
        else:
            log.msg(WARNING, "Unhandled event", name="DispatchableSocket.handleWriteReady")

    def handleSockExcept(self):
        if self.callback:
            apply(self.callback, (self, EXCP_EVENT) + self.cbArgs)
        else:
            log.msg(WARNING, "Unhandled event", name="DispatchableSocket.handleSockExcept")

    def handleClose(self):
        self.sock.close()
        self.dispatcher.removeDispatchable(self)


    def handlePyExcept(self):
        import traceback
        f = StringIO()
        traceback.print_exc(file = f)
        log.msg(WARNING, "%s", f.getvalue(), name="DispatchableSocket.handlePyExcept")

    #-----------------------------------
    def send(self, data):
        try:
            return self.sock.send(data)
        except socket.error, (errnum, errmsg):
            if (errnum == ECONNRESET or errnum == EPIPE):
                self.handleClose()
                return 0
            if errnum == EWOULDBLOCK:
                self.writeBlocked = 1
                return 0
            else:
                raise socket.error, (errnum, errmsg)

    #-----------------------------------
    def recv(self, buffsize):
        try:
            data = self.sock.recv(buffsize)
            if not data:
                # a closed connection is indicated by signaling
                # a read condition, and having recv() return 0 bytes.
                try:    # If we still have a socket do your thing else...
                    self.handleClose()
                except: # ... nevermind
                    pass
                return ''
            else:
                return data
        except socket.error, (errnum, errmsg):
            if errnum == ECONNRESET or errnum == EPIPE:
                self.handleClose()
                return ''
            else:
                raise socket.error, (errnum, errmsg)


#------------------------------------------------------------------------

if os.name == "posix":
    class DispatchableFile:
        """
        Makes a real file descriptor look like a socket so it can be used with
        DispatchableSocket for readReady events, etc.

        Use like this:
            f = open(filename)
            ...
            c = SomeChildOfDispatchableSocket(DispatchableFile(f))
        """

        def __init__(self, file):
            self.file = file

        def fileno(self):
            return self.file.fileno()

        def setblocking(self, blocking):
            import fcntl, FCNTL
            fd    = self.file.fileno()
            flags = fcntl.fcntl(fd, FCNTL.F_GETFL, 0)
            if not blocking:
                flags = flags | FCNTL.O_NONBLOCK
            else:
                flags = flags & ~FCNTL.O_NONBLOCK
            fcntl.fcntl(fd, FCNTL.F_SETFL, flags)

        def recv(self, bufsize):
            return self.file.read(bufsize)

        def send(self, data):
            return self.file.write(data)

        def close(self):
            self.file.close()

        def shutdown(self, how):
            self.file.close()

#------------------------------------------------------------------------

class Dispatcher:
    """
    This class is what handles distaching socket events to objects
    capable of handling them. (Children of the DispatchableSocket class.)
    Usage is simple:

        d = Dispatcher()
        d.addDispatchable(ds1)
        d.addDispatchable(ds2)
        d.mainLoop()

    The main loop will continue to run until all dispatchable objects
    have been removed from the dispatcher's control.
    """

    def __init__(self):
        self.dispObjs  = []
        self.idleObjs  = []
        self.timerObjs = []
        self.timeout   = 30.0

    def __del__(self):
        self.shutdown()

    def shutdown(self):
        for x in self.dispObjs:
            x.handleClose()
        for x in self.idleObjs:
            x.handleClose()
        for x in self.timerObjs:
            x.handleClose()

    #-----------------------------------
    def addDispatchable(self, obj):
        obj.dispatcher = self
        self.dispObjs.append(obj)

    def removeDispatchable(self, obj):
        dObjs = self.dispObjs
        for x in range(len(dObjs)):
            if dObjs[x] is obj:
                dObjs[x].callback   = None
                dObjs[x].dispatcher = None
                del dObjs[x]
                break

    #-----------------------------------
    def addIdle(self, obj):
        obj.dispatcher = self
        self.idleObjs.append(obj)

    def removeIdle(self, obj):
        iObjs = self.idleObjs
        for x in range(len(iObjs)):
            if iObjs[x] is obj:
                iObjs[x].callback   = None
                iObjs[x].dispatcher = None
                del iObjs[x]
                break

    #-----------------------------------
    def addTimer(self, obj):
        obj.dispatcher = self
        self.timerObjs.append(obj)
        self.timerObjs.sort()

    def removeTimer(self, obj):
        tObjs = self.timerObjs
        for x in range(len(tObjs)):
            if tObjs[x] is obj:
                tObjs[x].callback   = None
                tObjs[x].dispatcher = None
                del tObjs[x]
                break

    #-----------------------------------
    def setTimeout(self, seconds):
        self.timeout = seconds


    #-----------------------------------
    def pollDispatchables(self, timeout):
        r = filter(lambda x: x.readEvents,                     self.dispObjs)
        w = filter(lambda x: x.writeEvents and x.writeBlocked, self.dispObjs)
        e = self.dispObjs[:]
        try:                    # This helps us deal with signal errors...
            (r, w, e) = select.select(r, w, e, timeout)
        except select.error:    # ...So if we get one, ignore it.
            pass

        # if we timed-out (got empty lists) then return and do the
        # idle time stuff
        if not r and not w and not e:
            return 0

        for x in r:
            try:    x.handleReadReady()
            except: x.handlePyExcept()
        for x in w:
            try:    x.handleWriteReady()
            except: x.handlePyExcept()
        for x in e:
            try:    x.handleSockExcept()
            except: x.handlePyExcept()

        return 1

    #-----------------------------------
    def runIdles(self):
        for x in self.idleObjs:
            try:    x.handleIdle()
            except: x.handlePyExcept()

    #-----------------------------------
    def checkTimers(self):
        count = 0
        now   = time.time()

        while self.timerObjs and self.timerObjs[0].when < now:
            obj = self.timerObjs[0]
            try:    obj.handleTimeout()
            except: obj.handlePyExcept()
            count = count + 1

            # if the object didn't remove or reschedule itself,
            # figure out what to do with it.
            if self.timerObjs and (obj is self.timerObjs[0]):
                if obj.oneShot:
                    self.timerObjs[0].callback = None
                    self.timerObjs[0]          = None
                    del self.timerObjs[0]
                else:
                    obj.when = now + obj.duration
                    self.timerObjs.sort()

        return count, now

    #-----------------------------------
    def mainLoop(self):
        # loop until we have no more dispatchables or timers
        while self.dispObjs or self.timerObjs:
            tCount, now = self.checkTimers()
            if self.timerObjs:
                timeout = min(self.timerObjs[0].when-now,
                              self.timeout)
            else:
                timeout = self.timeout

            if self.dispObjs or self.timerObjs:
                dCount = self.pollDispatchables(timeout)

            if not tCount and not dCount:
                self.runIdles()



#------------------------------------------------------------------------
#------------------------------------------------------------------------



def _testcb(timer):
    log.msg(INFO, 'tick: %s' % time.time(), name='_testcb')

def _test():
    d = Dispatcher()
    t = Timer(time.time()+5, 0, callback=_testcb)
    d.addTimer(t)

    d.mainLoop()



if __name__ == '__main__':
    _test()