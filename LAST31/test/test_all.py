"""
Run all test cases.
"""

import sys
import unittest

verbose = 1
if len(sys.argv) > 1 and sys.argv[1] == 'silent':
    verbose = 0



def suite():
    test_modules = [ 'test_compat',
                     'test_basics',
                     'test_misc',
                     'test_dbobj',
                     'test_recno',
                     'test_queue',
                     'test_get_none',
                     'test_dbshelve',
                     'test_dbtables',
                     'test_thread',
                     'test_lock',
                   ]

    alltests = unittest.TestSuite()
    for name in test_modules:
        module = __import__(name)
        alltests.addTest(module.suite())
    return alltests



if __name__ == '__main__':
    if not unittest.TextTestRunner().run(suite()).wasSuccessful():
        sys.exit(1)

