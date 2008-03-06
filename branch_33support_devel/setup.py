#!/usr/bin/env python
#----------------------------------------------------------------------
# Setup script for the bsddb3 package

import sys, os, string, re
from distutils.core     import setup, Extension
from distutils.dep_util import newer

VERSION = "3.3a1"

#----------------------------------------------------------------------

debug = '--debug' in sys.argv or '-g' in sys.argv

lflags_arg = []


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
    incdir = libdir = None
    if not BERKELEYDB_DIR:
        for dir in ('/usr', '/usr/local/'):

            for version in ('', '.3.3', '.3.2', '.3.1'):
                instdir = os.path.join(dir, "BerkeleyDB"+version)
                if os.path.exists(instdir):
                    BERKELEYDB_DIR = instdir
                    print "Found BerkeleyDB installation at " + instdir
                    break

            incdir = os.path.join(dir, "include/db3")
            if os.path.exists(incdir):
                libdir = os.path.join(dir, "lib")
                print "Found db3 header files at " + incdir
                break
            else:
                incdir = None


    if not BERKELEYDB_DIR and not incdir and not libdir:
        print "Can't find a local db3 installation."
        sys.exit(1)

    # figure out from the base setting where the lib and .h are
    if not incdir: incdir = os.path.join(BERKELEYDB_DIR, 'include')
    if not libdir: libdir = os.path.join(BERKELEYDB_DIR, 'lib')
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
    # So to make things easier, I'm just going to exepect that the DB stuff
    # has been moved to the ./db directory.  There's an updatedb.bat file to
    # help.
    #
    # You'll need to edit the project file that comes with Berkeley DB so it
    # uses "Multithreaded DLL" and "Debug Multithreaded DLL"  (/MD and /MDd)
    # settings for the run-time library.

    incdir = 'db/include'
    libdir = 'db/lib'

    # read db.h to figure out what version of Berkeley DB this is
    ver = None
    db_h_lines = open(os.path.join(incdir, 'db.h'), 'r').readlines()
    db_ver_re = re.compile(r'^#define\s+DB_VERSION_STRING\s.*Berkeley DB (\d+\.\d+).*')
    for line in db_h_lines:
        match = db_ver_re.match(line)
        if not match:
            continue
        fullverstr = match.group(1)
        ver = fullverstr[0] + fullverstr[2]   # 31 == 3.1, 32 == 3.2, etc.
    assert ver in ('31', '32', '33'), ("pybsddb untested with this Berkeley DB version", ver)
    print 'Detected berkeleydb version', ver, 'from db.h'

    if debug:
        libname = ['libdb%ssd' % ver]     # Debug, static
    else:
        libname = ['libdb%ss' % ver]      # Release, static
    utils = [("bsddb3/utils",
              ["db/bin/db_archive.exe",
               "db/bin/db_checkpoint.exe",
               "db/bin/db_deadlock.exe",
               "db/bin/db_dump.exe",
               "db/bin/db_load.exe",
               "db/bin/db_printlog.exe",
               "db/bin/db_recover.exe",
               "db/bin/db_stat.exe",
               "db/bin/db_upgrade.exe",
               "db/bin/db_verify.exe",
               "db/bin/libdb%s.dll" % ver,
               ])]


# Update the version .h file if this file is newer
if newer('setup.py', 'src/version.h'):
    open('src/version.h', 'w').write('#define PY_BSDDB_VERSION "%s"\n' % VERSION)


# do the actual build, install, whatever...
setup(name = 'bsddb3',
      version = VERSION,
      description = 'Python interface for BerkeleyDB 3.x',
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
                               include_dirs = [ incdir ],
                               library_dirs = [ libdir ],
                               libraries = libname,
                               extra_link_args = lflags_arg,
                               )],
      data_files = utils,
      )
