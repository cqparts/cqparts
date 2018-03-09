import os
import tempfile
import mock

from base import CQPartsTest
from base import testlabel

from partslib import Box

# Unit under test
from cqparts.catalogue import JSONCatalogue
from cqparts.errors import SearchNoneFoundError, SearchMultipleFoundError


class JSONCatalogueTests(CQPartsTest):
    def setUp(self):
        self.filename = tempfile.mkstemp()[1]

    def tearDown(self):
        os.unlink(self.filename)

    def get_catalogue(self):
        return JSONCatalogue(self.filename)

    def populate_catalogue(self, catalogue):
        catalogue.add('id1', Box(length=20), criteria={'a': 0, 'b': 1})
        catalogue.add('id2', Box(width=20), criteria={'a': 0, 'b': 2})
        catalogue.add('id3', Box(height=20), criteria={'a': 1, 'b': 2})

    def test_init_status(self):
        c = self.get_catalogue()
        self.assertEqual(c.db.tables(), set([
            'items',
            JSONCatalogue._dbinfo_name,
        ]))
        self.assertEqual(len(c.db.table('items').all()), 0)
        self.assertEqual(len(c.db.table('_default').all()), 0)

    def test_clean(self):
        c = JSONCatalogue(self.filename)
        self.populate_catalogue(c)
        self.assertGreater(len(c.items.all()), 0)
        c.close()
        c = JSONCatalogue(self.filename, clean=True)  # should clear catalogue
        self.assertEquals(len(c.items.all()), 0)

    @mock.patch('tinydb.TinyDB')
    def test_name(self, mock_tinydb):
        c = self.get_catalogue()
        self.assertTrue(bool(c.name))

    def test_dbinfo_table(self):
        # open new catalogue
        c = self.get_catalogue()
        self.assertIn(c._dbinfo_name, c.db.tables())
        self.assertEqual(len(c._dbinfo_table.all()), 1)

        self.assertIsInstance(c.dbinfo, dict)
        self.assertEquals(c.dbinfo['lib'], 'cqparts')

        # manually change content
        table = c._dbinfo_table
        table.update({'lib': 'TEST_CONTENT'})

        # re-open and confirm dbinfo content isn't clobbered
        c.close()
        c = self.get_catalogue()

        self.assertEqual(len(c._dbinfo_table.all()), 1)  # still just 1 entry
        self.assertEquals(c.dbinfo['lib'], 'TEST_CONTENT')

    def test_add_single_item(self):
        c = self.get_catalogue()
        self.assertEqual(len(c.items.all()), 0)

        for (id_str, count) in [('id1', 1), ('id2', 2)]:
            # add box to db, make sure it was added
            c.add(id_str, Box())
            self.assertEqual(len(c.items.all()), count)
            item = c.items.all()[count - 1]
            self.assertEqual(item['id'], id_str)
            self.assertEqual(item['criteria'], {})
            # object serialization tests are out of scope
            self.assertEqual(set(item['obj'].keys()), set(['params', 'class', 'lib']))

    def test_add_duplicate_id(self):
        c = self.get_catalogue()
        c.add('id1', Box())
        self.assertRaises(ValueError, c.add, 'id1', Box())

    def test_add_replace_id(self):
        c = self.get_catalogue()
        c.add('id1', Box(), criteria={'try': 1, 'old': 'foo'})
        c.add('id1', Box(), criteria={'try': 2, 'new': 'bar'}, force=True)
        self.assertEqual(len(c.items.all()), 1)
        item = c.items.all()[0]
        self.assertNotIn('old', item['criteria'])
        self.assertIn('new', item['criteria'])

    def test_add_not_component(self):
        c = self.get_catalogue()
        self.assertRaises(TypeError, c.add, 'foo', 'not_a_component')

    def test_search(self):
        c = self.get_catalogue()
        self.populate_catalogue(c)

        id_set = lambda r: set(map(lambda i: i['id'], r))
        item = c.get_query()

        results = c.search(item.criteria.a == 0)  # 2 results
        self.assertEquals(id_set(results), set(['id1', 'id2']))

        results = c.search(item.criteria.a == 100)  # no results
        self.assertEquals(len(results), 0)

    def test_find(self):
        c = self.get_catalogue()
        self.populate_catalogue(c)
        item = c.get_query()
        result = c.find(item.criteria.a == 1)
        result['id'] == 'id1'

    def test_find_noresult(self):
        c = self.get_catalogue()
        self.populate_catalogue(c)
        item = c.get_query()
        self.assertRaises(SearchNoneFoundError, c.find, item.criteria.a == 100)

    def test_find_multipleresults(self):
        c = self.get_catalogue()
        self.populate_catalogue(c)
        item = c.get_query()
        self.assertRaises(SearchMultipleFoundError, c.find, item.criteria.a == 0)

    def test_deserialize(self):
        c = self.get_catalogue()
        c.add('id1', Box())
        c.close()

        # re-open catalogue
        c = self.get_catalogue()
        i = c.get_query()
        item = c.find(i.id == 'id1')
        obj = c.deserialize_item(item)
        self.assertIsInstance(obj, Box)

    def test_get(self):
        c = self.get_catalogue()
        c.add('id1', Box())
        i = c.get_query()
        obj = c.get(i.id == 'id1')
        self.assertIsInstance(obj, Box)
