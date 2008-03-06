#!/bin/env python
#------------------------------------------------------------------------
#               Copyright (c) 1998 by Total Control Software
#                         All Rights Reserved
#------------------------------------------------------------------------
#
# Module Name:  logger.py
#
# Description:  Simple, but extensible message logger
#
# Creation Date:    1/16/98 8:50:37PM
#
# License:      This is free software.  You may use this software for any
#               purpose including modification/redistribution, so long as
#               this header remains intact and that you do not claim any
#               rights of ownership or authorship of this software.  This
#               software has been tested, but no warranty is expressed or
#               implied.
#
#------------------------------------------------------------------------

import sys, time, string

#---------------------------------------------------------------------------
# Severity Levels for trace and alarms
DEBUG       = 1
INFO        = 2
WARNING     = 3
CRITICAL    = 4
FATAL       = 5
LOG         = 6                # this level can't be turned off

# a map from level to text and back
levelMap = {    DEBUG   : "DEBUG",
                INFO    : "INFO",
                WARNING : "WARNING",
                CRITICAL: "CRITICAL",
                FATAL   : "FATAL",
                LOG     : "LOG",

                "DEBUG"   : DEBUG,
                "INFO"    : INFO,
                "WARNING" : WARNING,
                "CRITICAL": CRITICAL,
                "FATAL"   : FATAL,
                "LOG"     : LOG
            }

__version__ = '1.1.0'

#---------------------------------------------------------------------------

_defaultLogOutput = sys.stderr

def setDefaultLogOutput(fileLikeObj):
    '''
    Change the default Logger output object used for newly created Loggers.
    '''
    rv = _defaultLogOutput
    _defaultLogOutput = fileLikeObj
    return rv

#---------------------------------------------------------------------------

class Logger:
    '''
    Basic logging class, can send output to any file-like object, but
    defaults to sys.stderr.  Use like this:

    log = Logger("Module or function name")
    log.msg(INFO, "This is some message text")
    log.msg(WARNING, "Here is one with args:  x = %d, y = %d", x, y)
    '''
    def __init__(self, name='', logLevel=INFO):
        assert logLevel>=DEBUG and logLevel<=LOG
        self.name = name
        self.logLevel = logLevel
        self.output = sys.stderr

    def setLogLevel(self, level):
        assert level>=DEBUG and level<=LOG
        rv = self.logLevel
        self.logLevel = level
        return rv

    def setOutputHandler(self, fileLikeObj):
        rv = self.output
        self.output = fileLikeObj
        return rv

    def msg(self, level, txt, *args, **kw):
        '''
        Output log message, if level permits.
        '''
        assert level>=DEBUG and level<=LOG
        if level >= self.logLevel:
            # build and output the message
            txt = txt % args
            txt = string.joinfields(string.splitfields(txt, "\n"), "\n\t")
            utcsec = time.time()
            timestr = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(utcsec))
            name = self.name
            if not name and kw.has_key('name'):
                name = kw['name']

            theMsg = '%s.%2.2d | %s | %s\n\t%s\n\n' % (
                        timestr,
                        (utcsec - int(utcsec))*100,
                        levelMap[level],
                        name,
                        txt
                        )

            self.output.write(theMsg)
            self.output.flush()


#---------------------------------------------------------------------------

# Create a global instance of the Logger for apps that ony need one.
log = Logger()

#---------------------------------------------------------------------------

def _test():
    log.msg(INFO, 'Hello')
    log.msg(WARNING, 'How the heck are ya?', name='_test')
    log.msg(INFO, 'Some values:\nfoo = %s\nsna = %s', 'bar', 'fu', name='TeSt')


