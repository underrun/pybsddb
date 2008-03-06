import os
import sys
# distutils is included with python 1.6 and later, go grab a copy if you use python 1.5.2.
try:
    from distutils.core import setup, Extension
except ImportError:
   raise SystemExit, "You need to install the distutils package from python.org"

if os.environ.has_key('BERKELEYDB_DIR'):
    bdbdir = os.environ['BERKELEYDB_DIR']
    if sys.platform == 'win32' :
        if not ( os.path.isdir(bdbdir) and
                 os.path.isdir(os.path.join(bdbdir, 'build_win32'))
               ):
            raise SystemExit, "Your BERKELEYDB_DIR environment variable is incorrect."
        include_dirs = [os.path.join(sys.prefix, 'PC'), os.path.join(bdbdir, 'build_win32')]
        lib_dirs = [os.path.join(sys.prefix, 'PCbuild'), os.path.join(bdbdir, r'build_win32\Release')]
        libraries = ['libdb31']
    else:
        if not ( os.path.isdir(bdbdir) and
                 os.path.isdir(os.path.join(bdbdir, 'lib')) and
                 os.path.isdir(os.path.join(bdbdir, 'include'))
               ):
            raise SystemExit, "Your BERKELEYDB_DIR environment variable is incorrect."
        include_dirs = [os.path.join(bdbdir, 'include')]
        lib_dirs = [os.path.join(bdbdir, 'lib')]
        libraries = ['db']
else:
    raise SystemExit, "Your BERKELEYDB_DIR environment variable must be set."

setup ( name = "py-bsddb3",
        version = "2.2.3",
        author = "Gregory P. Smith  --  Autonomous Zone Industries",
        author_email = "greg@users.sourceforge.net",
        url = "http://electricrain.com/greg/python/bsddb3/",
        ext_modules = [
            Extension(
                "dbc",
                # NOTE: we could change this to "db.i" if distutils properly supports SWIG but
                # that would cause SWIG to be required to build; instead we distribute db_wrap.c.
                ["db_wrap.c"],
                # The BERKELEYDB_DIR environment variable is required
                include_dirs=include_dirs,
                library_dirs=lib_dirs,
                libraries=libraries,
            )
        ],
        packages = ["bsddb3"],
        package_dir = {"bsddb3": "."},  # the current directory contains the bsddb3 package
      )

