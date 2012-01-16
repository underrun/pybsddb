#!/usr/bin/env python

"""
This program checks all the matrix formed by
several Python and Berkeley DB versions.

This code is only intented to be used by the
maintainer, just before a pybsddb release, to
verify compatibility and regresions. It contains
local details only applicable to maintainer. If
you try it as is, it would fail.
"""

def do_matrix_check() :
  python_versions=("2.4","2.5","2.6","2.7","3.1","3.2")
  berkeleydb_versions=("4.3","4.4","4.5","4.6","4.7","4.8","5.0","5.1","5.2","5.3")

  warning_level=("-Wdefault", "-Werror")[1]
  import subprocess

  for py in python_versions :
    for bdb in berkeleydb_versions :
      print
      print "*** Testing bindings for Python %s and Berkeley DB %s" %(py,bdb)
      extra_params = [warning_level, "-tt"]
      # Extra flags for 3.x
      extra_params += [] if float(py)<=2.999 else ["-bb"]
      # Extra flags for >=2.6
      extra_params += [] if ((float(py)<=2.599) or (float(py)>=2.999)) else ["-3"]
      params = extra_params + ["setup.py", "-q", \
                 "--berkeley-db=/usr/local/BerkeleyDB."+bdb,"build", "-f"]
      params = ["/usr/local/bin/python"+py] + params
      print "EXECUTING:", " ".join(params)
      ret=subprocess.call(params)
      if ret :
        print
        print ">>> Testsuite skipped"
        print
      else :
        params = ["/usr/local/bin/python"+py] + extra_params + ["test.py","-p"]
        print "EXECUTING:", " ".join(params)
        ret = subprocess.call(params)
        if ret :
            import sys
            sys.exit(1)

if __name__=="__main__" :
  print __doc__
  do_matrix_check()
