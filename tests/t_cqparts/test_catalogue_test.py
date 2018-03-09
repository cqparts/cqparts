

from cqparts.utils.test import CatalogueTest
from cqparts.catalogue import JSONCatalogue

catalogue = JSONCatalogue('test-files/catalogue.json')
CatalogueTest.create_from(catalogue, add_to=globals())
