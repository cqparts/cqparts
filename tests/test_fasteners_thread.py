import unittest

from base import testlabel

from cqparts.utils.test import CatalogueTest
from cqparts.catalogue import JSONCatalogue

catalogue = JSONCatalogue('test-files/thread_catalogue.json')
cls = testlabel('complex_thread')(CatalogueTest.create_from(catalogue))

# FIXME: when #1 is fixed, remove this so tests are not permenantly skipped
cls = unittest.skip('skipped until #1 is fixed')(cls)

globals()[cls.__name__] = cls
