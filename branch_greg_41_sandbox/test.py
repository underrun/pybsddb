##############################################################################
#
# Copyright (c) 2001, 2002 Zope Corporation and Contributors.
# All Rights Reserved.
# 
# This software is subject to the provisions of the Zope Public License,
# Version 2.0 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
# 
##############################################################################
"""
test.py [-bCdgGLvv] [modfilter [testfilter]]

Test harness.

-b  build
    Run "python setup.py -q build" before running tests, where "python"
    is the version of python used to run test.py.  Highly recommended.

-C  use pychecker

-d  debug
    Instead of the normal test harness, run a debug version which
    doesn't catch any exceptions.  This is occasionally handy when the
    unittest code catching the exception doesn't work right.
    Unfortunately, the debug harness doesn't print the name of the
    test, so Use With Care.

-v  verbose
    With one -v, unittest prints a dot (".") for each test run.  With
    -vv, unittest prints the name of each test (for some definition of
    "name" ...).  Witn no -v, unittest is silent until the end of the
    run, except when errors occur.

-L  Loop
    Keep running the selected tests in a loop.  You may experience
    memory leakage.

-g  threshold
    Set the garbage collector generation0 threshold.  This can be used to
    stress memory and gc correctness.  Some crashes are only reproducible when
    the threshold is set to 1 (agressive garbage collection).  Do "-g 0" to
    disable garbage collection altogether.

-G  gc_option
    Set the garbage collection debugging flags.  The argument must be one
    of the DEBUG_ flags defined bythe Python gc module.  Multiple options
    can be specified by using "-G OPTION1 -G OPTION2."

modfilter
testfilter
    Case-sensitive regexps to limit which tests are run, used in search
    (not match) mode.
    In an extension of Python regexp notation, a leading "!" is stripped
    and causes the sense of the remaining regexp to be negated (so "!bc"
    matches any string that does not match "bc", and vice versa).
    By default these act like ".", i.e. nothing is excluded.

    modfilter is applied to a test file's path, starting at "build" and
    including (OS-dependent) path separators.

    testfilter is applied to the (method) name of the unittest methods
    contained in the test files whose paths modfilter matched.

Extreme (yet useful) examples:

    test.py -vvb . "^checkWriteClient$"

    Builds the project silently, then runs unittest in verbose mode on all
    tests whose names are precisely "checkWriteClient".  Useful when
    debugging a specific test.

    test.py -vvb . "!^checkWriteClient$"

    As before, but runs all tests whose names aren't precisely
    "checkWriteClient".  Useful to avoid a specific failing test you don't
    want to deal with just yet.
"""

import gc
import os
import re
import sys
import traceback
import unittest

from distutils.util import get_platform

class ImmediateTestResult(unittest._TextTestResult):

    __super_init = unittest._TextTestResult.__init__

    def __init__(self, *args, **kwarg):
        debug = kwarg.get('debug')
        if debug is not None:
            del kwarg['debug']
        self.__super_init(*args, **kwarg)
        self._debug = debug

    def stopTest(self, test):
        if gc.garbage:
            print test
            print gc.garbage
        
    def _print_traceback(self, msg, err, test, errlist):
        if self.showAll or self.dots:
            self.stream.writeln("\n")

        tb = ''.join(traceback.format_exception(*err))
        self.stream.writeln(msg)
        self.stream.writeln(tb)
        errlist.append((test, tb))

    def addError(self, test, err):
        if self._debug:
            raise err[0], err[1], err[2]
        self._print_traceback("Error in test %s" % test, err,
                              test, self.errors)

    def addFailure(self, test, err):
        if self._debug:
            raise err[0], err[1], err[2]
        self._print_traceback("Failure in test %s" % test, err,
                              test, self.failures)

    def printErrorList(self, flavor, errors):
        for test, err in errors:
            self.stream.writeln(self.separator1)
            self.stream.writeln("%s: %s" % (flavor, self.getDescription(test)))
            self.stream.writeln(self.separator2)
            self.stream.writeln(err)

class ImmediateTestRunner(unittest.TextTestRunner):

    __super_init = unittest.TextTestRunner.__init__

    def __init__(self, **kwarg):
        debug = kwarg.get('debug')
        if debug is not None:
            del kwarg['debug']
        self.__super_init(**kwarg)
        self._debug = debug

    def _makeResult(self):
        return ImmediateTestResult(self.stream, self.descriptions,
                                   self.verbosity, debug=self._debug)

# setup list of directories to put on the path

PLAT_SPEC = "%s-%s" % (get_platform(), sys.version[0:3])

def setup_path():
    DIRS = ["lib.%s" % PLAT_SPEC,
            ]
    for d in DIRS:
        sys.path.insert(0, d)

def match(rx, s):
    if not rx:
        return 1
    if rx[0] == '!':
        return re.search(rx[1:], s) is None
    else:
        return re.search(rx, s) is not None

# Find test files.
# They live under either a lib.PLAT_SPEC or plain "lib" directory.
_sep = re.escape(os.sep)
_pat = "%s(%s|lib)%s" % (_sep, re.escape("lib." + PLAT_SPEC), _sep)
hasgooddir = re.compile(_pat).search
del _sep, _pat

