#ifndef __CxxTestMain_h
#define __CxxTestMain_h

#include <cstring>
#include <iostream>

namespace CxxTest {

void print_help(const char* name)
{
   std::cerr << name << " <suitename>" << std::endl;
   std::cerr << name << " <suitename> <testname>" << std::endl;
   std::cerr << name << " -h" << std::endl;
   std::cerr << name << " --help" << std::endl;
   std::cerr << name << " --help-tests" << std::endl;
}


template <class TesterT>
int Main(int argc, char* argv[])
{ 
TesterT tmp;
//
// Parse the command-line arguments. The default behavior is to run all tests
//
// This is a primitive parser, but I'm not sure what sort of portable
// parser should be used in cxxtest.
//

//
// Print command-line syntax
//
for (int i=1; i<argc; i++) {
  if ((strcmp(argv[i],"-h")==0) || (strcmp(argv[i],"--help")==0)) {
     print_help(argv[0]);
     return 0;
  } else if ((strcmp(argv[1],"--help-tests")==0)) {
    std::cout << "Suite/Test Names" << std::endl;
    std::cout << "---------------------------------------------------------------------------" << std::endl;
    for ( SuiteDescription *sd = RealWorldDescription().firstSuite(); sd; sd = sd->next() )
        for ( TestDescription *td = sd->firstTest(); td; td = td->next() )
            std::cout << td->suiteName() << " " << td->testName() << std::endl;
    return 0;
  }
}

bool status=false;
if ((argc==2) && (argv[1][0] != '-')) {
    status=leaveOnly(argv[1]);
    if (!status) {
       std::cerr << "ERROR: unknown suite '" << argv[1] << "'" << std::endl;
       return -1;
       }
    }
if ((argc==3) && (argv[1][0] != '-')) {
    status=leaveOnly(argv[1],argv[2]);
    if (!status) {
       std::cerr << "ERROR: unknown test '" << argv[1] << "::" << argv[2] << "'" << std::endl;
       return -1;
       }
    }

tmp.process_commandline(argc,argv);
return tmp.run();
}

}
#endif

// Copyright 2008 Sandia Corporation. Under the terms of Contract
// DE-AC04-94AL85000 with Sandia Corporation, the U.S. Government
// retains certain rights in this software.

