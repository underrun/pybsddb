README.txt
bsddb3.db v3.0b3
http://pybsddb.sourceforge.net/
February 21, 2001
--------------------------------------


Here is yet another BerkeleyDB wrapper module for Python.  This one is
different from the ones that Gregory P. Smith <greg@electricrain.com>
and I have done in the past in that it doesn't use SWIG.  This one is
completely hand-crafted, and there are no "shadow classes" or other
SWIG related overhead.

This module provides a nearly complete wrapping of the Sleepycat C API
for the Database Environment, Database, Cursor, and Transaction
objects, and each of these is exposed as a Python Type in the
bsddb3.db module.  The database objects can use different access
methods, btree, hash, recno, and queue.  For the first time all of
these are fully supported in the Python wrappers.  Please see the
documents in the docs directory for more details on the types and
methods provided.

There is also a collection of test cases in the test directory that
can be used to validate the modules, as well as giving an idea of how
to use bsddb3.db.

Thanks to The Written Word (http://thewrittenword.com/), bsddb3 is
known to pass its unit tests on these platforms:

     HP-UX 10.20, 11.00
     Tru64 UNIX 4.0D, 5.0
     IRIX 6.2, 6.5
     Solaris 2.5.1, 2.6, 7, 8

In addition I've run it on a few varieties of Linux and of course on
Win32.



Installation
------------

If you are on a Win32 system then you can just get the binary
installer and run it and then you'll be all set.  If you want to build
it yourself, you can follow the directions below, but see the comments
in setup.py first.

If you are on a Unix/Linux system then keep reading...

The Python Distutils are used to build and install bsddb3.db, so it is
fairly simple to get things ready to go.

1. First, make sure that you have Berkeley DB 3.1.x (I'm using 3.1.17
   currently) and that it is built and installed.  Setup.py will
   detect a db3 or BerkeleyDB directory under either /usr or
   /usr/local; this will catch installations from RPMs and most hand
   installations under Unix.  If setup.py can't find your libdb then
   you can give it a hint either in the environment or on the command
   line by specifying the directory containing the include and lib
   directory.  For example:

	    --berkeley-db=/stuff/BerkeleyDB.3.1


   If your Berkeley DB was built as a shared library, and if that
   shared library is not on the runtime load path, then you can
   specify the additional linker flags needed to find the shared
   library on the command line as well.  For example:

	   --lflags="-Xlinker -rpath -Xlinker /stuff/BerkeleyDB.3.1/lib"

   or perhaps just

           --lflags="-R /stuff/BerkeleyDB.3.1/lib"

   Check your compiler and linker documentation to be sure.

   It is also possible to specify linking against a different library
   with the --libs switch:

           --libs="-ldb3"
           --libs="-ldb3 -lnsl"



   NOTE:  My recommendation is to not rely on pre-built versions of
   BerkeleyDB since on some systems there can be several versions
   installed and it's difficult to tell which you are getting.
   Instead get the sources and build/install it yourself as a static
   library and let setup.py find it in /usr/local.  It's not such a
   big library that you have to worry about wasting space by not
   dynamically linking and doing it this way will possibly save you
   some gray hairs.



2. From the main bsddb3 distribution directory run this command, (plus
   any extra flags needed as discussed above):

	python setup.py build_ext --inplace

   If your Python was built with the old bsddb module built-in
   (statically linked) then the setup script will complain and you'll
   have to type "yes" to build anything.  Please see the note below
   about remedying this.


3. To run the test suite change into the test directory and run this
   command, (assuming your shell is bash or compatible):

	export PYTHONPATH=..
	python test_all.py silent

   If you would like to see some verbose output from the tests simply
   leave off the "silent" flag.  You can also run only the tests in a
   particular test module by themselves.  For example:

	python test_lock.py


4. To install the extension module and the Python modules in the
   bsddb3 package, change back to the root distribution directory and
   run this command as the root user:

	python setup.py install


That's it!




Rebuilding Python w/o bsddb
---------------------------

If the old bsddb is linked staticly with Python all kinds of strange
problems can happen when you try to use bsddb3.  Everything from
seg-faults, to getting strange errors on every test, to working
perfectly on some tests, but locking up the process on others.  How
strange can it get?  Try this:

    python -c "from bsddb3.db import *;print version(), DB_VERSION_STRING"

On one machine I got this output:

    (3, 1, 14) Sleepycat Software: Berkeley DB 3.1.17: (July 31, 2000)

Notice the different version numbers?  One set is coming from the DB
library, the other from a macro in db.h so it is actually coming from
my _db.c.  The strange part is that bsddb3 was staticly linked with
3.1.17, but it was still calling functions in the 3.1.14 version
linked with Python.

The best way (only way?) to fix this is to get the old bsddb extension
out of the Python executable.  If the old bsddb is a dynamic extension
module loaded from a shared library, then everything is peachy and
bsddb3 works perfectly.  To do this, edit Modules/Setup.config in the
Python 2.0 distribution and remove the # from in front of *shared*,
then recompile and reinstall Python.  If you just want to remove the
old bsddb entirely, just comment out the following line starting with
bsddb, and then rebuild and install Python.


-- Robin
robin@alldunn.com









