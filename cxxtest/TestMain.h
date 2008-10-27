#ifndef __CxxTestMain_h
#define __CxxTestMain_h

#include <cstring>
#include <iostream>

namespace CxxTest {

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
if ((argc > 3) || ((argc==2) && ((strcmp(argv[1],"-h")==0) || (strcmp(argv[1],"--help")==0)))) {
   std::cerr << argv[0] << " <suitename>" << std::endl;
   std::cerr << argv[0] << " <suitename> <testname>" << std::endl;
   std::cerr << argv[0] << " -h" << std::endl;
   std::cerr << argv[0] << " --help" << std::endl;
   std::cerr << argv[0] << " --help-tests" << std::endl;
   return -1;
   }
//
// Print a list of the suite and test names
//
if ((argc==2) && (strcmp(argv[1],"--help-tests")==0)) {
   std::cout << "Suite/Test Names" << std::endl;
   std::cout << "---------------------------------------------------------------------------" << std::endl;
   for ( SuiteDescription *sd = RealWorldDescription().firstSuite(); sd; sd = sd->next() )
     for ( TestDescription *td = sd->firstTest(); td; td = td->next() )
       std::cout << td->suiteName() << " " << td->testName() << std::endl;
   return 0;
   }

bool status=false;
if (argc==2) {
    status=leaveOnly(argv[1]);
    if (!status) {
       std::cerr << "ERROR: unknown suite '" << argv[1] << "'" << std::endl;
       return -1;
       }
    }
if (argc==3) {
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

