#!/usr/bin/env bash

ENV_NAME=${PWD##*/}
NAME=cqparts-test:${ENV_NAME}

docker image rm ${NAME}

