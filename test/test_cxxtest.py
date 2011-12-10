import sys
import os
import os.path
import glob
import difflib
import subprocess
if sys.version_info < (2,7):
    import unittest2 as unittest
else:
    import unittest

currdir = os.path.dirname(os.path.abspath(__file__))+os.sep
sampledir = os.path.dirname(os.path.dirname(currdir))+'/sample'+os.sep

# Headers from the cxxtest/sample directory
samples = ' '.join(file for file in sorted(glob.glob(sampledir+'*.h')))
guiInputs=currdir+'../sample/gui/GreenYellowRed.h'
target_suffix = '.exe' if sys.platform.startswith('win') else ''

def available(compiler, exe_option):
    cmd = "%s %s %s %s > %s 2>&1" % (compiler, exe_option, currdir+'anything', currdir+'anything.cpp', currdir+'anything.log')
    ##print cmd
    status = subprocess.call(cmd, shell=True)
    flag = status == 0 and os.path.exists(currdir+'anything')
    os.remove(currdir+'anything.log')
    if os.path.exists(currdir+'anything'):
        os.remove(currdir+'anything')
    return flag

def file_diff(filename1, filename2):
    INPUT1=open(filename1, 'r')
    lines1 = INPUT1.readlines()
    for i in range(0,len(lines1)):
        lines1[i] = lines1[i].strip()
        if '/' in lines1[i]:
            lines1[i] = lines1[i].split('/')[-1]
    INPUT1.close()

    INPUT2=open(filename2, 'r')
    lines2 = INPUT2.readlines()
    for i in range(0,len(lines2)):
        lines2[i] = lines2[i].strip()
        if '/' in lines2[i]:
            lines2[i] = lines2[i].split('/')[-1]
    INPUT2.close()

    s=""
    for line in difflib.unified_diff(lines2,lines1,fromfile=filename2,tofile=filename1):
        s += line+"\n"
    return s



