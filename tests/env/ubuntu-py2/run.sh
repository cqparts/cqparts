#!/usr/bin/env bash

ENV_NAME=${PWD##*/}
NAME=cqparts-test:${ENV_NAME}

case "$1" in
    bash|python|ipython)
        docker run --rm -it ${NAME} $1
        ;;
    test|"")
        docker run --rm ${NAME}
        ;;
    *)
        echo "give action: bash|ipython|test"
        ;;
esac
