# client.py - client class, part of osa.
# Copyright 2013 Sergey Bozhenkov, boz at ipp.mpg.de
# Licensed under LGPLv3 or later, see the COPYING file.

"""
    Top level access to SOAP service.
"""

from . import xmlnamespace
from . import wsdl


def str_for_containers(self):
    """
        Nice printing for types and method containers.

        Containers must have _container attribute containing all
        elements to be printed.
    """
    cont = getattr(self, '_container', None)
    if cont is None:
        return ''
    res = ''
    for child in cont:
        descr = str(getattr(getattr(self, child, None), '__doc__', None))
        if len(descr) > 100:
            descr = descr[:100] + '...'
        descr = descr.replace('\n', '\n\t')
        res = res + '\n%s\n\t%s' % (child, descr)
    res = res[1:]
    return res


class Client(object):
    """
        Top level class to talk to soap services.

        This is an access point to service functionality. The client accepts
        WSDL address and uses `osa.wsdl.WSDLParser` to get all defined types and
        operations. The types are set to client.types and operations
        are set to self.service.

        To examine present types or operations simply print (or touch repr)::

            >>> client.types

        or::

            >>> client.service

        correspondingly.

        To create type simply call::

            >>> client.types.MyTypeName().

        Class constructor will also create all obligatory (non-nillable) children.
        To call an operation::

            >>> client.service.MyOperationName(arg1, arg2, arg3, ...),

        where arguments are of required types. Arguments can also
        be passed as keywords or a ready wrapped message.

        If any help is available in the WSDL document it is propagated to the
        types and operations, see e.g. help
        :py:attr:`client.types.MyTypeName`. In addition
        the help page on an operation displays its call signature.

        Nice printing is also available for all types defined in client.types::

            >>> print(client.types.MyTypeName())

        .. warning::
            Only document/literal wrapped convention is implemented at the moment.

        In reality client.types and client.service are simply containers.
        The content of these containers is set from results of parsing
        the wsdl document by
        `osa.wsdl.WSDLParser.get_types` and
        `osa.wsdl.WSDLParser.get_services` correspondingly.
        See also `osa.wsdl.WSDLParser.parse`.

        The client.types container consists of auto generated (by
        `osa.xmlschema.XMLSchemaParser`)
        class definitions. So that a call to a member returns and instance
        of the new type. New types are auto-generated according to a special
        convention by metaclass `osa.xmltypes.ComplexTypeMeta`.

        The client.service container consists of methods wrapers
        methods.Method. The method wrapper is callable with free number of
        parameters. The input and output requirements of a method are
        contained in methods.Message instances `osa.methods.Method.input` and
        `osa.methods.Method.output` correspondingly. On a call a method converts
        the input to XML by using Method.input, sends request to the
        service and finally decodes the response from XML by
        Method.output.

        Parameters
        ----------
        wsdl_url : str
            Address of wsdl document to consume.
    """
    def __init__(self, wsdl_url):
        #create parser and download the WSDL document
        self.wsdl_url = wsdl_url
        parser = wsdl.WSDLParser(wsdl_url)
        self._types, self._services = parser.parse()
        self.names = []
        self.create_types_container()
        self.create_services_containers()

        return

    def create_types_container(self):
        """
            Create types container class for easy access.

            As a result of this method, self.types contains
            all the defined classes with their short names,
            i.e. without namespace prefix. If a name collision
            is detected, the second and all consecutive classes
            are appended with a counter.
        """
        types = {}
        for k, v in self._types.items():
            short_name = xmlnamespace.get_local_name(k)
            if short_name in types:
                counter = 1
                while True:
                    new_name = '%s_%d' % (short_name, counter)
                    counter += 1
                    if not new_name in types:
                        short_name = new_name
                        break
            types[short_name] = v
        types['_container'] = list(types)
        types['__str__'] = str_for_containers
        types['__repr__'] = str_for_containers
        self.types = type('TypesDispatcher', (), types)()

    def create_services_containers(self):
        """
            Create methods containers for easy access.

            As a result of this method, self.service
            with available operations is created. If
            there are several services in the supplied
            wsdl, than self.service_1, self.service_2
            are created.
        """
        def create(name, attr_name, methods):
            """
                Do create.

                Parameters
                ----------
                name : nice server name
                attr_name : hot to attach service, i.e. self.service_1
                methods : dict of service methods
            """
            methods['_container'] = list(methods)
            methods['__str__'] = str_for_containers
            methods['__repr__'] = str_for_containers
            setattr(self, attr_name,
                    type('ServiceDispatcher', (), methods)())
            self.names.append('%s %s' % (attr_name, name))

        if len(self._services) == 1:
            l = list(self._services)
            create(l[0], 'service', self._services[l[0]])
        else:
            counter = 1
            for k, v in self._services.items():
                attr_name = 'service_%d' % counter
                counter += 1
                create(k, attr_name, v)

    def __str__(self):
        res = ''
        for name in self.names:
            res = res + ', %s' % name
        res = res[2:] + ' from:\n\t%s' % (self.wsdl_url)
        return res

    def __repr__(self):
        return self.__str__()
