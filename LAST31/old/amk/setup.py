
# Setup script for the BSDDB3 package

import os
from distutils.core import setup, Extension

BERKELEYDB_DIR="/usr/local/BerkeleyDB.3.1"

dbext = Extension('bsddb3._bsddb',
                  include_dirs = [ os.path.join(BERKELEYDB_DIR, 'include') ],
                  library_dirs = [ os.path.join(BERKELEYDB_DIR, 'lib') ],
                  libraries = ['db'],
                  sources = ['_bsddb.c']
                  )

setup (name = "BerkeleyDB",
       version = "2.9.2",
       description = "Python interface for BerkeleyDB 3.1.x",
       author = "XXX",
       author_email = "XXX",
       url = "XXX",

       package_dir = {'bsddb3':'.'},
       packages = ['bsddb3'],
       ext_modules = [dbext] )


