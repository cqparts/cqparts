#!/usr/bin/env bash

#rm -r _build/*
#make html

SPHINXOPTS="-a -E"
SPHINXBUILD=sphinx-build
SOURCEDIR=.
BUILDDIR=_build

${SPHINXBUILD} -M html ${SOURCEDIR} ${BUILDDIR} ${SPHINXOPTS}
