#!/usr/bin/env python
#----------------------------------------------------------------------
# Setup script for the bsddb3 package

import sys, os, string
from distutils.core     import setup, Extension
from distutils.dep_util import newer

VERSION = "3.0b3"

#----------------------------------------------------------------------

debug = '--debug' in sys.argv or '-g' in sys.argv

lflags_arg = []

libdirs = []
incdirs = []

if os.name == 'posix':
    # Allow setting the DB dir and additional link flags either in
    # the environment or on the command line.
    # First check the environment...
    BERKELEYDB_DIR = os.environ.get('BERKELEYDB_DIR', '')
    LFLAGS = os.environ.get('LFLAGS', [])
    LIBS = os.environ.get('LIBS', [])

    # ...then the command line.
    # Handle --berkeley-db=[PATH] and --lflags=[FLAGS]
    args = sys.argv[:]
    for arg in args:
        if string.find(arg, '--berkeley-db=') == 0:
            BERKELEYDB_DIR = string.split(arg, '=')[1]
            sys.argv.remove(arg)
        elif string.find(arg, '--lflags=') == 0:
            LFLAGS = string.split(string.split(arg, '=')[1])
            sys.argv.remove(arg)
        elif string.find(arg, '--libs=') == 0:
            LIBS = string.split(string.split(arg, '=')[1])
            sys.argv.remove(arg)

    if LFLAGS or LIBS:
        lflags_arg = LFLAGS + LIBS

    # If we were not told where it is, go looking for it.
    if not BERKELEYDB_DIR:
        for dir in ('/usr', '/usr/local/'):

            for version in ('', '3.1'):  # , '3.2'):  (soon)
                instdir = os.path.join(dir, "BerkeleyDB"+version)
                if os.path.exists(instdir):
                    BERKELEYDB_DIR = instdir
                    print "Found BerkeleyDB installation at " + instdir
                    break

            incdirs.append(os.path.join(dir, "include"))
            if os.path.exists(incdirs[-1] + '/db3'):
                BERKELEYDB_DIR = dir
                print "Found db3 header files at " + incdirs[-1]
                break


    if not BERKELEYDB_DIR:
        print "Can't find a local db3 installation."
        sys.exit(1)

    # figure out from the base setting where the lib and .h are
    incdirs.append(os.path.join(BERKELEYDB_DIR, 'include'))
    libdirs.append(os.path.join(BERKELEYDB_DIR, 'lib'))
    if not '-ldb' in LIBS:
        libname = ['db']
    else:
        libname = []
    utils = []


    # Test if the old bsddb is built-in
    static = 0
    try:
        import bsddb
        if string.find(str(bsddb), 'built-in') >= 0:
            static = 1
    except ImportError:
        pass

    # On Un*x, double check that no other built-in module pulls libdb in as a
    # side-effect.  TBD: how/what to do on other platforms?
    import os
    fp = os.popen('ldd %s 2>&1' % sys.executable)
    results = fp.read()
    status = fp.close()
    if not status and string.find(results, 'libdb.') >= 0:
        static = 1

    if static:
        print """\
\aWARNING:
\tIt appears that the old bsddb module is staticly linked in the
\tPython executable.  This will cause various random problems for
\tbsddb3, up to and including segfaults.  Please rebuild your
\tPython either with bsddb disabled, or with it built as a shared
\tdynamic extension.  Watch out for other modules (e.g. dbm) that create
\tdependencies in the python executable to libdb as a side effect."""
        st = raw_input("Build anyway? (yes/[no]) ")
        if st != "yes":
            sys.exit(1)


elif os.name == 'nt':

    # The default build of Berkeley DB for windows just leaves
    # everything in the build dirs in the db source tree.  That means
    # that we either have to hunt around to find it, (which would be
    # even more difficult than the mess above for Unix...) or we make
    # the builder specify everything here.  Compounding the problem is
    # version numbers in default path names, and different library
    # names for debug/release or dll/static.
    #
    # the default is to expect BerkeleyDB to be in the ./db directory;
    # Alternatively you can set the BERKELEYDB_DIR environment variable
    # or specify --berkeley-db=[PATH] on the command line.

    BERKELEYDB_DIR = os.environ.get('BERKELEYDB_DIR', 'db/')
    # ...then the command line.
    # Handle --berkeley-db=[PATH]
    args = sys.argv[:]
    for arg in args:
        if string.find(arg, '--berkeley-db=') == 0:
            BERKELEYDB_DIR = string.split(arg, '=')[1]
            sys.argv.remove(arg)

    incdirs.append(os.path.join(BERKELEYDB_DIR, 'build_win32'))
    incdirs.append(os.path.join(BERKELEYDB_DIR, 'include'))
    libdirs.append(os.path.join(BERKELEYDB_DIR, r'lib'))
    if debug:
        libdirs.append(os.path.join(BERKELEYDB_DIR, r'build_win32\Debug'))
        libname = ['libdb31sd']     # Debug, static
    else:
        libdirs.append(os.path.join(BERKELEYDB_DIR, r'build_win32\Release'))
        libname = ['libdb31s']      # Release, static
    utils = [("bsddb3/utils",
              [os.path.join(BERKELEYDB_DIR, "bin/db_archive.exe"),
               os.path.join(BERKELEYDB_DIR, "bin/db_checkpoint.exe"),
               os.path.join(BERKELEYDB_DIR, "bin/db_deadlock.exe"),
               os.path.join(BERKELEYDB_DIR, "bin/db_dump.exe"),
               os.path.join(BERKELEYDB_DIR, "bin/db_load.exe"),
               os.path.join(BERKELEYDB_DIR, "bin/db_printlog.exe"),
               os.path.join(BERKELEYDB_DIR, "bin/db_recover.exe"),
               os.path.join(BERKELEYDB_DIR, "bin/db_stat.exe"),
               os.path.join(BERKELEYDB_DIR, "bin/db_upgrade.exe"),
               os.path.join(BERKELEYDB_DIR, "bin/db_verify.exe"),
               os.path.join(BERKELEYDB_DIR, "bin/libdb31.dll"),
               ])]


# Update the version .h file if this file is newer
if newer('setup.py', 'src/version.h'):
    open('src/version.h', 'w').write('#define PY_BSDDB_VERSION "%s"\n' % VERSION)


# do the actual build, install, whatever...
setup(name = 'bsddb3',
      version = VERSION,
      description = 'Python interface for BerkeleyDB 3.1.x',
      long_description = """\
This module provides a nearly complete wrapping
of the Sleepycat C API for the Database
Environment, Database, Cursor, and Transaction
objects, and each of these is exposed as a Python
Type in the bsddb3.db module.  The databse objects
can use various access methods: btree, hash, recno,
and queue.  For the first time all of these are
fully supported in the Python wrappers.  Please see
the documents in the docs directory of the source
distribution or at the website for more details on
the types and methods provided.""",

      author = 'Robin Dunn',
      author_email = 'robin@alldunn.com',
      url = 'http://PyBSDDB.sourceforge.net',

      packages = ['bsddb3'],
      ext_modules = [Extension('bsddb3._db',
                               sources = ['src/_db.c'],
                               include_dirs = incdirs,
                               library_dirs = libdirs,
                               libraries = libname,
                               extra_link_args = lflags_arg,
                               )],
      data_files = utils,
      )
