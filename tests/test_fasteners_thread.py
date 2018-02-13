
from base import testlabel

from cqparts.utils.test import CatalogueTest
from cqparts.catalogue import JSONCatalogue

catalogue = JSONCatalogue('test-files/thread_catalogue.json')
cls = testlabel('complex_thread')(CatalogueTest.create_from(catalogue))
globals()[cls.__name__] = cls
