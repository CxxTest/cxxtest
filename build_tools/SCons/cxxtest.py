# coding=UTF-8
#
# == Preamble ==
#
# CxxTest builder by Gasper Azman
#
# Contributors:
# J. Darby Mitchell
# Diego Nieto Cid
# Joe Maruzsevski
# Edmundo López B.
#
# please send bugreports/praise/comments/criticism to
# gasper.azman at gmail.com or the cxxtest mailing list.
#
# This file is maintained as a part of the CxxTest test suite.
# 
# == About ==
#
# This builder correctly tracks dependencies and supports just about every
# configuration option for CxxTest that I can think of. It automatically
# defines a target "check" (configurable), so all tests can be run with a
#  % scons check
# This will first compile and then run the tests.
#
# The default configuration assumes that cxxtest is installed in the base
# source directory (where SConstruct is), that the cxxtestgen.py is under
# cxxtest/cxxtestgen.py and headers are in cxxtest/cxxtest/. The header
# include path is automatically added to CPPPATH. It, however, can also
# recognise that cxxtest is installed system-wide (based on redhat's RPM).
#
# For a list of environment variables and their defaults, see the generate()
# function.
#
# This should be in a file called cxxtest.py somewhere in the scons toolpath.
# (default: #/site_scons/site_tools/)
#
# == Usage: ==
#
# This builder has a variety of different possible usages, so bear with me.
#
# env.CxxTest('target')
# The simplest of them all, it models the Program call. This sees if target.t.h
# is around and passes it through the cxxtestgen.py and compiles it. Might only
# work on unix though, because target can't have a suffix right now.
#
# env.CxxTest(['target.t.h'])
# This compiles target.t.h as in the previous example, but now sees that it is a
# source file. It need not have the same suffix as the env['CXXTEST_SUFFIX']
# variable dictates. The only file provided is taken as the test source file.
#
# env.CxxTest(['test1.t.h','test1_lib.cpp','test1_lib2.cpp','test2.t.h',...])
# You may also specify multiple source files. In this case, the 1st file that
# ends with CXXTEST_SUFFIX (default: .t.h) will be taken as the default test
# file. All others will be run with the --part switch and linked in. All files
# *not* having the right suffix will be passed to the Program call verbatim.
#
# In the last two cases, you may also specify the desired name of the test as
# the 1st argument to the function. This will result in the end executable
# called that. Normal Program builder rules apply.
#
# == Changelog ==
# 2009-02-11: Fixed passing variables via the environment. Added the
#    CXXTEST_CCFLAGS_REMOVE variable. Fixed globbing thanks to a tip provided by
#    Edmundo.
# 2008-09-28: Added the option that #, as understood in pathnames in the rest of
#    SCons, is now also understood here. Minor bugfixes all around.
# 2008-08-30: CXXTEST_RUNNER became CXXTEST_PYTHON, and CXXTEST_PRINTER became
#    CXXTEST_RUNNER because it now governs the argument of the --runner
#    commandline option.
# 2008-08-29: Gašper Ažman added the --root and --part functionality.
#    Documentation above.
# 2008-08-28: Gašper Ažman added CXXTEST_SKIP_ERRORS that makes all tests run no
#    matter whether they fail or succeed. Fixed the issue where CPPPATH would
#    vanish. Fixed bug #40
# 2008-08-25: Gasper Azman and Darby Mitchell (MIT) refactored the tool to
#    set defaults that don't override previously set environment variables, and 
#    automatically search for the cxxtestgen Python script in the path and 
#    project if it isn't specified by the user in the environment or kwargs.
# 2008-08-23: Gasper Azman removed Perl support, since SCons is based on Python
#    and CxxTest has plans to drop the cxxtestgen Perl script in the near future.
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

from SCons.Script import *
from SCons.Builder import Builder
from os import path

# A warning class to notify users of problems
class ToolCxxTestWarning(SCons.Warnings.Warning):
    pass

SCons.Warnings.enableWarningClass(ToolCxxTestWarning)

def accumulateEnvVar(dicts, name, default = []):
    """
    Accumulates the values under key 'name' from the list of dictionaries dict.
    The default value is appended to the end list if 'name' does not exist in
    the dict.
    """
    final = []
    for d in dicts:
        final += Split(d.get(name, default))
    return final

def multiget(dictlist, key, default = None):
    """
    Takes a list of dictionaries as its 1st argument. Checks if the key exists
    in each one and returns the 1st one it finds. If the key is found in no
    dictionaries, the default is returned.
    """
    for dict in dictlist:
        if dict.has_key(key):
            return dict[key]
    else:
        return default

