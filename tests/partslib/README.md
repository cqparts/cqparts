# Test Parts Library

This is a mini parts library for testing.

## Avoid use in low-level testing

These *components* are to be imported as high level stimulus.

All expectations of a test-case using these parts must do so with the
following assumptions:

* `Part` class and all its functions are verified
* `Assembly` class and all its functions are verified
* `cqparts.search` functionality is verified

Failing to do so may yield false passes, and mask underlying errors.
