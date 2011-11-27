#
# TODO: add line number info
# TODO: add test function names
#

import sys
import re
#from os.path import abspath, dirname
#sys.path.insert(0, dirname(dirname(abspath(__file__))))
#sys.path.insert(0, dirname(dirname(abspath(__file__)))+"/cxx_parse")
from cxxtest_misc import *
import cxx_parser
import string

def cstr( str ):
    '''Convert a string to its C representation'''
    return '"' + string.replace( str, '\\', '\\\\' ) + '"'

def scanInputFiles(files, _options):
    '''Scan all input files for test suites'''
    suites=[]
    for file in files:
        try:
            print "Parsing file "+file,
            sys.stdout.flush()
            parse_info = cxx_parser.parse_cpp(filename=file,optimize=1)
        except IOError, err:
            print " error."
            print str(err)
            continue
        print "done."
        sys.stdout.flush()
        keys = parse_info.index.keys()
        keys.sort()
        tpat = re.compile("[Tt][Ee][Ss][Tt]")
        for key in keys:
            if parse_info.index[key].scope_t == "class" and parse_info.is_baseclass(key,"CxxTest::TestSuite"):
                name=parse_info.index[key].name
                suite = { 'name'         : name,
                        'file'         : file,
                        'cfile'        : cstr(file),
                        'line'         : '0',
                        'generated'    : 0,
                        'object'       : 'suite_%s' % name,
                        'dobject'      : 'suiteDescription_%s' % name,
                        'tlist'        : 'Tests_%s' % name,
                        'tests'        : [],
                        'lines'        : [] }
                for tname in parse_info.get_functions(key,quiet=True):
                    if tname.startswith('createSuite'):
                        # Indicate that we're using a dynamically generated test suite
                        suite['create'] = '0' # (unknown line)
                    if tname.startswith('destroySuite'):
                        # Indicate that we're using a dynamically generated test suite
                        suite['destroy'] = '0' # (unknown line)
                    if not tpat.match(tname):
                        # Skip non-test methods
                        continue
                    test = { 'name'   : tname,
                        'suite'  : suite,
                        'class'  : 'TestDescription_%s_%s' % (suite['name'], tname),
                        'object' : 'testDescription_%s_%s' % (suite['name'], tname),
                        'line'   : '0',
                        }
                    suite['tests'].append(test)
                suites.append(suite)

    #
    # WEH: see if it really makes sense to use parse information to
    # initialize this data.  I don't think so...
    #
    if not _options.noStandardLibrary:
        _options.haveStandardLibrary=1
    if not _options.noExceptionHandling:
        _options.haveExceptionHandling=1

    #print "INFO\n"
    #for suite in suites:
        #for key in suite:
            #print key,suite[key]
        #print ""

    if not _options.root:
        ntests = 0
        #print suites
        for suite in suites:
            ntests += len(suite['tests'])
        if ntests == 0:
            abort( 'No tests defined' )
    #
    return [_options, suites]

