
Logo
==========

Making the logo awesome.

.. todo:: build the ``cqparts`` logo using ``cqparts``


CQ Block
--------

Block
^^^^^^

Text
^^^^^

Text is converted from the logo's SVG to *wires*, which are then either used to:

* extrude to make a solid
* cut into a solid

.. note::

    **SVG Assumptions:**

    * text is converted to path
    * the words "cq" and "path" are grouped paths
    * group ``id`` contains the word "text", of which there are only 2 (in order)
    * paths only use `quadratic bézier <https://en.wikipedia.org/wiki/B%C3%A9zier_curve#Quadratic_B.C3.A9zier_curves>`_ splines, and linear.

Parts Block
-----------

Block
^^^^^

Thread
^^^^^^^
