# CxxTest builder by Gasper Azman
#
# please send bugreports/praise/comments/criticism to
# gasper.azman at gmail.com
#
# This has been somewhat inspired by my previous work here:
# http://www.scons.org/wiki/UnitTests
#
# This builder correctly tracks dependencies and supports just about every
# configuration option for CxxTest that I can think of. It automatically
# defines a target "check" (configurable), so all tests can be run with a
#   scons check
# This will first compile and then run the tests.
#
# The default configuration assumes that cxxtest is installed in the base
# source directory (where SConstruct is), that the cxxtestgen.py is under
# cxxtest/cxxtestgen.py and headers are in cxxtest/cxxtest/. The header
# include path is automatically added to CPPPATH.
#
# This should be in a file called cxxtest.py somewhere in the toolpath.
#
# CHANGELOG:
# 2008-03-29:
#    Fixed a bug introduced in the last version, where the script would fail if
#    CXXFLAGS was never set.
# 2008-03-23:
#    Added CXXTEST_CXXFLAGS_REMOVE
#    Bugfix: if only a single test was specified, scons check would do nothing
#    Bugfix: test would not compile if '#' was not a part of path. Now added
#    automatically.
# 2008-06-22:
#    Bugfix: on windows, the script would not work because windows does not
#    support running scripts without an explicit interpreter invocation
#    (./script.py). 
#    Patch kindly provided by Diego Nieto Cid (dnietoc at gmail dot com)
# 2008-06-25:
#    Bugfix: Diego also provided a patch to his added functionality, so that
#    now not all paths are imported, but just the path required to run the
#    interpreter.
#
# Last changed: 2008-06-25 23:58:40 CEST

from SCons.Script import *
from SCons.Builder import Builder
from os import path

def UnitTest(env, target, source = [], **kwargs):
    cxxflags = ""
    if (type(env["CXXFLAGS"]) == "str"):
        cxxflags = env["CXXFLAGS"]
    cxxflags = kwargs.get("CXXFLAGS", cxxflags)
    for item in env['CXXTEST_CXXFLAGS_REMOVE']:
        cxxflags = cxxflags.replace(item, "")
    kwargs["CXXFLAGS"] = cxxflags;
    test = env.Program(target, source = source, **kwargs)
    env.Alias(env['CXXTEST_TARGET'], test, test[0].abspath)
    env.AlwaysBuild(env['CXXTEST_TARGET'])
    return test

def find_interpreter(script):
    # See if the script ends in pl or py
    if script[len(script)-1] == 'l':
        # Iterate PATH environment variable checking for perl executable
        for i in os.environ['PATH'].split(os.pathsep):
            perl = path.join(i, "perl.exe")
            if path.exists(perl):
                return path.split(perl)
    else:
        # With python is simple, we are already running it
        return path.split(sys.executable)


def generate(env, **kwargs):
    """
    Accepted keyword arguments:
    CXXTEST_DIR     - the directory the cxxtest library is in.
                        Default: #/cxxtest
    CXXTEST         - the path to the cxxtestgen.py or cxxtestgen.pl.
                        Default: CXXTEST_DIR/cxxtestgen.py
    CXXTEST_HEADERS - the directory the cxxtest headers are in.
                        Default: CXXTEST_DIR
    CXXTEST_PRINTER - the printer to use. Default: error-printer
    CXXTEST_OPTS    - other options to pass to cxxtest. Default: ''
    CXXTEST_SUFFIX  - the suffix of the test files. Default: '.t.h'
    CXXTEST_TARGET  - the target to append the tests to. Default: check
    CXXTEST_CXXFLAGS_REMOVE - the flags that cxxtests can't compile with,
                              or give lots of warnings. Will be stripped.
    CXXTEST_RUNNER  - how to run the script? (for windows compability :-)
                        Default:os dependent: POSIX=empty;WINDOWS=(python|perl)
    ... and all others that Program() accepts, like CPPPATH etc.
    """
    env['CXXTEST_DIR'] = kwargs.get('CXXTEST_DIR', '#/cxxtest');
    env['CXXTEST']     = kwargs.get('CXXTEST',
            Dir(env['CXXTEST_DIR']).path + '/cxxtestgen.py');
    # cxxtest runner stuf
    cxxtest_runner = ""
    if os.name == 'nt':
        #Locate the interpreter for cxxtest script
        location, executable = find_interpreter(env['CXXTEST'])
        # Add location to PATH
        env['ENV']['PATH'] += os.pathsep + location
        # Set runner
        cxxtest_runner = executable
    env['CXXTEST_RUNNER']  = kwargs.get('CXXTEST_RUNNER', cxxtest_runner)
    env['CXXTEST_HEADERS'] = kwargs.get('CXXTEST_HEADERS', '$CXXTEST_DIR')
    env['CXXTEST_PRINTER'] = kwargs.get('CXXTEST_PRINTER', 'error-printer');
    env['CXXTEST_OPTS']    = kwargs.get('CXXTEST_OPTS', '');
    env['CXXTEST_SUFFIX']  = kwargs.get('CXXTEST_SUFFIX', '.t.h');
    env['CXXTEST_TARGET']  = kwargs.get('CXXTEST_TARGET', 'check');
    env['CXXTEST_CXXFLAGS_REMOVE'] = Split(
            kwargs.get('CXXTEST_CXXFLAGS_REMOVE',
                ['-pedantic','-Weffc++']
                )
            )

    cxxtest_builder = Builder(
        action = "$CXXTEST_RUNNER $CXXTEST --$CXXTEST_PRINTER $CXXTEST_OPTS -o $TARGET $SOURCE",
        suffix = ".cpp",
        src_suffix = '$CXXTEST_SUFFIX'
        )

    def CxxTest(env, target, source = [], **kwargs):
        """Usage:
        The function is modelled to be called as the Program() call is:
        env.CxxTest('target_name') will build the test from the source
            target_name + env['CXXTEST_SUFFIX'],
        env.CxxTest('target_name', source = 'test_src.t.h') will build the test
            from test_src.t.h source,
        env.CxxTest('target_name, source = ['test_src.t.h', other_srcs]
            builds the test from source[0] and links in other files mentioned in
            sources,
        You may also add additional arguments to the function. In that case, they
        will be passed to the actual Program builder call unmodified. Convenient
        for passing different CPPPATHs and the sort.
        """
        if (source == []):
            source = Split(target + env['CXXTEST_SUFFIX'])
        sources = Split(source)
        sources[0] = env.CxxTestCpp(sources[0])
        env.AppendUnique(CPPPATH = ['$CXXTEST_HEADERS','#'])

        return UnitTest(env, target, source = sources, **kwargs)

    env.Append( BUILDERS = { "CxxTest" : CxxTest, "CxxTestCpp" : cxxtest_builder } )

def exists(env):
    return path.exists(env['CXXTEST'])
