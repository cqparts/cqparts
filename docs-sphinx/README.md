# Sphinx Documentation

This folder contains the source files, and build scripts to generate
the documentation viewable at:

https://fragmuffin.github.io/cqparts/doc/

## Build Script

Build, host, and publish with the `go.sh` script in this directory...
Not a very creative name, I know, but it does the job.

    Usage: ./go.sh {clean|web|...}

    Helper script to perorm common documentation operations

    Arguments:

        clean   deletes _build directory for a forced clean build
        web     start http service at: http://localhost:9040 to view docs
        publish mirror build directory to docs for publishing
        test    run documented code as testcases

        Build:
            build       make sphinx docs
            build api   generate api sphinx rst sources
            build all   clean, then make everything

Note: use the `web` sub-command to host a http service and display the built
documentation. This is necessary to view anything displayed by a
_three.js loader_, they don't support the `file://` protocol (not sure why).
