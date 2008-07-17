#!/usr/bin/env python

import sys, os
refactor_path="/usr/local/lib/python3.0/"

def make2to3(path_from, path_to) :
    cwd = os.getcwd()
    if os.path.exists(path_to) and \
        (os.stat(path_from).st_ctime < os.stat(path_to).st_ctime) :
            return True
    print "Converting", path_to
    if path_from[0] != "/" :
        path_from = cwd+"/"+path_from
    if path_to[0] != "/" :
        path_to = cwd+"/"+path_to

    retcode = 0
    try :
        open(path_to, "w").write(open(path_from, "r").read())
        import subprocess, cStringIO
        process = subprocess.Popen(["2to3", "-w", path_to], cwd=refactor_path)
        retcode = process.wait()
    except :
        os.remove(path_to)
        raise

    os.remove(path_to+".bak")

    if retcode :
        print "ERROR!"

    return not bool(retcode)

print make2to3("setup2.py", "setup3.py")

