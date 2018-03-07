The docker containers built from these sub-folders are used as a basis for
deployment and testing.

These environments are centralised in this folder in an attempt to avoid
redundancy; namely installing freecad over and over again.

**Why**?

Creating this docker environment basis was decided when desiging the
deployment strategy; deployment requires a suitable environment, without the
python dependencies pre-installed (meeting dependency requirements is part of
the package testing). Whereas having to install python package dependencies each
time I want to run a unittest would be painful... hence this `env` folder.

# Docker Environments

Environments are ultimately split by their freecad installation.

## FreeCAD v0.16 -> Python 2.x

Install `python` and `freecad` as they are directy from `apt`

At the time of writing this: [2018-03]

- Python 2.7.12 (default, Dec  4 2017, 14:50:18)
- FreeCAD 0.16 Revision: 6712 (Git)

## FreeCAD v0.17 -> Python 3.x

Install `python3` with `apt`, and `freecad=0.17` with `conda`:

At the time of writing this: [2018-03]

- Python 3.5.2 (default, Nov 23 2017, 16:37:01)
- FreeCAD 0.17, Libs: 0.17R13062 (Git)

# Using these as a basis

Docker containers build elsewhere in this repository use one of these
environments as a basis... for example:

The `Dockerfile` for `cqparts-test:ubuntu-py2` would start with

    FROM cqparts-env:ubuntu-py2
