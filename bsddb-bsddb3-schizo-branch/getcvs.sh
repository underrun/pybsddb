#! /bin/sh
#
# Use this script to get a copy of the Python cvs source files.  If
# you are not a Python SF project developer, provide the `anon'
# argument and an anonymous checkout will be done.

root="cvs.python.sourceforge.net:/cvsroot/python"
server=":ext:"
login="no"

anon=${1:-"no"}
if [ "$anon" = "anon" ]; then
    server=:pserver:anonymous@
    login="yes"
fi

CVSROOT=${server}${root}

if [ "$login" = "yes" ]; then
    echo "Just hit return when prompted for the CVS password"
    cvs -d${CVSROOT} login
fi

# First, check out the Python modules
cvs -d${CVSROOT} co -d bsddb python/dist/src/Lib/bsddb

# Now check out the extension
cvs -d${CVSROOT} co -d extsrc python/dist/src/Modules/_bsddb.c
