#
# Some convenient ways of running the self tests
#

TEST = perl test.pl

all: gcc

clean:
	rm -f *p[ly].out *px *px.out *build.log *root.cpp parsetab.py *.gcno *.gcda ../cxxtest/*.gcno ../cxxtest/*.gcda ../sample/*.gcno ../sample/*.gcda Test*.cpp
	rm -Rf *.dSYM

gcc:
	$(TEST) --gcc || (diff -u pl.cpp py.cpp; cat pl.out py.out build.log px.out)

gcc-2.96:
	$(TEST) --compiler='g++-2.96 -g -Wall -W -Werror -Woverloaded-virtual -Wnon-virtual-dtor -Wreorder -Wsign-promo' --no-eh-option='-fno-exceptions' || (diff -u pl.cpp py.cpp; cat pl.out py.out build.log px.out; exit 1)

gcc-2.96-bug:
	$(TEST) --compiler='g++-2.96 -g -Wall -fomit-frame-pointer' --no-eh-option='-fno-exceptions' || (diff -u pl.cpp py.cpp; cat pl.out py.out build.log px.out; exit 1)

gcc_no_python:
	$(TEST) --gcc --no-python || (cat pl.out build.log px.out; exit 1)

#
# Local Variables:
# compile-command: "gmake gcc"
# End:
#
