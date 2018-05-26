#!/usr/bin/env python

# Catalogue Usage example:
#   >>> from cqparts.catalogue import JSONCatalogue
#   >>> import cqparts_motors
#   >>> filename = os.path.join(
#   ...     os.path.dirname(cqparts_motors.__file__),
#   ...     'catalogue', 'dcmotor.json',
#   ... )
#   >>> catalogue = JSONCatalogue(filename)
#   >>> item = catalogue.get_query()
#   >>> dc = catalogue.get(item.criteria.size == 304)
#   >>> from cqparts.display import display
#   >>> display(dc)

import os

import cqparts
from cqparts.catalogue import JSONCatalogue

# DC Motor 
from cqparts_motors.dc import DCMotor


CATALOGUE_NAME = 'dcmotor.json'

# DC Motor hobby examples

DC_HOBBY = {

}

# Generate Catalogue
catalogue = JSONCatalogue(
    filename=os.path.join('..', CATALOGUE_NAME),
    clean=True,  # starts fresh
)

# Create Motors 
for (size, params) in DC_HOBBY.items():
    catalogue.add(
        id='DC_MOTOR%i' % size,
        obj=DCMotor(**params),
        criteria={
            'type': 'motor',
            'class': 'dc',
            'size': size,
        },
    )
