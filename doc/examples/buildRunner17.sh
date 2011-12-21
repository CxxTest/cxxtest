#!/bin/bash -v

export PATH=$CXXTEST/bin:$PATH

# @main:
cxxtestgen --have-std --error-printer -o runner.cpp MyTestSuite7.h
# @:main

# @compile:
g++ -o runner -I$CXXTEST runner.cpp
# @:compile

./runner

