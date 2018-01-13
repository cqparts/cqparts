#!/usr/bin/env bash

script=runtests.py


function show_help() {
    [ "$@" ] && echo "$@"
cat << EOF
Usage: ./${0##*/} {all|...}

Helper script to run different groups of testing.

Arguments:

    all     run all tests
    quick   run most tests, skip the slower ones

EOF
}


case "$1" in
    # Show help on request
    -h|--help)
        show_help
        exit 0
        ;;

    all|"")
        # run all tests (default behaviour)
        python ${script}
        ;;

    coverage)
        coverage run ${script}
        case "$2" in
            text|"")
                coverage report
                ;;
            html)
                coverage html
                ;;
        esac
        ;;

    quick)
        python ${script} --blacklist "slow"
        ;;

    *)
        show_help >&2
        exit 1
        ;;

esac
