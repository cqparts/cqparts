#/usr/bin/env bash


sphinx_build=_build/html
sphinx_dest=../docs-published/doc

rsync -aIvzh --delete "${sphinx_build}/" "${sphinx_dest}/"
