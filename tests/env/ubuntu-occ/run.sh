#!/usr/bin/env bash
source ./common-vars.sh

function run_container() {
    docker run --rm --volume ${CQPARTS_ROOT}:/code -it ${IMAGE} "$@"
}

case "$1" in
    "")
        # Run tests in interactive mode
        run_container
        ;;
    non-interactive)
        # Run tests (non-interactive; for continuous integration)
        docker run --rm --volume ${CQPARTS_ROOT}:/code ${IMAGE}
        ;;
    core)
        # Only run core t_cqparts tests
        run_container python3 runtests.py --module cqparts
        ;;
    *)
        run_container "${@:1}"
        ;;
esac
