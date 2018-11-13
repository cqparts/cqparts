The docker images built from these sub-folders are used as a basis for
deployment and testing.

These environments are centralised in this folder in an attempt to avoid
redundancy; namely installing freecad over and over again.

**Why**?

Creating this docker environment basis was decided when designing environments
for deployment and unittest environments:

* *Deployment* : testing requires a suitable environment, *without* any python dependencies
  pre-installed (meeting dependency requirements is part of the package testing).

* *Unit-Testing* : needs to have a fully functioning environment so tests can
  begin straight away.

To avoid redundancy in environments, the docker images built in this folder are
used as a basis for others elsewhere in the project.


# Docker Images

To build each of these containers, go into each folder and run:

    ./build.sh

## `cqparts-env:ubuntu-occ`

Install `python` and `pythonocc` (via `cadquery-occ`)

At the time of writing this: [2018-11]

- Python 3.5.2


# Using these as a basis

Docker images built elsewhere in this repository use one of these
environments as a basis... for example:

The `Dockerfile` for `cqparts-test:ubuntu-occ` would start with

    FROM cqparts-env:ubuntu-occ
