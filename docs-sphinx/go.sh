#!/usr/bin/env bash

# ----- Build html from sphinx indexes
SPHINXOPTS="-a -E"
SPHINXBUILD=sphinx-build
SOURCEDIR=.
BUILDDIR=_build

PUBLISH_SRC=${BUILDDIR}/html
PUBLISH_DEST=../docs/doc


function show_help() {
    [ "$@" ] && echo "$@"
cat << EOF
Usage: ./${0##*/} {clean|web|...}

Helper script to perorm common documentation operations

Arguments:

    clean   deletes _build directory for a forced clean build
    web     start http service at: http://localhost:9040 to view docs
    publish mirror build directory to docs for publishing
    test    run documented code as testcases

    Build:
        build       make sphinx docs
        build api   generate api sphinx rst sources
        build all   clean, then make everything

EOF
}


function clean() {
    # Force build (delete build directory)
    if [[ -d $BUILDDIR/doctrees ]] && [[ -d $BUILDDIR/html ]] ; then
        rm -r $BUILDDIR/*
    else
        echo "ERROR: build directory doesn't look right"
        exit 1
    fi
}


function build_apidocs() {
    # Build API sphinx indexes
    api/build.sh -f
}


function build_all() {
    build_apidocs
    ${SPHINXBUILD} -M html ${SOURCEDIR} ${BUILDDIR} ${SPHINXOPTS}
}

function build_html() {
    make html
}

function web() {
    python localweb.py
}

function build() {

    case "$1" in
        "")
            build_html
            ;;
        api)
            build_apidocs
            ;;
        all)
            clean
            build_apidocs
            build_all
            ;;
    esac
}

function doctest() {
    make doctest
}

function publish() {
    rsync -aIvzh --delete "${PUBLISH_SRC}/" "${PUBLISH_DEST}/"
}


case "$1" in
    # Show help on request
    -h|--help)
        show_help
        exit 0
        ;;
    clean) clean ;;
    web) web ;;
    publish) publish ;;
    test) doctest ;;
    build) build $2 ;;
    *)
        show_help >&2
        exit 1
        ;;

esac