class BaseTestCase(object):

    fog=''

    def setUp(self):
        self.passed=False
        self.prefix=''
        self.py_out=''
        self.py_cpp=''
        self.px_pre=''
        self.px_out=''
        self.build_log=''
        self.build_target=''

    def tearDown(self):
        if not self.passed:
            return
        if os.path.exists(self.py_out):
            os.remove(self.py_out)
        if os.path.exists(self.py_cpp):
            os.remove(self.py_cpp)
        if os.path.exists(self.px_pre):
            os.remove(self.px_pre)
        if os.path.exists(self.px_out):
            os.remove(self.px_out)
        if os.path.exists(self.build_log):
            os.remove(self.build_log)
        if os.path.exists(self.build_target):
            os.remove(self.build_target)

    def check_if_supported(self, filename, msg):
        target=currdir+'check'+'px'+target_suffix
        log=currdir+'check'+'_build.log'
        cmd = "%s %s %s %s. %s%s../ %s > %s 2>&1" % (self.compiler, self.exe_option, target, self.include_option, self.include_option, currdir, filename, log)
        ##print cmd
        status = subprocess.call(cmd, shell=True)
        os.remove(log)
        if status != 0 or not os.path.exists(target):
            self.skipTest(msg)
        os.remove(target)

    def init(self, prefix):
        #
        self.prefix = self.__class__.__name__+'_'+prefix
        self.py_out = currdir+self.prefix+'_py.out'
        self.py_cpp = currdir+self.prefix+'_py.cpp'
        self.px_pre = currdir+self.prefix+'_px.pre'
        self.px_out = currdir+self.prefix+'_px.out'
        self.build_log = currdir+self.prefix+'_build.log'
        self.build_target = currdir+self.prefix+'px'+target_suffix

    def check_root(self, prefix='', output=None):
        self.init(prefix)
        args = "--have-eh --abort-on-fail --root --error-printer"
        cmd = "%s %s../python/scripts/cxxtestgen %s -o %s %s > %s 2>&1" % (sys.executable, currdir, self.fog, self.py_cpp, args, self.py_out)
        #print self.fog, "CMD", cmd
        status = subprocess.call(cmd, shell=True)
        self.assertEquals(status, 0, 'Error executing cxxtestgen')
        #
        files = [self.py_cpp]
        for i in [1,2]:
            args = "--have-eh --abort-on-fail --part Part%s.h" % str(i)
            file = currdir+self.prefix+'_py%s.cpp' % str(i)
            files.append(file)
            cmd = "%s %s../python/scripts/cxxtestgen %s -o %s %s > %s 2>&1" % (sys.executable, currdir, self.fog, file, args, self.py_out)
            ##print cmd
            status = subprocess.call(cmd, shell=True)
            self.assertEquals(status, 0, 'Error executing cxxtestgen')
        #
        cmd = "%s %s %s %s. %s%s../ %s > %s 2>&1" % (self.compiler, self.exe_option, self.build_target, self.include_option, self.include_option, currdir, ' '.join(files), self.build_log)
        ##print cmd
        status = subprocess.call(cmd, shell=True)
        for file in files:
            if os.path.exists(file):
                os.remove(file)
        self.assertEquals(status, 0, 'Error executing command: '+cmd)
        #
        status = subprocess.call("%s -v > %s 2>&1" % (self.build_target, self.px_pre), shell=True)
        OUTPUT = open(self.px_pre,'a')
        print >>OUTPUT, 'Error level = '+str(status)
        OUTPUT.close()
        diffstr = file_diff(self.px_pre, output)
        if not diffstr == '':
            self.fail("Unexpected differences in output:\n"+diffstr)
        #
        self.passed=True

    def compile(self, prefix='', args=None, compile='', output=None, main=None, failGen=False, run=None):
        self.init(prefix)
        #
        cmd = "%s %s../python/scripts/cxxtestgen %s -o %s %s > %s 2>&1" % (sys.executable, currdir, self.fog, self.py_cpp, args, self.py_out)
        #print "HERE", cmd
        status = subprocess.call(cmd, shell=True)
        if failGen:
            if status == 0: 
                self.fail('Expected cxxtestgen to fail.')
            else:
                self.passed=True
                return
        self.assertEquals(status, 0, 'Error executing command: '+cmd)
        #
        if not main is None:
            # Compile with main
            cmd = "%s %s %s %s. %s%s../ %s main.cpp %s > %s 2>&1" % (self.compiler, self.exe_option, self.build_target, self.include_option, self.include_option, currdir, compile, self.py_cpp, self.build_log)
        else:
            # Compile without main
            cmd = "%s %s %s %s. %s%s../ %s %s > %s 2>&1" % (self.compiler, self.exe_option, self.build_target, self.include_option, self.include_option, currdir, compile, self.py_cpp, self.build_log)
        status = subprocess.call(cmd, shell=True)
        self.assertEquals(status, 0, 'Error executing command: '+cmd)
        #
        if compile == '' and not output is None:
            if run is None:
                cmd = "%s -v > %s 2>&1" % (self.build_target, self.px_pre)
            else:
                cmd = run % (self.build_target, self.px_pre)
            status = subprocess.call(cmd, shell=True)
            #print "HERE-status",status
            OUTPUT = open(self.px_pre,'a')
            print >>OUTPUT, 'Error level = '+str(status)
            OUTPUT.close()
            diffstr = file_diff(self.px_pre, output)
            if not diffstr == '':
                self.fail("Unexpected differences in output:\n"+diffstr)
        #
        if compile == '' and output is None and os.path.exists(self.py_cpp):
            self.fail("Output cpp file %s should not have been generated." % self.py_cpp)
        #
        self.passed=True

    #
    # Tests for cxxtestgen
    #

    def test_root_or_part(self):
        """Root/Part"""
        self.check_root(prefix='root_or_part', output="parts.out")

    def test_root_plus_part(self):
        """Root + Part"""
        self.compile(prefix='root_plus_part', args="--error-printer --root --part "+samples, output="error.out")

    def test_wildcard(self):
        """Wildcard input"""
        self.compile(prefix='wildcard', args=currdir+'../sample/*.h', main=True, output="wildcard.out")

    def test_stdio_printer(self):
        """Stdio printer"""
        self.compile(prefix='stdio_printer', args="--runner=StdioPrinter "+samples, output="error.out")

    def test_paren_printer(self):
        """Paren printer"""
        self.compile(prefix='paren_printer', args="--runner=ParenPrinter "+samples, output="paren.out")

    def test_yn_runner(self):
        """Yes/No runner"""
        self.compile(prefix='yn_runner', args="--runner=YesNoRunner "+samples, output="runner.out")

    def test_no_static_init(self):
        """No static init"""
        self.compile(prefix='no_static_init', args="--error-printer --no-static-init "+samples, output="error.out")

    def test_have_std(self):
        """Have Std"""
        self.compile(prefix='have_std', args="--runner=StdioPrinter --have-std HaveStd.h", output="std.out")

    def test_comments(self):
        """Comments"""
        self.compile(prefix='comments', args="--error-printer Comments.h", output="comments.out")

    def test_longlong(self):
        """Long long"""
        self.check_if_supported('longlong.cpp', "Long long is not supported by this compiler")
        self.compile(prefix='longlong', args="--error-printer --longlong= LongLong.h", output="longlong.out")

    def test_int64(self):
        """Int64"""
        self.check_if_supported('int64.cpp', "64-bit integers are not supported by this compiler")
        self.compile(prefix='int64', args="--error-printer --longlong=__int64 Int64.h", output="int64.out")

    def test_include(self):
        """Include"""
        self.compile(prefix='include', args="--include=VoidTraits.h --include=LongTraits.h --error-printer IncludeTest.h", output="include.out")

    #
    # Template file tests
    #

    def test_preamble(self):
        """Preamble"""
        self.compile(prefix='preamble', args="--template=preamble.tpl "+samples, output="preamble.out")

    def test_activate_all(self):
        """Activate all"""
        self.compile(prefix='activate_all', args="--template=activate.tpl "+samples, output="error.out")

    def test_only_suite(self):
        """Only Suite"""
        self.compile(prefix='only_suite', args="--template=%s../sample/only.tpl %s" % (currdir, samples), run="%s SimpleTest > %s 2>&1", output="suite.out")

    def test_only_test(self):
        """Only Test"""
        self.compile(prefix='only_test', args="--template=%s../sample/only.tpl %s" % (currdir, samples), run="%s SimpleTest testAddition > %s 2>&1", output="suite_test.out")

    #
    # Test cases which do not require exception handling
    #

    def test_no_errors(self):
        """No errors"""
        self.compile(prefix='no_errors', args="--error-printer GoodSuite.h", output="good.out")

    def test_max_dump_size(self):
        """Max dump size"""
        self.compile(prefix='max_dump_size', args="--error-printer --include=MaxDump.h DynamicMax.h SameData.h", output='max.out')

    def test_wide_char(self):
        """Wide char"""
        self.check_if_supported('wchar.cpp', "The file wchar.cpp is not supported.")
        self.compile(prefix='wide_char', args="--error-printer WideCharTest.h", output="wchar.out")

    def test_factor(self):
        """Factor"""
        self.compile(prefix='factor', args="--error-printer --factor Factor.h", output="factor.out")

    def test_user_traits(self):
        """User traits"""
        self.compile(prefix='user_traits', args="--template=UserTraits.tpl UserTraits.h", output='user.out')

    normals = "LessThanEquals.h Relation.h DefaultTraits.h DoubleCall.h SameData.h Tsm.h TraitsTest.h MockTest.h SameZero.h"

    def test_normal_behavior(self):
        """Normal Behavior"""
        self.compile(prefix='normal_behavior', args="--error-printer "+self.normals, output="normal.out")

    def test_normal_plus_abort(self):
        """Normal + Abort"""
        self.compile(prefix='normal_plus_abort', args="--error-printer --have-eh --abort-on-fail "+self.normals, output="abort.out")

    def test_stl_traits(self):
        """STL Traits"""
        self.check_if_supported('stpltpl.cpp', "The file stpltpl.cpp is not supported.")
        self.compile(prefix='stl_traits', args="--error-printer StlTraits.h", output="stl.out")

    #
    # Test cases which do require exception handling
    #
    def test_throw_wo_std(self):
        """Throw w/o Std"""
        self.compile(prefix='test_throw_wo_std', args="--template=ThrowNoStd.tpl ThrowNoStd.h", output='throw.out')

    ehNormals = "Exceptions.h DynamicAbort.h"

    def test_exceptions(self):
        """Exceptions"""
        self.compile(prefix='exceptions', args="--error-printer --have-eh "+self.ehNormals, output="eh_normals.out")

    def test_exceptions_plus_abort(self):
        """Exceptions plus abort"""
        self.compile(prefix='exceptions', args="--error-printer --abort-on-fail --have-eh DynamicAbort.h DeepAbort.h ThrowsAssert.h", output="eh_plus_abort.out")

    def test_default_abort(self):
        """Default abort"""
        self.compile(prefix='default_abort', args="--error-printer --include=DefaultAbort.h "+self.ehNormals+ " DeepAbort.h ThrowsAssert.h", output="default_abort.out")

    def test_default_no_abort(self):
        """Default no abort"""
        self.compile(prefix='default_no_abort', args="--error-printer "+self.ehNormals+" DeepAbort.h ThrowsAssert.h", output="default_abort.out")

    #
    # Global Fixtures
    #

    def test_global_fixtures(self):
        """Global fixtures"""
        self.compile(prefix='global_fixtures', args="--error-printer GlobalFixtures.h WorldFixtures.h", output="gfxs.out")

    def test_gf_suw_fails(self):
        """GF:SUW fails"""
        self.compile(prefix='gf_suw_fails', args="--error-printer SetUpWorldFails.h", output="suwf.out")

    def test_gf_suw_throws(self):
        """GF:SUW throws"""
        self.compile(prefix='gf_suw_throws', args="--error-printer SetUpWorldThrows.h", output="suwt.out")

    def test_gf_su_fails(self):
        """GF:SU fails"""
        self.compile(prefix='gf_su_fails', args="--error-printer GfSetUpFails.h", output="gfsuf.out")

    def test_gf_su_throws(self):
        """GF:SU throws"""
        self.compile(prefix='gf_su_throws', args="--error-printer GfSetUpThrows.h", output="gfsut.out")

    def test_gf_td_fails(self):
        """GF:TD fails"""
        self.compile(prefix='gf_td_fails', args="--error-printer GfTearDownFails.h", output="gftdf.out")

    def test_gf_td_throws(self):
        """GF:TD throws"""
        self.compile(prefix='gf_td_throws', args="--error-printer GfTearDownThrows.h", output="gftdt.out")

    def test_gf_tdw_fails(self):
        """GF:TDW fails"""
        self.compile(prefix='gf_tdw_fails', args="--error-printer TearDownWorldFails.h", output="tdwf.out")

    def test_gf_tdw_throws(self):
        """GF:TDW throws"""
        self.compile(prefix='gf_tdw_throws', args="--error-printer TearDownWorldThrows.h", output="tdwt.out")

    #
    # GUI
    #

    def test_gui(self):
        """GUI"""
        self.compile(prefix='gui', args='--gui=DummyGui %s' % guiInputs, output ="gui.out")

    def test_gui_runner(self):
        """GUI + runner"""
        self.compile(prefix='gui_runner', args="--gui=DummyGui --runner=ParenPrinter %s" % guiInputs, output="gui_paren.out")

    def test_qt_gui(self):
        """QT GUI"""
        self.compile(prefix='qt_gui', args="--gui=QtGui GoodSuite.h", compile=self.qtFlags)

    def test_win32_gui(self):
        """Win32 GUI"""
        self.compile(prefix='win32_gui', args="--gui=Win32Gui GoodSuite.h", compile=self.w32Flags)

    def test_win32_unicode(self):
        """Win32 Unicode"""
        self.compile(prefix='win32_unicode', args="--gui=Win32Gui GoodSuite.h", compile=self.w32Flags+' -DUNICODE')

    def test_x11_gui(self):
        """X11 GUI"""
        self.check_if_supported('wchar.cpp', "Cannot compile wchar.cpp")
        self.compile(prefix='x11_gui', args="--gui=X11Gui GoodSuite.h", compile=self.x11Flags)


    #
    # Tests for when the compiler doesn't support exceptions
    #

    def test_no_exceptions(self):
        """No exceptions"""
        if self.no_eh_option is None:
            self.skipTest("This compiler does not have an exception handling option")
        self.compile(prefix='no_exceptions', args='--runner=StdioPrinter NoEh.h', output="no_eh.out", compile=self.no_eh_option)

    def test_force_no_eh(self):
        """Force no EH"""
        if self.no_eh_option is None:
            self.skipTest("This compiler does not have an exception handling option")
        self.compile(prefix="force_no_eh", args="--runner=StdioPrinter --no-eh ForceNoEh.h", output="no_eh.out", compile=self.no_eh_option)

    #
    # Invalid input to cxxtestgen
    #

    def test_no_tests(self):
        """No tests"""
        self.compile(prefix='no_tests', args='EmptySuite.h', failGen=True)

    def test_missing_input(self):
        """Missing input"""
        self.compile(prefix='missing_input', args='--template=NoSuchFile.h', failGen=True)

    def test_missing_template(self):
        """Missing template"""
        self.compile(prefix='missing_template', args='--template=NoSuchFile.h '+samples, failGen=True)

    def test_inheritance(self):
        """Test relying on inheritance"""
        self.compile(prefix='inheritance', args='--error-printer InheritedTest.h', output='inheritance_old.out')

    def test_inheritance(self):
        """Test relying on inheritance"""
        if self.fog == '':
            self.compile(prefix='inheritance', args='--error-printer InheritedTest.h', failGen=True)
        else:
            self.compile(prefix='inheritance', args='--error-printer InheritedTest.h', output='inheritance.out')

    def test_simple_inheritance(self):
        """Test relying on simple inheritance"""
        self.compile(prefix='simple_inheritance', args='--error-printer SimpleInheritedTest.h', output='simple_inheritance.out')


