from collections import defaultdict

from base import CQPartsTest
from base import testlabel

from partslib import Box, Cylinder

# Unit under test
import cqparts
from cqparts.search import register
from cqparts.search import search, find
from cqparts.search import common_criteria

from cqparts.errors import SearchNoneFoundError, SearchMultipleFoundError


class ClearSearchIndexTests(CQPartsTest):
    def setUp(self):
        super(ClearSearchIndexTests, self).setUp()

        # retain original values
        self.orig_index = cqparts.search.index
        self.orig_class_list = cqparts.search.class_list

        # clear values
        cqparts.search.index = defaultdict(lambda: defaultdict(set))
        cqparts.search.class_list = set()

    def tearDown(self):
        super(ClearSearchIndexTests, self).tearDown()
        # restore original values
        cqparts.search.index = self.orig_index
        cqparts.search.class_list = self.orig_class_list


class RegisterTests(ClearSearchIndexTests):

    def test_register(self):
        _Box = register(a=1, b=2)(Box)
        self.assertEqual(cqparts.search.index, {
            'a': {1: set([Box])},
            'b': {2: set([Box])},
        })
        self.assertEqual(cqparts.search.class_list, set([Box]))

    def test_register_duplicate_criteria(self):
        _Box = register(a=1, b=2)(Box)
        _Cyl = register(b=2, c=3)(Cylinder)
        self.assertEqual(cqparts.search.index, {
            'a': {1: set([Box])},
            'b': {2: set([Box, Cylinder])},
            'c': {3: set([Cylinder])},
        })
        self.assertEqual(cqparts.search.class_list, set([Box, Cylinder]))


class SearchFindTests(ClearSearchIndexTests):

    def setUp(self):
        super(SearchFindTests, self).setUp()
        self.Box = register(a=1, b=2)(Box)
        self.Cyl = register(b=2, c=3)(Cylinder)

    def test_search_single(self):
        self.assertEqual(search(a=1), set([self.Box]))
        self.assertEqual(search(c=3), set([self.Cyl]))

    def test_search_multiple(self):
        self.assertEqual(search(b=2), set([self.Box, self.Cyl]))

    def test_search_noresults(self):
        self.assertEqual(search(a=10), set())

    def test_find(self):
        self.assertEqual(find(a=1), self.Box)
        self.assertEqual(find(c=3), self.Cyl)

    def test_find_multiple(self):
        with self.assertRaises(SearchMultipleFoundError):
            find(b=2)

    def test_find_noresults(self):
        with self.assertRaises(SearchNoneFoundError):
            find(a=10)


class CommonCriteriaTests(ClearSearchIndexTests):
    def test_common_criteria(self):
        def foo(**kwargs):
            return kwargs
        self.assertEqual(foo(a=1), {'a': 1})
        bar = common_criteria(b=2)(foo)
        self.assertEqual(bar(a=1), {'a': 1, 'b': 2})
