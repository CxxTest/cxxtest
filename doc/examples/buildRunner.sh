#!/bin/bash

# @main:
$CXXTESTBIN/cxxtestgen --error-printer -o runner.cpp MyTestSuite.h
# @:main

# @compile:
g++ -o runner -I$CXXTEST runner.cpp
# @:compile
