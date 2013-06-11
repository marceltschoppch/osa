.. include:: links.rst

.. _api:

API index
=========

.. _client:

Client
^^^^^^

.. automodule:: osa.client
   :show-inheritance:
   :members:

.. _wsdl:

WSDL parser
^^^^^^^^^^^

.. automodule:: osa.wsdl
   :show-inheritance:
   :members:

.. automodule:: osa.xmlschema
   :show-inheritance:
   :members:

.. _methods:

Methods wrapper
^^^^^^^^^^^^^^^

.. automodule:: osa.message
   :show-inheritance:
   :members:

.. automodule:: osa.method
   :show-inheritance:
   :members:

.. _types

XML types
^^^^^^^^^
.. autoclass:: osa.xmltypes.XMLType
   :show-inheritance:
   :members:

.. autoclass:: osa.xmltypes.XMLString
   :show-inheritance:
   :members:

.. autoclass:: osa.xmltypes.XMLInteger
   :show-inheritance:
   :members:

.. autoclass:: osa.xmltypes.XMLDouble
   :show-inheritance:
   :members:

.. autoclass:: osa.xmltypes.XMLBoolean
   :show-inheritance:
   :members:

.. autoclass:: osa.xmltypes.XMLAny
   :show-inheritance:
   :members:

.. autoclass:: osa.xmltypes.XMLDecimal
   :show-inheritance:
   :members:

.. autoclass:: osa.xmltypes.XMLDate
   :show-inheritance:
   :members:

.. autoclass:: osa.xmltypes.XMLDateTime
   :show-inheritance:
   :members:

.. py:class:: osa.xmltypes.ComplexTypeMeta

    Metaclass to create complex types on the fly.

    .. py:method:: __new__(name, bases, attributes)

        Method to create new types.

        _children attribute must be present in attributes. It describes
        the arguments to be present in the new type. The he
        _children argument must be a list of the form:
        [{'name':'arg1', 'min':1, 'max':1, 'type':ClassType}, ...]

        Parameters
        ----------
        cls : this class
        name : str
            Name of the new type.
        bases : tuple
            List of bases classes.
        attributes : dict
            Attributes of the new type.

.. _soap stuff:

SOAP constants
^^^^^^^^^^^^^^

.. automodule:: osa.soap
   :show-inheritance:
   :members:
