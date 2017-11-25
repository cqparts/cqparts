#/usr/bin/env bash


sphinx_build=_build/html
sphinx_dest=../docs/doc

rsync -aIvzh --delete "${sphinx_build}/" "${sphinx_dest}/"
