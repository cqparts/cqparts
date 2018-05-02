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

## `cqparts-env:ubuntu-py2`

Install `python` and `freecad` as they are directy from `apt`

At the time of writing this: [2018-03]

- Python 2.7.12 (default, Dec  4 2017, 14:50:18)
- FreeCAD 0.16 Revision: 6712 (Git)

## `cqparts-env:ubuntu-py3`

Install `python3` with `apt`, and `freecad=0.17` with `conda`:

At the time of writing this: [2018-03]

- Python 3.5.2 (default, Nov 23 2017, 16:37:01)
- FreeCAD 0.17, Libs: 0.17R13062 (Git)


# Using these as a basis

Docker images built elsewhere in this repository use one of these
environments as a basis... for example:

The `Dockerfile` for `cqparts-test:ubuntu-py2` would start with

    FROM cqparts-env:ubuntu-py2
