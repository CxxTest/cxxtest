#!/bin/bash
function test() {
    if [[ "x$SELECT_TEST" != "x" ]] && [[ "x${1%'/'}" != "x$SELECT_TEST" ]]
    then
        return 0
    fi

    if [[ -d "$1" ]]
    then
        cd "$1"
        if [[ "$ACTION" == "--clean" ]]
        then
            scons --clean
        elif [[ "$ACTION" == "--run" ]]
        then
            echo "### RUNNING TEST $1 ###"
            scons --clean && scons . && scons check
            ret=$?
            if [[ "x$ret" = "x0" ]]
            then
                echo "### TEST $1 SUCCESSFUL ###"
                echo
            else
                echo "### TEST $1 FAILED ###"
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
cleanup
