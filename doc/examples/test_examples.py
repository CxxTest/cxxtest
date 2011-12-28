# Imports
import pyutilib.th as unittest
import glob
import os
from os.path import dirname, abspath, basename
import sys

currdir = dirname(abspath(__file__))+os.sep
datadir = currdir

def filter(line):
    return 'Running' in line or "IGNORE" in line

# Declare an empty TestCase class
class Test(unittest.TestCase): pass

if not sys.platform.startswith('win'):
    # Find all *.sh files, and use them to define baseline tests
    for file in glob.glob(datadir+'*.sh'):
        bname = basename(file)
        name=bname.split('.')[0]
        if os.path.exists(datadir+name+'.txt'):
            Test.add_baseline_test(cwd=datadir, cmd=file, baseline=datadir+name+'.txt', name=name, filter=filter)

# Execute the tests
if __name__ == '__main__':
    unittest.main()
