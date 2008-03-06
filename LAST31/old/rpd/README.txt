BSD DB 1.2.0 Module
README.txt
12-July-1999
robin@alldunn.com
----------------------------------------------------------------------------

Enclosed is version 1.2 of my BSD DB family of modules.  So what is it?  It is
a Python extension and wrapper module for the DB library available from
http://www.sleepycat.com/db/.

The only changes from 1.1.x are those needed to be compatible with
version 2.7.5 of BerkeleyDB.

Installation
============

1. If installing a prebuilt version of this package, jump to number 7 below.

2. To build the dbc extension module, go to the TCS/bsddb directory and
unzip the src.zip file.  Be sure to use the appropriate flag (-a ?) to convert
the text files to the proper line-termination.

3. You will need to have already installed version 2.7.5 of the BSD DB
library.  Check the path in Setup.in to be sure it is where you
libdb.a is located.

4. Execute "make -f Makefile.pre.in boot" to build the Makefile to match your
Python installation.

5. Run "make" to build your dbc module as a shared library.

6. Run "make superclean" to cleanup all the stuff you don't need anymore.

7. Move or link the TCS directory to somewhere on the PYTHONPATH. TCS is the
top-level package. If you have other packages from TCS you will need to merge
the contents of TCS with your existing package directory.   Move the dbSS.py
script to somewhere on the PATH for easy startup of the ShelveServer.

8. Testing...  (Sorry, the standard test scripts aren't part of the package
yet.  Maybe next release.)

Notes
=====

There has been quite a bit of testing of this module using BTREE and HASH
files on Linux and SCO, so I am reasonably confident that all Unix versions
are stable and work as advertised.  I have also used this module in an
environment where multiple long-running processes are acessing the database at
the same time, (and at a fairly high load.)  There have been no conflicts or
corruption at all. Simply use the db.appinit function and pass a value for the
flags argument of db.DB_CREATE|db.DB_INIT_LOCK|db.DB_INIT_MPOOL and it works
like magic!  (Well, okay...  I have had some deadlock issues, but running the
db_deadlock deamon from the DB library usually did the trick.)

I have done no testing with RECNO files, so I am reasnonably sure that there
are probably several bugs lurking there.  I don't have a need for RECNO files
myself, does anybody want to use them?  If so, let me know how it goes and
I'll work on fixing the bugs.


For information on how to use the core TCS.bsddb.db module, please see
TCS/bsddb/db.txt. The other modules are introduced here:

TCS.bsddb.dbShelve:
    This module implements a persistent, dictionary-like object that can store
    nearly any Python object using pickles.  To use it simply do something
    like the following:

        from TCS.bsddb import dbShelve
        d = dbShelve.open('shelf.db')

    and then d can be used as a dictionary whose keys and values are stored
    and retrieved transparently from a file named shelf.db.  The only
    restrictions are that the keys must be strings or convertable to an
    appropriate string using str() and that the values must be "picklable."

    Additionally, the dbShelve objects have traversal methods like first() and
    next().  See the module source for details.


TCS.bsddb.dbShelveServer
TCS.bsddb.dbShelveClient:
    dbShelveServer is a standalone server application used for dishing up
    access to dbShelve files to processes residing on other boxes, (or the
    same box, I don't care, but with DB's excellent multi-process
    capabilities, there really is no reason to use a server for same-box
    access...)  TCS.bsddb.dbShelveClient is the client-side support
    module for the ShelveServer.

    Using the ShelveServer is simple.  There are default values for all the
    necessary command-line arguments on the server and for the open function
    on the client-side.  This allows easy use as well as easy customization of
    the communication parameters when needed.  For example, if the
    dbShelveServer is running on a machine named sandbox, access from the
    client is just this simple:

        from TCS.bsddb import dbShelveClient

        s = dbShelveClient.open('test.db', host='sandbox')
        print s.keys()
        s['spam'] = 'eggs ' * 50 # if you are really hungry!
        print s['spam']
        s.close()


Have fun and keep an eye on http://starship.skyport.net/robind/python/ for
updates.

----------------------------------------------------------------------------