class TestFileFinder:
    def __init__(self):
        self.files = []

    def visit(self, rx, dir, files):
        if dir[-5:] != "tests":
            return
        # ignore tests that aren't in packages
        if not "__init__.py" in files:
            print "not a package", dir
            return
        for file in files:
            if file[:4] == "test" and file[-3:] == ".py":
                path = os.path.join(dir, file)
                if not hasgooddir(path):
                    # built for a different version
                    continue
                if rx is not None:
                    if rx.search(path):
                        self.files.append(path)
                else:
                    self.files.append(path)

def find_tests(srx):
    if srx is not None:
        rx = re.compile(srx)
    else:
        rx = None
    finder = TestFileFinder()
    os.path.walk("build", finder.visit, rx)
    return finder.files

def package_import(modname):
    mod = __import__(modname)
    for part in modname.split(".")[1:]:
        mod = getattr(mod, part)
    return mod

def module_from_path(path):
    """Return the Python package name indiciated by the filesystem path."""

    assert path.endswith('.py')
    path = path[:-3]
    dirs = []
    while path:
        path, end = os.path.split(path)
        dirs.insert(0, end)
    return ".".join(dirs[2:])

def get_suite(file):
    modname = module_from_path(file)
    try:
        mod = package_import(modname)
    except ImportError, err:
        # print traceback
        print "Error importing %s\n%s" % (modname, err)
        if debug:
            raise
        return None
    try:
        suite_func = mod.test_suite
    except AttributeError:
        print "No test_suite() in %s" % file
        return None
    return suite_func()

def filter_testcases(s, rx):
    new = unittest.TestSuite()
    for test in s._tests:
        if isinstance(test, unittest.TestCase):
            name = test.id() # Full test name: package.module.class.method
            name = name[1 + name.rfind('.'):] # extract method name
            if match(rx, name):
                new.addTest(test)
        else:
            filtered = filter_testcases(test, rx)
            if filtered:
                new.addTest(filtered)
    return new

def runner(files, test_filter, debug):
    runner = ImmediateTestRunner(verbosity=VERBOSE, debug=debug)
    suite = unittest.TestSuite()
    for file in files:
        s = get_suite(file)
        if s is not None:
            if test_filter is not None:
                s = filter_testcases(s, test_filter)
            suite.addTest(s)
    r = runner.run(suite)

def remove_stale_bytecode(arg, dirname, names):
    names = map(os.path.normcase, names)
    for name in names:
        if name.endswith(".pyc") or name.endswith(".pyo"):
            srcname = name[:-1]
            if srcname not in names:
                fullname = os.path.join(dirname, name)
                print "Removing stale bytecode file", fullname
                os.unlink(fullname)

def main(module_filter, test_filter):
    os.path.walk(os.curdir, remove_stale_bytecode, None)
    setup_path()
    files = find_tests(module_filter)
    files.sort()

    os.chdir("build") 

    if LOOP:
        while 1:
            runner(files, test_filter, debug)
    else:
        runner(files, test_filter, debug)


def process_args():
    import getopt
    global module_filter
    global test_filter
    global VERBOSE
    global LOOP
    global debug
    global build
    global gcthresh
    global gcdebug

    module_filter = None
    test_filter = None
    VERBOSE = 0
    LOOP = 0
    debug = 0 # Don't collect test results; simply let tests crash
    build = 0
    gcthresh = None
    gcdebug = 0

    try:
        opts, args = getopt.getopt(sys.argv[1:], 'vdLbhCg:G:',
                                   ['help'])
    except getopt.error, msg:
        print msg
        print "Try `python %s -h' for more information." % sys.argv[0]
        sys.exit(2)

    for k, v in opts:
        if k == '-v':
            VERBOSE += 1
        elif k == '-d':
            debug = 1
        elif k == '-L':
            LOOP = 1
        elif k == '-b':
            build = 1
        elif k in ('-h', '--help'):
            print __doc__
            sys.exit(0)
        elif k == '-C':
            if not os.environ.get('PYCHECKER'):
                # only errors, all globals, skip stdlib
                os.environ['PYCHECKER'] = "-e -g -q"
            import pychecker.checker
        elif k == '-g':
            gcthresh = int(v)
        elif k == '-G':
            flag = getattr(gc, v)
            gcdebug |= flag

    if gcthresh is not None:
        if gcthresh == 0:
            gc.disable()
            print "gc disabled"
        else:
            gc.set_threshold(gcthresh)
            print 'gc threshold:', gc.get_threshold()

    if gcdebug:
        gc.set_debug(gcdebug)

    if build:
        cmd = sys.executable + " setup.py -q build"
        if VERBOSE:
            print cmd
        sts = os.system(cmd)
        if sts:
            print "Build failed", hex(sts)
            sys.exit(1)

    if args:
        if len(args) > 1:
            test_filter = args[1]
        module_filter = args[0]
    try:
        bad = main(module_filter, test_filter)
        if bad:
            sys.exit(1)
    except ImportError, err:
        print err
        print sys.path
        raise


if __name__ == "__main__":
    process_args()
