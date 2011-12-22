#!/bin/bash -v

. GetGlobals.sh
export PATH=$CXXTEST/bin:$PATH

# @main:
cxxtestgen --have-std --error-printer -o runner.cpp MyTestSuite7.h
# @:main

# @compile:
g++ -o runner -I$CXXTEST runner.cpp
# @:compile

./runner

