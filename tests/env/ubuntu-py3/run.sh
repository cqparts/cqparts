#!/usr/bin/env bash

ENV_NAME=${PWD##*/}
NAME=cqparts-test:${ENV_NAME}

case "$1" in
    test|"")
        docker run --rm ${NAME}
        ;;
    *)
        docker run --rm -it ${NAME} "${@:1}"
        ;;
esac
