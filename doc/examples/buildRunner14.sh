#!/bin/bash -v

export PATH=$CXXTEST/bin:$PATH

# @main:
cxxtestgen --error-printer -o runner.cpp MyTestSuite5.h
# @:main

# @compile:
g++ -o runner -I$CXXTEST runner.cpp
# @:compile

./runner
