
from base import testlabel

from cqparts.utils.test import CatalogueTest
from cqparts.catalogue import JSONCatalogue

def add_catalogue(filename):
    catalogue = JSONCatalogue(filename)
    cls = testlabel('catalogue')(CatalogueTest.create_from(catalogue))
    globals()[cls.__name__] = cls


# Stepper Catalogue(s)
add_catalogue('../src/cqparts_motors/catalogue/dc-motor.json')
add_catalogue('../src/cqparts_motors/catalogue/stepper-nema.json')