def UnitTest(env, target, source = [], **kwargs):
    """
    Prepares the Program call arguments, calls Program and adds the result to
    the check target.
    """
    # get the c and cxx flags to process.
    ccflags   = Split( multiget([kwargs, env], 'CCFLAGS' ))
    cxxflags  = Split( multiget([kwargs, env], 'CXXFLAGS'))
    # get the removal c and cxx flags
    cxxremove = set( Split( multiget([kwargs, env],'CXXTEST_CXXFLAGS_REMOVE')))
    ccremove  = set( Split( multiget([kwargs, env],'CXXTEST_CCFLAGS_REMOVE' )))
    # remove the required flags
    ccflags   = [item for item in ccflags if item not in ccremove]
    cxxflags  = [item for item in cxxflags if item not in cxxremove]
    # fill the flags into kwargs
    kwargs["CXXFLAGS"] = cxxflags
    kwargs["CCFLAGS"]  = ccflags
    test = env.Program(target, source = source, **kwargs)
    if multiget([kwargs, env], 'CXXTEST_SKIP_ERRORS', False):
        runner = env.Action(test[0].abspath, exitstatfunc=lambda x:0)
    else:
        runner = env.Action(test[0].abspath)
    env.Alias(env['CXXTEST_TARGET'], test, runner)
    env.AlwaysBuild(env['CXXTEST_TARGET'])
    return test

def isValidScriptPath(cxxtestgen):
    """check keyword arg or environment variable locating cxxtestgen.py script"""
       
    if(cxxtestgen and cxxtestgen.endswith('.py') and path.exists(cxxtestgen) ):
        return True
    else:
        SCons.Warnings.warn(ToolCxxTestWarning,
                            "Invalid CXXTEST environment variable specified!")
        return False
    

def findCxxTestGen(env):
    """locate the cxxtestgen script by checking environment, path and project"""
    
    # check the SCons environment...
    # Then, check the OS environment...
    cxxtest = multiget([env, os.environ], 'CXXTEST', None)

    # check for common passing errors and provide diagnostics.
    if isinstance(cxxtest, (list, tuple, dict)):
        SCons.Warnings.warn(
                ToolCxxTestWarning,
                "The CXXTEST variable was specified as a list."
                " This is not supported. Please pass a string."
                )

    if cxxtest:
        try:
            #try getting the absolute path of the file first.
            # Required to expand '#'
            cxxtest = env.File(cxxtest).abspath;
        except TypeError:
            try:
                #maybe only the directory was specified?
                cxxtest = env.File(cxxtest+'/cxxtestgen.py').abspath;
            except TypeError:
                pass
        # If the user specified the location in the environment,
        # make sure it was correct
        if isValidScriptPath(cxxtest):
           return cxxtest
    
    # No valid environment variable found, so...
    # Next, check the path...
    # Next, check the project
    cxxtest = (env.WhereIs('cxxtestgen.py') or 
               env.WhereIs('cxxtestgen.py',
                   path=Dir(path.join('#', 'cxxtest')).abspath)
              )
    
    if cxxtest:
        return cxxtest
    else:
        # If we weren't able to locate the cxxtestgen.py script, complain...
        SCons.Warnings.warn(
                ToolCxxTestWarning,
                "Unable to locate cxxtestgen.py in environment, path or"
                " project!\n"
                "Please set the CXXTEST variable to the path of the"
                " cxxtestgen.py script"
                )
        return None
    

