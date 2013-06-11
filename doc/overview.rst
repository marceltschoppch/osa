.. include:: links.rst

.. _using:

Using
--------
To use the library do the import::

    >>> import osa

This exposes the top level class :ref:`Client <client>`. It the only one
class used to consume a service by a normal user. The client
is initialized by full address of a `WSDL 1.1`_ document::

    >>> cl = osa.Client("http://.../HelloWorldService?wsdl")

Convenience print functions are available at several levels, e.g. to find information
about the client one can enter::

    >>> cl

which returns names of all found services in the `WSDL 1.1`_ document and
location of the service::

    service HelloWorldService from:
        http://.../HelloWorldService?wsdl

The top level client is a container for class definitions constructed from
*XML* types in the supplied `WSDL 1.1`_ focument and for remote method
wrappers. All types are contained in :py:attr:`cl.types` and all
methods are available through :py:attr:`cl.service`. It is again possible
to inspect them by printing::

    >>> cl.types

which lists all known types and help if available::

    Person
        no documentation
    Name
        no documentation
    ...

Similarly::

    >>> cl.service

prints all found methods and there short description if available::

    sayHello
        str[] result | None = sayHello(sayHello msg)
        str[] result | None = sayHello(Person person , int time...
    echoString
        str result  = echoString(echoString msg)
        str result  = echoString(str msg )
        str result  = echoString...
        ...

It is worth noting once more that if any documentation is available in
the initial `WSDL 1.1`_ document it is propagated to types and methods.

To create an instance of a type in :py:attr:`cl.types` is easy
(note that tab completion works both for types and methods)::

    >>> person = cl.types.Person()

To inspect the new instance simply print it::

    >>> person
    (Person){
    name = None (Name)
    weight = None (int)
    age = None (int)
    height = None (int)
    }

As can be seen all attributes of the new instance are empty, i.e.
they are :py:data:`None`. Expected types of attributes are
given after :py:data:`None` in the brackets. Sometimes it useful
to initialize immediately all obligatory (non-nillable) attributes.
To do this one can use :py:attr:`deep` keyword to class
constructors::

    >>> person = cl.types.Person(deep = True)

which initializes the whole hierarchy::

    (Person){
    name = (Name){
               firstName = 
               lastName = 
           }
    weight = 0
    age = 0
    height = 0
    }

The attributes can be set with the usual dot-convention::

    >>> person.name.firstName = "Osa"
    >>> person.name.lastName = "Wasp"

To call a method one can access it directly from :py:attr`cl.service`.
Help to a method can be viewed by simply printing its doc (*ipython* style)::

    >>> cl.service.sayHello ?

This shows possible call signatures and gives help from the
`WSDL 1.1`_ document::

    Type:             Method
    Base Class:       <class 'osa.methods.Method'>
    String Form:   str[] result | None = sayHello(sayHello msg)
    Namespace:        Interactive
    File:             /usr/local/lib/python2.6/site-packages/osa-0.1-py2.6.
    egg/osa/methods.py
    Docstring:
        str[] result | None = sayHello(sayHello msg)
        str[] result | None = sayHello(Person person , int times )
        str[] result | None = sayHello(person=Person , times=int )

                   says hello to person.name.firstName given number of times
                   illustrates usage of compex types

    ...

It is possible to call any method in four different formats:

- single input parameter with proper wrapper message for this functions
- expanded positional parameters: children of the wrapper message
- expanded keyword parameters
- mixture of positional and keyword parameters.

The help page shows all possible signatures with explained types.
On return the message is expanded so that a real output is returned
instead of the wrapper. The return type is also shown in the
help. Please note, that lists are used in place of arrays for any
types, this is shown by brackets :py:data:`[]`. Finally, let's
make the call::

    >>> cl.service.sayHello(person, 5)
    ['Hello, Osa', 'Hello, Osa', 'Hello, Osa', 'Hello, Osa', 'Hello, Osa']


The library can also handle *XML* :py:data:`anyType` properly in most of the
cases: *any* variable chooses the suitable type from the service and
uses it to do the conversion from *XML* to *Python*.

The library can be used with large messages, e.g about 8 millions of
double elements are processed in few tens of seconds only. The
transient peak memory consumption for such a message is of the order
of 1 GB.

.. _Structure:

Structure
---------
This section briefly explains the library structure. It is useful for
those who wants to improve it.

The top level :ref:`Client <client>` class is simply a container.
On construction it creates an instance of :ref:`WSDLParser <wsdl>`
and processes the service description by calling its
methods :py:func:`parse`. Afterwards
the parser is deleted. As a result of the initial processing
two dictionaries are available: containing newly created types
and methods.

Types and methods are generated by the :ref:`WSDLParser <wsdl>`, for types
it internally uses :ref:`XMLSchemaParser <wsdl>`.
The types are constructed by using meta-class :ref:`ComplexTypeMeta <types>`.
This meta-class has a special convention to pass children names and types.
The methods are wrapped as instances of :ref:`Method <methods>` class.
The latter class has a suitable :py:func:`__call__` method and contains
information about input and output arguments as instances of
the :ref:`Message <methods>` class in attributes :py:data:`input` and
:py:data:`output` correspondingly.

The top level :ref:`Client <client>` class creates sub-containers for
types and methods: :py:data:`types` and :py:data:`service`. This
containers have special print function to display help. Types and
methods are set as direct attributes of the corresponding
containers, so that the usual dot-access and tab-completion are
possible. The attributes of the :py:data:`types` container are
class definitions, so that to create a new instance one has
to add the brackets *()*. The attributes of
the :py:data:`service` container are callable method wrappers.

To allow a correct :py:data:`anyType` processing the
:ref:`WSDLParser <wsdl>` updates special dictionary of
:ref:`XMLAny <types>` class by all discovered classes.

Every function call is processed by :py:func:`__call__` method
of a :ref:`Method <methods>` instance. The call method uses
the input message :py:attr:`input` to convert its arguments to
*XML* string (:py:func:`to_xml`). Afterwards *urllib2* is used to send the
request to service. The service response is deserialized by
using the output message :py:attr:`output` (:py:func:`from_xml`).
The deserialized result is returned to the user.

The input points for serialization is a :ref:`Message <methods>`
instance. The message first analyzes the input arguments and
if required wraps them into a top level message. Afterwards
:py:func:`to_xml` methods of al children are called with a proper
*XML* element. The children create *XML* elements for them and
propagate the call to their children and so on. The process
is continued until the bottom of the hierarchy is reached.
Only the primitive :ref:`types` set the real text tag.
The deserialization process is similar: in this case
:py:func:`from_xml` is propagated and all children
classes are constructed. In addition the output message
parser expands the response wrapper, so that the user sees
the result without the shell.

At the moment only wrapped document/literal convention is realized.
The format of the message is determined by :py:func:`to_xml` and
:py:func:`from_xml`. Therefore, to introduce other conventions
(rpc, encoded) one has to modify these two methods only.

The library uses :py:mod:`cElementTree` module for *XML* processing.
This module has about 2 times lower memory footprint as the usual
:py:mod:`lxml` library.
