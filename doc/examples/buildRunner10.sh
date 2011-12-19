#!/bin/bash

export PATH=$CXXTEST/bin:$PATH

# @main:
cxxtestgen -o runner.cpp --template runner10.tpl MyTestSuite2.h
# @:main

# @compile:
g++ -o runner -I$CXXTEST runner.cpp
# @:compile

./runner
