#!/usr/bin/env python

import sys
if sys.version_info[0] == 2 :
  import test2 as test
else :  # >= Python 3.0
  import test3 as test

if __name__ == "__main__":
    test.process_args()

