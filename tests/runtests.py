#!/usr/bin/env python

import unittest
import re
import functools


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
        super(MyTestRunner, self).run(suite)


if __name__ == "__main__":

    import argparse

    # ---- create commandline parser
    parser = argparse.ArgumentParser(description='Find and run cqparts tests.')

    label_list_type = lambda v: re.split(r'\W+', v)

    # skip labels
    group = parser.add_argument_group(
        "Skip tests",
        description="tests can be shown, but execution skipped based on their label",
    )
    group.add_argument(
        '-s', '--dontskip', dest='skip_whitelist',
        type=label_list_type, default=[],
        help="list of labels to test (skip all others)",
    )
    group.add_argument(
        '-ds', '--skip', dest='skip_blacklist',
        type=label_list_type, default=[],
        help="list of labels to skip",
    )

    # ignore labels
    group = parser.add_argument_group(
        "Ignore tests",
        description="tests can be ignored based on their label",
    )
    group.add_argument(
        '-i', '--dontignore', dest='ignore_whitelist',
        type=label_list_type, default=[],
        help="list of labels to test (ignore all others)",
    )
    group.add_argument(
        '-di', '--ignore', dest='ignore_blacklist',
        type=label_list_type, default=[],
        help="list of labels to ignore",
    )

    args = parser.parse_args()

    # ---- Discover and run tests
    # Load tests
    loader = unittest.TestLoader()
    tests = loader.discover('.', pattern='test_*.py')

    # Run tests
    testRunner = MyTestRunner(
        skip_blacklist=args.skip_blacklist,
        skip_whitelist=args.skip_whitelist,
        ignore_blacklist=args.ignore_blacklist,
        ignore_whitelist=args.ignore_whitelist,
        verbosity=2,
    )
    testRunner.run(tests)
