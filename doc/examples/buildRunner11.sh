#!/bin/bash -v

export PATH=$CXXTEST/bin:$PATH

# @main:
cxxtestgen -f --error-printer -o runner.cpp MyTestSuite3.h
# @:main

# @compile:
g++ -o runner -I$CXXTEST runner.cpp
# @:compile

./runner
