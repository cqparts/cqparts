
.. _fasteners.easy-install.catalogue:

.. currentmodule:: cqparts_fasteners.utils


Catalogue Selected Fastener
-----------------------------------

In the last section (:ref:`fasteners.easy-install.exact`), we used the analysis
from the :class:`VectorEvaluator` to precicely create a ``WoodScrew`` with
exactly the right dimensions.

The problem with this strategy is that a screw with those exact dimensions is
unlikely to exist, and would need to be custom made.

As an alternative, we can change the :class:`Selector` to pick a screw from
a list, more specifically, a :ref:`cqparts.catalogue`.


Populate a Catalogue
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

First we need to create an empty :class:`JSONCatalogue <cqparts.catalogue.JSONCatalogue>`.

::

    from cqparts.catalogue import JSONCatalogue
    import tempfile

    # Temporary catalogue (just for this script)
    catalogue_filename = tempfile.mkstemp()[1]
    catalogue = JSONCatalogue(catalogue_filename)

Now we'll add some screws to the *catalogue*:

::

    # Add screws to catalogue
    #   note: this is the kind of information you'd store in a csv
    #   file, then import with a script similar to this one, to convert that
    #   information to a Catalogue.
    screws = [
        {
            'id': 'screw_30',
            'obj_params': {  # parameters to WoodScrew constructor
                'neck_exposed': 5,
                'length': 40,  # exposing 10mm of thread
                'neck_length': 30,
            },
            'criteria': {
                'type': 'screw',
                'thread_length': 10,
                'compatible_anchor': 'anchor_10',
            },
        },
        {
            'id': 'screw_50',
            'obj_params': {
                'neck_exposed': 6,
                'length': 65,  # exposing 15mm of thread
                'neck_length': 50,

            },
            'criteria': {
                'type': 'screw',
                'thread_length': 15,
                'compatible_anchor': 'anchor_15',
            },
        },
    ]
    for screw in screws:
        obj = WoodScrew(**screw['obj_params'])
        catalogue.add(id=screw['id'], criteria=screw['criteria'], obj=obj)

And some *anchors*:

::

    # Add anchors to catalogue
    anchors = [
        {
            'id': 'anchor_10',
            'obj_params': {  # parameters to WoodScrew constructor
                'diameter': 10,
                'height': 7,
            },
            'criteria': {'type': 'anchor'},
        },
        {
            'id': 'anchor_15',
            'obj_params': {  # parameters to WoodScrew constructor
                'diameter': 15,
                'height': 10,
            },
            'criteria': {'type': 'anchor'},
        },
    ]
    for anchor in anchors:
        obj = Anchor(**anchor['obj_params'])
        catalogue.add(id=anchor['id'], criteria=anchor['criteria'], obj=obj)

Then :meth:`close() <cqparts.catalogue.JSONCatalogue.close>` the *catalogue* to
commit the items we've added to file.

To learn more about catalogues, read: :ref:`cqparts.catalogue`.


Catalogue Selector
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Our previous implementation of the :class:`Fastener <cqparts_fasteners.Fastener>`
in :ref:`fasteners.easy-install.exact` can mostly be salvaged, so we'll inherit
from it, but just change how the *screw* and *anchor* components are selected
and instantiated (in the overridden
:meth:`get_components() <Selector.get_components>` method).


::

    from cqparts.catalogue import JSONCatalogue
    from cqparts.utils import property_buffered

    class EasyInstallCatalogueFastener(EasyInstallFastener):

        class Selector(EasyInstallFastener.Selector):

            def get_components(self):
                # Find minimum neck length (total effect length, minus last effect)
                neck_length_min = abs(self.evaluator.eval[-1].start_point - self.evaluator.eval[0].start_point)
                thread_length_max = abs(self.evaluator.eval[-1].end_point - self.evaluator.eval[-1].start_point)

                # Get the catalogue of available items
                catalogue = JSONCatalogue(catalogue_filename)
                item = catalogue.get_query()

                # Find viably sized wood-screw
                screw_item = sorted(
                    catalogue.search(
                        # eval sets minimum evaluation length
                        (item.obj.params.neck_length >= neck_length_min) &
                        # thread shouldn't pierce through last part
                        (item.criteria.thread_length < thread_length_max)
                    ),
                    # sort by shortest first
                    key=lambda x: x['obj']['params']['neck_length']
                )[0]  # first result; shortest screw

                return {
                    'screw': catalogue.deserialize_result(screw_item),
                    'anchor': catalogue.get(
                        item.id == screw_item['criteria']['compatible_anchor']
                    ),
                }

Result
^^^^^^^^^^^^^

Now, to re-use everything else we've done, we can inherit from
``ConnectedPlanks`` but use a different *fastener* class:

::

    class ConnectedPlanksCatalogue(ConnectedPlanks):
        fastener_class = EasyInstallCatalogueFastener

.. raw:: html

    <iframe class="model-display"
        src="../../_static/iframes/easy-install/connected_catalogue.html"
        height="300px" width="100%"
    ></iframe>