def generate(env, **kwargs):
    """
    Accepted keyword arguments:
    CXXTEST         - the path to the cxxtestgen.py
                        Default: searches SCons environment, OS environment,
                        path and project in that order.
    CXXTEST_RUNNER  - the runner to use.  Default: ErrorPrinter
    CXXTEST_OPTS    - other options to pass to cxxtest.  Default: ''
    CXXTEST_SUFFIX  - the suffix of the test files.  Default: '.t.h'
    CXXTEST_TARGET  - the target to append the tests to.  Default: check
    CXXTEST_CXXFLAGS_REMOVE - the flags that cxxtests can't compile with,
                              or give lots of warnings. Will be stripped.
                              Default: -pedantic -Weffc++
    CXXTEST_CCFLAGS_REMOVE - the same thing as CXXTEST_CXXFLAGS_REMOVE, just for
                            CCFLAGS. Default: same as CXXFLAGS.
    CXXTEST_PYTHON  - the path to the python binary.
                        Default: searches path for python
    CXXTEST_SKIP_ERRORS - set to True to continue running the next test if one
                          test fails. Default: False
    CXXTEST_CPPPATH - If you do not want to clutter your global CPPPATH with the
                        CxxTest header files and other stuff you only need for
                        your tests, this is the variable to set. Behaves as
                        CPPPATH does.
    ... and all others that Program() accepts, like CPPPATH etc.
    """

    print "Loading CxxTest tool..."
    
    #If the user specified the path to CXXTEST, make sure it is correct
    #otherwise, search for and set the default toolpath.
    if (not kwargs.has_key('CXXTEST') or not isValidScriptPath(kwargs['CXXTEST']) ):
        env["CXXTEST"] = findCxxTestGen(env)

    #
    # Expected behaviour: keyword arguments override environment variables;
    # environment variables override default settings.
    #          
    env.SetDefault( CXXTEST_RUNNER  = 'ErrorPrinter'        )
    env.SetDefault( CXXTEST_OPTS    = ''                    )
    env.SetDefault( CXXTEST_SUFFIX  = '.t.h'                )
    env.SetDefault( CXXTEST_TARGET  = 'check'               )
    env.SetDefault( CXXTEST_CPPPATH = ['#']                 )
    env.SetDefault( CXXTEST_PYTHON  = env.WhereIs('python') )
    env.SetDefault( CXXTEST_SKIP_ERRORS = False             )
    env.SetDefault( CXXTEST_CXXFLAGS_REMOVE =
            ['-pedantic','-Weffc++','-pedantic-errors'] )
    env.SetDefault( CXXTEST_CCFLAGS_REMOVE  =
            ['-pedantic','-Weffc++','-pedantic-errors'] )
    
    #Here's where keyword arguments are applied
    apply(env.Replace, (), kwargs)
    
    cxxtest = env['CXXTEST']
    if(cxxtest):
        # Check to see if there is a 'cxxtest' subdirectory in the location where
        # the script was found.  If so, assume that is the header directory, and  
        # therefore the script directory should be included in the CPPPATH
        if(path.exists(path.join(path.dirname(cxxtest), 'cxxtest') ) ):
           # for some reason, setting PATH here doesn't work for me (Gašper)
           env.AppendUnique(CXXTEST_CPPPATH = [path.dirname(cxxtest)] )
        
        #
        # Create the Builder (only if we have a valid cxxtestgen!)
        #
        cxxtest_builder = Builder(
            action =
            [["$CXXTEST_PYTHON",cxxtest,"--runner=$CXXTEST_RUNNER",
                "$CXXTEST_OPTS","$CXXTEST_ROOT_PART","-o","$TARGET","$SOURCE"]],
            suffix = ".cpp",
            src_suffix = '$CXXTEST_SUFFIX'
            )

    def CxxTest(env, target, source = None, **kwargs):
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
        for passing different CPPPATHs and the sort. This function also appends
        CXXTEST_CPPPATH to CPPPATH. It does not clutter the environment's CPPPATH.
        """
        if (source == None):
            suffix = multiget([kwargs, env], 'CXXTEST_SUFFIX', "")
            source = [t + suffix for t in target]
        sources = Flatten(Split(source))
        headers = []
        linkins = []
        for l in sources:
            # check whether this is a file object or a string path
            try:
                s = l.abspath
            except AttributeError:
                s = l

            if s.endswith(multiget([kwargs, env], 'CXXTEST_SUFFIX', None)):
                headers.append(l)
            else:
                linkins.append(l)

        deps = []
        if len(headers) == 0:
            if len(linkins) != 0:
                # the 1st source specified is the test
                deps.append(env.CxxTestCpp(linkins.pop(0), **kwargs))
        else:
            deps.append(env.CxxTestCpp(headers.pop(0), **kwargs))
            deps.extend(
                [env.CxxTestCpp(header, CXXTEST_RUNNER = 'none', 
                    CXXTEST_ROOT_PART = '--part', **kwargs)
                    for header in headers]
                )
        deps.extend(linkins)
        kwargs['CPPPATH'] = list(set(
            Split(kwargs.get('CPPPATH', [])) +
            Split(env.get(   'CPPPATH', [])) +
            Split(kwargs.get('CXXTEST_CPPPATH', [])) +
            Split(env.get(   'CXXTEST_CPPPATH', []))
            ))

        return UnitTest(env, target, source = deps, **kwargs)

    env.Append( BUILDERS = { "CxxTest" : CxxTest, "CxxTestCpp" : cxxtest_builder } )

def exists(env):
    return path.exists(env['CXXTEST'])
