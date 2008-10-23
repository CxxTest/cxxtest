#ifndef __CxxTestMain_h
#define __CxxTestMain_h

#include <cstring>
#include <iostream>

namespace CxxTest {

template <class TesterT>
int Main(int argc, char* argv[])
{
TesterT tmp;
return tmp.run();
}

}

/*
 * Copyright 2008 Sandia Corporation. Under the terms of Contract
 * DE-AC04-94AL85000 with Sandia Corporation, the U.S. Government
 * retains certain rights in this software.
 */
#endif
