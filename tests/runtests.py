#!/usr/bin/env python

import sys
import unittest
import re
import functools
import logging
import mock
import os
import inspect
from contextlib import contextmanager

_this_path = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))


class MyTestRunner(unittest.runner.TextTestRunner):

    def __init__(self, *args, **kwargs):
        """
        Append blacklist & whitelist attributes to TestRunner instance
        """
        # skip
        self.skip_whitelist = set(kwargs.pop('skip_whitelist', []))
        self.skip_blacklist = set(kwargs.pop('skip_blacklist', []))
        # ignore
        self.ignore_whitelist = set(kwargs.pop('ignore_whitelist', []))
        self.ignore_blacklist = set(kwargs.pop('ignore_blacklist', []))


        super(MyTestRunner, self).__init__(*args, **kwargs)

    @classmethod
    def test_iter(cls, suite):
        """
        Iterate through test suites, and yield individual tests
        """
        for test in suite:
            if isinstance(test, unittest.TestSuite):
                for t in cls.test_iter(test):
                    yield t
            else:
                yield test

    def run(self, testlist):
        # Change given testlist into a TestSuite
        suite = unittest.TestSuite()

        # Add each test in testlist, apply skip mechanism if necessary
        for test in self.test_iter(testlist):

            # Determine if test should be IGNORED
            ignore = bool(self.ignore_whitelist)
            test_labels = getattr(test, '_labels', set())
            if test_labels & self.ignore_whitelist:
                ignore = False
            if test_labels & self.ignore_blacklist:
                ignore = True

            if not ignore:
                # Determine if test should be SKIPPED
                skip = bool(self.skip_whitelist)
                test_labels = getattr(test, '_labels', set())
                if test_labels & self.skip_whitelist:
                    skip = False
                if test_labels & self.skip_blacklist:
                    skip = True

                if skip:
                    # Test should be skipped.
                    #   replace original method with function "skip"
                    test_method = getattr(test, test._testMethodName)

                    # Create a "skip test" wrapper for the actual test method
                    @functools.wraps(test_method)
                    def skip_wrapper(*args, **kwargs):
                        raise unittest.SkipTest('label exclusion')
                    skip_wrapper.__unittest_skip__ = True
                    skip_wrapper.__unittest_skip_why__ = 'label exclusion'

                    setattr(test, test._testMethodName, skip_wrapper)

                suite.addTest(test)

        # Resume normal TextTestRunner function with the new test suite
        return super(MyTestRunner, self).run(suite)


@contextmanager
def readonly_tinydb(path=None):
    if path is None:
        # set path default, should be repository root
        path = os.path.realpath(os.path.join(_this_path, '..'))
    else:
        path = os.path.realpath(path)

    # __builtin__.open replcement method
    from codecs import open as codecs_open
    def _codecs_open_readonly(name, mode='r', **kwargs):
        if os.path.realpath(name).startswith(path):
            # file being used is in this repository
            return codecs_open(name, mode='r', **kwargs)  # ignore given mode; force read-only
        # otherwise, the file is probably in a temporary, read/writeable location
        return open(name, mode)

    with mock.patch('tinydb.storages.codecs.open', _codecs_open_readonly):
        with mock.patch('tinydb.storages.os.utime'):
            yield


# ------------------- mainline -------------------
if __name__ == "__main__":

    import argparse

    # ---- create commandline parser
    parser = argparse.ArgumentParser(description='Find and run cqparts tests.')

    label_list_type = lambda v: re.split(r'\W+', v)

    # test selection
    group = parser.add_argument_group("Test Selection")
    group.add_argument(
        '-p', '--pattern', dest='pattern', default='test_*',
        help="filename pattern",
    )
    group.add_argument(
        '-m', '--module', dest='module', default=None,
        help="only run tests from the 't_<module>' folder",
    )

    # label filtering
    group = parser.add_argument_group(
        "Label filters (skip & ignore)",
        description="tests can be skipped, or ignored based on their label",
    )
    group.add_argument(
        '-s', '--skip', dest='skip_blacklist',
        type=label_list_type, default=[],
        help="list of labels to skip",
    )
    group.add_argument(
        '-ds', '--dontskip', dest='skip_whitelist',
        type=label_list_type, default=[],
        help="list of labels to test (skip all others)",
    )
    group.add_argument(
        '-i', '--ignore', dest='ignore_blacklist',
        type=label_list_type, default=[],
        help="list of labels to ignore",
    )
    group.add_argument(
        '-di', '--dontignore', dest='ignore_whitelist',
        type=label_list_type, default=[],
        help="list of labels to test (ignore all others)",
    )

    # logging
    group = parser.add_argument_group("Logging")
    def logging_level_type(value):
        if hasattr(logging, value):
            # named type: DEBUG, INFO, WARN, ERROR, CRITICAL
            ret = getattr(logging, value)
            if isinstance(ret, int):
                return ret
        else:
            try:
                return int(value)
            except ValueError:
                pass
        raise argparse.ArgumentTypeError("bad logging level: %r" % value)

    group.add_argument(
        '-l', '--logginglevel', dest='logginglevel',
        type=logging_level_type, default=None,
        help="if specified, logging is enabled",
    )

    args = parser.parse_args()

    # enable logging
    if args.logginglevel:
        import cadquery
        cadquery.freecad_impl.console_logging.enable(
            level=args.logginglevel,
        )

    # ---- Discover and run tests
    # Load tests

    class MyLoader(unittest.TestLoader):
        ignore_modules = ['partslib']

        def _get_module_from_name(self, name):
            # ignore modules outside specific module test folder (if given)
            if args.module is not None:
                if not name.startswith('t_%s.' % args.module):
                    return None

            # ignore modules that are in the ignore list
            try:
                __import__(name)
                return sys.modules[name]
            except ImportError:
                if name in self.ignore_modules:
                    return None
                raise

    with readonly_tinydb():
        loader = MyLoader()
        tests = loader.discover(
            start_dir='.',
            pattern=args.pattern,
        )

        # Run tests
        testRunner = MyTestRunner(
            skip_blacklist=args.skip_blacklist,
            skip_whitelist=args.skip_whitelist,
            ignore_blacklist=args.ignore_blacklist,
            ignore_whitelist=args.ignore_whitelist,
            verbosity=2,
        )
        test_run = testRunner.run(tests)

        # Exit with 0 if tests were successful (else 1)
        return_code = not test_run.wasSuccessful()

    sys.exit(return_code)
