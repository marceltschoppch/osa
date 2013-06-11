.. include:: links.rst
.. osa documentation master file
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to osa's documentation!
===================================

*osa* is a fast/slim library to consume `WSDL 1.1`_/`SOAP 1.1`_ services.
It is created with the following three requirements in mind: fast calls,
small memory footprint and convenience of use. I was not able to find a library
that meets all my requirements, especially for large messages (millions of
elements). Therefore I created this library by combining ideas found in
`suds`_ (nice printing), `soaplib`_ (serialization/deserialization) and
`Scio`_ (`WSDL 1.1`_ parsing).

At the moment the library is limited to wrapped document/literal `SOAP 1.1`_
convention. To include other call conventions one has to extend the
:py:func:`to_xml` and :py:func:`from_xml` methods of the :py:class:`Message`
:ref:`class <message>`. The structure of the library is briefly explained
:ref:`here <Structure>`. The *XML* processing is performed with the
help of :py:mod:`cElementTree` module.

To install the library please do the usual *Python* magic::

    >>> python setup.py install

Online help is available for all classes, please see also section
:ref:`using` for examples.

Contents:

.. toctree::
    :maxdepth: 2

    overview
    api
    license



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

