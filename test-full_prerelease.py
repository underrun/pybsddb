#!/usr/bin/env python

"""
This program checks all the matrix formed by
several Python and BerkeleyDB versions.

This code is only intented to be used by the
maintainer, just before a pybsddb release, to
verify compatibility and regresions. It contains
local details only applicable to maintainer. If
you try it as is, it would fail.
"""

def do_matrix_check() :
  python_versions=("2.3","2.4","2.5")
  berkeleydb_versions=("4.0","4.1","4.2","4.3","4.4","4.5","4.6")

  import subprocess

  for py in python_versions :
    for bdb in berkeleydb_versions :
      print
      print "*** Testing bindings for Python %s and BerkeleyDB %s" %(py,bdb)
      ret=subprocess.call(["/usr/local/bin/python"+py,"setup.py", "-q", \
                       "--berkeley-db=/usr/local/BerkeleyDB."+bdb,"build", "-f"])
      if ret :
        print
        print ">>> Testsuite skipped"
        print
      else :
        subprocess.call(["/usr/local/bin/python"+py,"test.py","-p"])

if __name__=="__main__" :
  print __doc__
  do_matrix_check()