class TestCpp(BaseTestCase, unittest.TestCase):

    # Compiler specifics
    exe_option = '-o'
    include_option = '-I'
    compiler='c++ -Wall -W -Werror -g'
    no_eh_option = None
    qtFlags='-Ifake'
    x11Flags='-Ifake'
    w32Flags='-Ifake'

    def run(self, *args, **kwds):
        if available('c++', '-o'):
            return unittest.TestCase.run(self, *args, **kwds)

    def setUp(self):
        BaseTestCase.setUp(self)

    def tearDown(self):
        BaseTestCase.tearDown(self)


class TestCppFOG(TestCpp):

    fog='-f'


class TestGpp(BaseTestCase, unittest.TestCase):

    # Compiler specifics
    exe_option = '-o'
    include_option = '-I'
    compiler='g++ -g -Wall -W -Wshadow -Woverloaded-virtual -Wnon-virtual-dtor -Wreorder -Wsign-promo'
    no_eh_option = '-fno-exceptions'
    qtFlags='-Ifake'
    x11Flags='-Ifake'
    w32Flags='-Ifake'

    def run(self, *args, **kwds):
        if available('g++', '-o'):
            return unittest.TestCase.run(self, *args, **kwds)

    def setUp(self):
        BaseTestCase.setUp(self)

    def tearDown(self):
        BaseTestCase.tearDown(self)


