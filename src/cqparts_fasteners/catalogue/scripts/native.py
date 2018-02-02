#!/usr/bin/env python

import os
import argparse
import itertools
import fnmatch

# cqparts
import cqparts
from cqparts.catalogue import JSONCatalogue

# cqparts_fasteners
import cqparts_fasteners
import cqparts_fasteners.bolts
import cqparts_fasteners.screws

# -------- Mapping


# --------- Iterators

def iter_diam_length(diameters, lengths, ratio_limits):
    """
    Iterate through all combinations of diameters & lengths, given a limited
    ratio between the two.
    """
    for (diam, length) in itertools.product(diameters, lengths):
        if ratio_limits[0] <= (float(length) / diam) <= ratio_limits[1]:
            yield (diam, length)


# --------- Component Catalogue Generators

class CatalogueGenerator(object):
    name = None
    catalogue_class = JSONCatalogue

    @classmethod
    def get_catalogue(cls, **kwargs):
        filename = os.path.join('..', 'native-%s.json' % cls.name)
        return cls.catalogue_class(filename, **kwargs)

    @classmethod
    def iter_components(cls):
        # must yield the format:
        #   (<id>, <criteria dict>, <component>)
        return iter(()) # nothing yielded by default

    @classmethod
    def generate_catalogue(cls):
        catalogue = cls.get_catalogue()
        for (idval, criteria, component) in cls.iter_components():
            catalogue.add(
                id=idval,
                obj=component,
                criteria=criteria,
                _check_id=False,
            )


class WoodScrews(CatalogueGenerator):
    name = 'woodscrews'

    drives = ['phillips', 'slot']
    diameters = [1.524, 1.8542, 2.1844, 2.5146, 2.8448, 3.175, 3.5052, 3.8354, 4.1656, 4.4958, 4.826, 5.4864, 6.1468, 6.8072, 7.4676, 8.128]
    lengths = [6.35, 9.525, 12.7, 15.875, 19.05, 22.225, 25.4, 31.75, 38.1, 44.45, 50.8, 57.15, 63.5, 76.2, 88.9, 101.6, 127, 152.4]
    ratio_limits = (2, 18)  # (min, max) of (length / diameter)

    #@classmethod
    #def iter_components(cls):
    #    param_iter = itertools.product(
    #        iter_diam_length( # (diam, length)
    #            diameters=cls.diameters,
    #            lengths=cls.lengths,
    #            ratio_limits=cls.ratio_limits,
    #        ),
    #        cls.drives,
    #    )
    #    for (idval, ((diam, length), drive_type)) in enumerate(param_iter):
    #        # FIXME



class HexBolts(CatalogueGenerator):
    name = 'bolts'

    diameters = [4, 5, 6, 8, 10, 12, 14, 16]
    lengths = [5, 8, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200]
    ratio_limits = (1, 20)  # (min, max) of (length / diameter)

    head_map = {  # format: {<thread diam>: (<head width>, <head height>, ... }
        # note: head height = (0.63 * diam) # TODO: base on better information?
        4: (7, 2.52),
        5: (8, 3.15),
        6: (10, 3.78),
        8: (13, 5.04),
        10: (16, 6.3),
        12: (18, 7.56),
        14: (21, 8.82),
        16: (24, 10.08),
        20: (30, 12.6),
    }

    @classmethod
    def iter_components(cls):
        param_iter = iter_diam_length(
            diameters=cls.diameters,
            lengths=cls.lengths,
            ratio_limits=cls.ratio_limits,
        )
        for (idval, (diam, length)) in enumerate(param_iter):

            component = cqparts_fasteners.bolts.Bolt(
                head=('hex', {
                    'width': cls.head_map[diam][0],
                    'height': cls.head_map[diam][1],
                    'washer': False,
                }),
                thread=('iso68', {
                    'diameter': diam,
                    'pitch': 1,  # FIXME
                }),
                length=length,
                neck_length=0,
            )

            criteria = {}
            yield (idval, criteria, component)


CATALOGUE_GENERATORS = [
    WoodScrews,
    HexBolts,
]
CATALOGUE_GEN_MAP = {cls.name: cls for cls in CATALOGUE_GENERATORS}



# ---------- Command-line Arguments Parser ----------

parser = argparse.ArgumentParser(
    description="Build catalogue of common fasteners, not based on a specific store",
)

def catalogues_list_type(value):
    catalogues_all = set(c.name for c in CATALOGUE_GENERATORS)
    catalogues = set()
    for filter_str in value.split(','):
        catalogues |= set(fnmatch.filter(catalogues_all, filter_str))
    return sorted(catalogues)

parser.add_argument(
    '--catalogues', '-c', dest='catalogues',
    type=catalogues_list_type, default=catalogues_list_type('*'),
    help="csv list of catalogues to act on",
)

parser.add_argument(
    '--list', '-l', dest='list',
    default=False, action='store_const', const=True,
    help="list catalogues to build",
)

args = parser.parse_args()


# list catalogues & exit
if args.list:
    print("Catalogues:")
    for name in args.catalogues:
        print("  - %s" % name)
    exit(0)


# ---------- Generate Catalogues ----------
for name in args.catalogues:
    cls = CATALOGUE_GEN_MAP[name]
    print("----- Build: %s" % name)

    cls.generate_catalogue()
