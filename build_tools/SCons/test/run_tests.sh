#!/bin/bash

TEST_SYMLINKS_FILE="test_symlinks"

function test() {
    if [[ "x$SELECT_TEST" != "x" ]] && [[ "x${1%'/'}" != "x$SELECT_TEST" ]]
    then
        return 0
    fi

    local testdir="$1"
    if [[ -d "$testdir" ]]
    then
        cd "$testdir"
        if [[ "$ACTION" == "--clean" ]]
        then
            ../helpers.sh create_symlinks "$TEST_SYMLINKS_FILE"
            scons --clean
            ../helpers.sh remove_symlinks "$TEST_SYMLINKS_FILE"
        elif [[ "$ACTION" == "--run" ]]
        then
            echo "### RUNNING TEST $testdir ###"
            if [[ -f "README" ]]
            then
                cat README
                echo "--------------------"
            fi
            ../helpers.sh create_symlinks "$TEST_SYMLINKS_FILE"
            scons --clean && scons . && scons check
            local ret=$?
            if [[ "x$ret" = "x0" ]]
            then
                echo "### TEST $testdir SUCCESSFUL ###"
                echo
            else
                echo "### TEST $testdir FAILED ###"
                echo
            fi
        fi
        cd ..
        return $ret
    else
        echo "Cannot find test!"
        return 1
    fi
}

function cleanup() {
    if [[ "$ACTION" == "--clean" ]]
    then
        rm */.sconsign.dblite
    fi
}

ACTION="--run"
SELECT_TEST=""

if [[ "$1" == "--clean" ]] || [[ "$1" == "--run" ]]
then
    ACTION="$1"
    DIR="$2"
else
    ACTION="--run"
    DIR="$1"
fi

if [[ -d "$DIR" ]] || [[ "x" == "x$DIR" ]]
then
    SELECT_TEST=${DIR%'/'}
else
    cat <<USAGE
This is the test runner for the SCons builder unit tests.

Usage: run_tests.sh [action] [directory]
    action: --run (default) - runs the test
            --clean         - cleans up
If the directory is provided, this will only run the test in that directory.
Otherwise, it will run all the tests.

Test definition: Tests must have a SConstruct file. Optionally, they can have a
$TEST_SYMLINKS_FILE file that specifies the link name and its destination. Example:

cxxtest ../../../../

would create a link called cxxtest in the current directory that pointed to ../../../../
Such links are removed with the --clean action. The file is used as an input to xargs, so
please, escape all characters properly.
USAGE
    exit 2
fi

test "default_env" &&\
test "nonstandard_cxxtest_dir" &&\
test "need_cpppath" &&\
test "string_cpppath" &&\
test "printer_propagation" &&\
test "multifile_tests" &&\
test "target_syntax" &&\
test "recursive_sources" &&\
test "expanding_#" &&\
test "include_CCFLAGS" &&\
test "include_CXXFLAGS" &&\
test "globbing" &&\
test "globbing_edmundo" &&\
test "empty_source_list" &&\
cleanup
