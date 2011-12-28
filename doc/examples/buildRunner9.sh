#!/bin/bash

. GetGlobals.sh
export PATH=$CXXTEST/bin:$PATH

# @part:
cxxtestgen --part --error-printer -o MyTestSuite1.cpp MyTestSuite1.h
cxxtestgen --part --error-printer -o MyTestSuite2.cpp MyTestSuite2.h
# @:part

# @root:
cxxtestgen --root --error-printer -o runner9.cpp
# @:root

# @compile:
g++ -o runner9 -I$CXXTEST runner9.cpp MyTestSuite1.cpp MyTestSuite2.cpp
# @:compile

./runner

#rm -f MyTestSuite1.cpp MyTestSuite2.cpp
