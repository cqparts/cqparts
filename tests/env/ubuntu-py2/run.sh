#!/usr/bin/env bash

CQPARTS_ROOT=$(git rev-parse --show-toplevel)
ENV_NAME=${PWD##*/}
NAME=cqparts-test:${ENV_NAME}

case "$1" in
    tests|"")
        docker run --rm --volume ${CQPARTS_ROOT}:/code ${NAME}
        ;;
    *)
        docker run --rm --volume ${CQPARTS_ROOT}:/code -it ${NAME} "${@:1}"
        ;;
esac
