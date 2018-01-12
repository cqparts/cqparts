#!/usr/bin/env bash



function show_help() {
    [ "$@" ] && echo "$@"
cat << EOF
Usage: ./${0##*/} {all|...}

Helper script to run different groups of testing.

Arguments:

    all     run all tests

EOF
}


function all() {
    python runtests.py
}


case "$1" in
    # Show help on request
    -h|--help)
        show_help
        exit 0
        ;;

    all|"") all ;;

    *)
        show_help >&2
        exit 1
        ;;

esac