class TestGppFOG(TestGpp):

    fog='-f'


class TestClang(BaseTestCase, unittest.TestCase):

    # Compiler specifics
    exe_option = '-o'
    include_option = '-I'
    compiler='clang++ -v -g -Wall -W -Wshadow -Woverloaded-virtual -Wnon-virtual-dtor -Wreorder -Wsign-promo'
    no_eh_option = '-fno-exceptions'
    qtFlags='-Ifake'
    x11Flags='-Ifake'
    w32Flags='-Ifake'

    def run(self, *args, **kwds):
        if available('clang++', '-o'):
            return unittest.TestCase.run(self, *args, **kwds)

    def setUp(self):
        BaseTestCase.setUp(self)

    def tearDown(self):
        BaseTestCase.tearDown(self)


class TestClangFOG(TestClang):

    fog='-f'


class TestCL(BaseTestCase, unittest.TestCase):

    # Compiler specifics
    exe_option = '-o'
    include_option = '-I'
    compiler='cl -nologo -GX -W4 -WX'
    no_eh_option = '-GX-'
    qtFlags='-Ifake'
    x11Flags='-Ifake'
    w32Flags='-Ifake'

    def run(self, *args, **kwds):
        if available('cl', '-o'):
            return unittest.TestCase.run(self, *args, **kwds)

    def setUp(self):
        BaseTestCase.setUp(self)

    def tearDown(self):
        BaseTestCase.tearDown(self)


class TestCLFOG(TestCL):

    fog='-f'


if __name__ == '__main__':
    unittest.main()
