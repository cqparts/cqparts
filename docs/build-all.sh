#!/usr/bin/env bash

# Force build (delete build directory)
#rm -r _build/*

# ----- Build API sphinx indexes
api/build.sh -f

# ----- Build html from sphinx indexes
SPHINXOPTS="-a -E"
SPHINXBUILD=sphinx-build
SOURCEDIR=.
BUILDDIR=_build

#make html
${SPHINXBUILD} -M html ${SOURCEDIR} ${BUILDDIR} ${SPHINXOPTS}
