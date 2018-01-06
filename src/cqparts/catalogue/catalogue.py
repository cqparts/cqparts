
from .. import __version__
from .. import Component
from ..errors import SearchError, SearchNoneFoundError, SearchMultipleFoundError
from ..params import ParametricObject

import tinydb


class Catalogue(object):
    """
    A catalogue is a simple file-based database to store parametric combinations
    for components.

    **Analogy**

    If a :class:`Component <cqparts.Component>` is a *blueprint*, the *parameters*
    of its inherited :class:`ParametricObject <cqparts.params.ParametricObject>`
    are the *measurements*, or *metrics* corresponding to the *blueprint*.

    A :class:`Catalogue` is an exhaustive list of all parameter combinations,
    for the context of manufacture, or purchase.

    **Storage**

    A catalogue is represented in a single ``json`` file, using :mod:`tinydb`
    to read & write.

    **Usage**

    .. doctest::

        >>> # temporary file (for demonstration purposes)
        >>> import tempfile
        >>> filename = tempfile.mktemp()

        >>> # Instantiate Catalogue
        >>> from cqparts.catalogue import Catalogue
        >>> catalogue = Catalogue(filename)

        >>> # Add a couple of items
        >>> from cqparts_misc.basic.primatives import Box
        >>> for length in [10, 20, 30]:
        ...     name = "box_L%g" % length
        ...     box = Box(length=length)
        ...     index = catalogue.add(
        ...         id=name,
        ...         criteria={
        ...             'type': 'box',
        ...             'lengthcode': 'L%g' % length,
        ...         },
        ...         obj=box
        ...     )

        >>> # Searching
        >>> item = catalogue.get_query()
        >>> result = catalogue.find(item.id == 'box_L20')
        >>> result.keys()
        [u'obj', u'id', u'criteria']
        >>> result['obj']['params']['length']
        20.0

        >>> # Creating object
        >>> catalogue.deserialize_result(result)
        <Box: height=1.0, length=20.0, width=1.0>

        >>> # Search and deserialize in one line
        >>> catalogue.get(item.obj.params.length > 25)
        <Box: height=1.0, length=30.0, width=1.0>

        >>> # cleanup temporary file
        >>> import os
        >>> os.unlink(filename)

    .. note::

        All searching is done by :mod:`tinydb`, so :meth:`search`, :meth:`find`
        and :meth:`get_query` are simply pass-throughs to the underlying
        :class:`tinydb.TinyDB` instance in the ``db`` attribute of this class.

        Please read the :mod:`tinydb` documentation, and query the database
        directly with this classes ``db`` attribute.

    Each catalogue item is stored in an ``items`` table within the database.

    The ``items`` *table* is stored as a list, one of the elements stored in the
    above example may be stored like this::

        {
            'id': 'box_L20',
            'criteria': {'lengthcode': 'L20', 'type': 'box'},
            'obj': {
                'class': {
                    'module': 'cqparts_misc.basic.primatives',
                    'name': 'Box',
                },
                'lib': {
                    'name': 'cqparts',
                    'version': '0.1.0',
                },
                'params': {
                    '_render': {'alpha': 1.0, 'color': [192, 192, 192]},
                    '_simple': False,
                    'height': 1.0,
                    'length': 20.0,
                    'width': 1.0,
                }
            }
        }

    """

    # database information
    _version = '0.1'
    _dbinfo_name = '_dbinfo'

    def __init__(self, filename):
        self.db = tinydb.TinyDB(filename)
        self.items = self.db.table('items')

        if self._dbinfo_name not in self.db.tables():
            # info table does not exist; database is new.
            dbinfo_table = self.db.table(self._dbinfo_name)
            dbinfo_table.insert({
                'module': type(self).__module__,
                'name': type(self).__name__,
                'ver': self._version,
                'lib': 'cqparts',
                'lib_version': __version__,
            })

    def close(self):
        self.db.close()

    @property
    def dbinfo_table(self):
        return self.db.table(self._dbinfo_name)

    @property
    def dbinfo(self):
        return self.dbinfo_table.all()[0]

    def get_query(self):
        """
        Passthrough to return a :class:`tinydb.Query` instance.
        (mostly implemented so importing :mod:`tinydb` is not mandatory to
        search the catalogue)

        :return: :mod:`tinydb` query instance
        :rtype: :class:`tinydb.Query`
        """
        return tinydb.Query()

    # ------- Searching -------
    def search(self, *args, **kwargs):
        """
        Passthrough to :meth:`Table.search() <tinydb.database.Table.search
        for the ``items`` table.

        So ``c.search(...)`` equivalent to ``c.db.table('items').search(...)``.

        :return: entries in ``items`` table that positively match given search criteria.
        :rtype: :class:`list` of ``items`` table entries
        """
        return self.items.search(*args, **kwargs)

    def find(self, *args, **kwargs):
        """
        Performs the same action as :meth:`search` but asserts a single result.

        :return:

        :raises SearchNoneFoundError: if nothing was found
        :raises SearchMultipleFoundError: if more than one result is found
        """
        result = self.search(*args, **kwargs)

        if len(result) == 0:
            raise SearchNoneFoundError("nothing found")
        elif len(result) > 1:
            raise SearchMultipleFoundError("more than one result found")

        return result[0]

    # ------- Adding items -------
    def add(self, id, criteria, obj, force=False):
        """
        Add a :class:`Component <cqparts.Component>` instance to the database.

        :param id: unique id of entry, can be anything
        :type id: :class:`str`
        :param criteria: arbitrary search criteria for the entry
        :type criteria: :class:`dict`
        :param obj: component to be serialized, then added to the catalogue
        :type obj: :class:`Component <cqparts.Component>`
        :param force: if ``True``, entry is forcefully overwritten if it already
                      exists. Otherwise an exception is raised
        :type force: :class:`bool`

        :raises TypeError: on parameter issues
        :raises ValueError: if a duplicate db entry is detected (and ``force``
                            is not set)

        :return: index of new entry
        :rtype: :class:`int`
        """
        # Verify component
        if not isinstance(obj, Component):
            raise TypeError("can only add(%r), component is a %r" % (
                Component, type(obj)
            ))

        # Serialize object
        obj_data = obj.serialize()

        # Add to database
        q = tinydb.Query()
        if self.items.count(q.id == id):
            if force:
                self.items.remove(q.id == id)
            else:
                raise ValueError("entry with id '%s' already exists" % (id))

        index = self.items.insert({
            'id': id,  # must be unique
            'criteria': criteria,
            'obj': obj_data,
        })

        return index

    # ------- Getting Items -------
    def deserialize_result(self, data):
        """
        Create a :class:`Component <cqparts.Component>` from a database
        search result.

        :param data: result from :meth:`find`, or an element of :meth:`search`
        :type data: :class:`dict`
        :return: deserialized object instance
        :rtype: :class:`Component <cqparts.Component>`
        """
        return ParametricObject.deserialize(data['obj'])

    def get(self, *args, **kwargs):
        """
        Combination of :meth:`find` and :meth:`deserialize_result`;
        the result from :meth:`find` is deserialized and returned.

        Input is a :mod:`tinydb` query.

        :return: deserialized object instance
        :rtype: :class:`Component <cqparts.Component>`
        """
        result = self.find(*args, **kwargs)
        return self.deserialize_result(result)
