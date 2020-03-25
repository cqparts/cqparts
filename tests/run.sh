#!/usr/bin/env bash

script=runtests.py

# Default python binary (if not environmentally set)
if [[ -z "${PYTHON_BIN}" ]]; then PYTHON_BIN=python; fi

function show_help() {
    [ "$@" ] && echo "$@"
cat << EOF
Usage: ./${0##*/} {all|...}

Helper script to run different groups of testing.

Arguments:

    (default)   with no argument, run all non-catalogue tests
    all         run all tests
    catalogue   run all catalogue tests (ignore others)

    coverage <text|html>
                run non-catalogue tests and generate coverage report
EOF
}


case "$1" in
    # Show help on request
    -h|--help)
        show_help
        exit 0
        ;;

    "")
        # run all non-catalogue tests (default behaviour)
        ${PYTHON_BIN} ${script} --ignore "catalogue,complex_thread"
        # FIXME: remove complex_thread when #1 is fixed.
        #        also remove from Dockerfile
        ;;

    all)
        # run all scripts
        ${PYTHON_BIN} ${script}
        ;;

    coverage)
        coverage run ${script} --ignore "catalogue"
        case "$2" in
            text|"")
                coverage report
                ;;
            html)
                coverage html
                ;;
        esac
        ;;

    catalogue)
        ${PYTHON_BIN} ${script} --dontignore "catalogue"
        ;;

    *)
        show_help >&2
        exit 1
        ;;

esac
