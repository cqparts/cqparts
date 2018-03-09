
from base import testlabel

from cqparts.utils.test import CatalogueTest
from cqparts.catalogue import JSONCatalogue

def add_catalogue(filename):
    catalogue = JSONCatalogue(filename)
    cls = testlabel('catalogue')(CatalogueTest.create_from(catalogue))
    globals()[cls.__name__] = cls


# BoltDepot catalogues
add_catalogue('../src/cqparts_template/catalogue/pegs.json')
