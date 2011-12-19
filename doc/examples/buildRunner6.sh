#!/bin/bash

export PATH=$CXXTEST/bin:$PATH

# @main:
cxxtestgen --runner=XmlPrinter -o runner.cpp MyTestSuite2.h
# @:main

# @compile:
g++ -o runner -I$CXXTEST runner.cpp
# @:compile

./runner
