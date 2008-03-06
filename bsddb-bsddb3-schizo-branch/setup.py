#!/usr/bin/env python
#----------------------------------------------------------------------
# Setup script for the bsddb3 package

import os
import re
import sys
import glob
from distutils.core import setup, Extension
from distutils.dep_util import newer

VERSION = "4.1.2"

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
        if arg.startswith('--berkeley-db='):
            BERKELEYDB_DIR = arg.split('=')[1]
            sys.argv.remove(arg)
        elif arg.startswith('--lflags='):
            LFLAGS = arg.split('=')[1].split()
            sys.argv.remove(arg)
        elif arg.startswith('--libs='):
            LIBS = arg.split('=')[1].split()
            sys.argv.remove(arg)

    if LFLAGS or LIBS:
        lflags_arg = LFLAGS + LIBS

    # If we were not told where it is, go looking for it.
    incdir = libdir = None
    if not BERKELEYDB_DIR:
        for dir in ('/usr/local', '/usr'):
            for version in ('', '.4.1', '.4.0', '.3.3', '.3.2', '.3.1'):
                instdir = os.path.join(dir, "BerkeleyDB"+version)
                if os.path.exists(instdir):
                    BERKELEYDB_DIR = instdir
                    print "Found BerkeleyDB installation at " + instdir
                    break

            incdir = os.path.join(instdir, "include/db3")
            if os.path.exists(incdir):
                libdir = os.path.join(dir, "lib")
                print "Found db3 header files at " + incdir
                break
            else:
                incdir = None


    if not BERKELEYDB_DIR and not incdir and not libdir:
        print "Can't find a local BerkeleyDB installation."
        print "(suggestion: try the --berkeley-db=/path/to/bsddb option)"
        sys.exit(1)

    # figure out from the base setting where the lib and .h are
    if not incdir:
        incdir = os.path.join(BERKELEYDB_DIR, 'include')
    if not libdir:
        libdir = os.path.join(BERKELEYDB_DIR, 'lib')
    if not '-ldb' in LIBS:
        libname = ['db']
    else:
        libname = []
    utils = []

    # Test if the old bsddb is built-in
    static = 0
    try:
        import bsddb
        if str(bsddb).find('built-in') >= 0:
            static = 1
    except ImportError:
        pass

    # On Un*x, double check that no other built-in module pulls libdb in as a
    # side-effect.  TBD: how/what to do on other platforms?
    fp = os.popen('ldd %s 2>&1' % sys.executable)
    results = fp.read()
    status = fp.close()
    if not status and results.find('libdb.') >= 0:
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
    # settings as appropriate to build .lib file (the db_static project).

    incdir = 'db/include'
    libdir = 'db/lib'

    # read db.h to figure out what version of Berkeley DB this is
    ver = None
    db_h_lines = open(os.path.join(incdir, 'db.h'), 'r').readlines()
    db_ver_re = re.compile(
        r'^#define\s+DB_VERSION_STRING\s.*Berkeley DB (\d+\.\d+).*')
    for line in db_h_lines:
        match = db_ver_re.match(line)
        if not match:
            continue
        fullverstr = match.group(1)
        ver = fullverstr[0] + fullverstr[2]   # 31 == 3.1, 32 == 3.2, etc.
    assert ver in ('31', '32', '33', '40', '41'), (
        "pybsddb untested with this Berkeley DB version", ver)
    print 'Detected BerkeleyDB version', ver, 'from db.h'

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
               ]),
             ("bsddb3/test", glob.glob("test/*.py"))
             ]


# do the actual build, install, whatever...
setup(name = 'bsddb3',
      version = VERSION,
      description = 'Python interface for BerkeleyDB 3.1 thru 4.1',
      long_description = """\
This module provides a nearly complete wrapping
of the Sleepycat C API for the Database
Environment, Database, Cursor, and Transaction
objects, and each of these is exposed as a Python
type in the bsddb3.db module.  The databse objects
can use various access methods: btree, hash, recno,
and queue.  For the first time all of these are
fully supported in the Python wrappers.  Please see
the documents in the docs directory of the source
distribution or at the website for more details on
the types and methods provided.""",

      author = 'Robin Dunn, Gregory P. Smith, Andrew Kuchling, Barry Warsaw',
      author_email = 'pybsddb-users@lists.sourceforge.net',
      url = 'http://pybsddb.sf.net/',

      packages = ['bsddb3', 'bsddb3/tests'],
      package_dir = {'bsddb3': 'bsddb',
                     'bsddb3/tests': 'bsddb/test'},
      ext_modules = [Extension('bsddb3._bsddb',
                               sources = ['extsrc/_bsddb.c'],
                               include_dirs = [ incdir ],
                               library_dirs = [ libdir ],
                               libraries = libname,
                               extra_link_args = lflags_arg,
                               )],
      data_files = utils,
      )
