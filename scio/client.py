"""
    Top level access to SOAP service.
"""

import wsdl
import xmltypes

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
        if len(descr)>100:
            descr = descr[:100] + "..."
        descr = descr.replace("\n", "\n\t")
        res = res + '\n%s\n\t%s' %(child, descr)
    res = res[1:]
    return res

class Client(object):
    """
        Top level class to talk to soap services.

        This is an access point to service functionality. The client accepts
        WSDL address and uses WSDLParser to get all defined types and
        operations. The types are set to client.types and operations
        are set to self.service.

        To examine present types or operations simply print (or touch repr):
            client.types or client.service, correspondingly.

        To create type simply call:
            client.types.MyTypeName().
        Class constructor will also create all obligatory (non-nillable) children.
        To call an operation:
            client.service.MyOperationName(arg1, arg2, arg3, ...),
        where arguments are of required types. Arguments can also
        be passed as keywords or a ready wrapped message.

        If any help is available in the WSDL document it is propagated to the
        types and operations, see e.g. help client.types.MyTypeName. In addition
        the help page on an operation displays its call signature.

        Nice printing is also available for all types defined in client.types:
            print(client.types.MyTypeName())

        .. warning::
            Only document/literal wrapped convention is implemented at the moment.

        Details
        -------
        In reality client.types and client.service are simply containers.
        The content of these containers is set from results of parsing
        the wsdl document by WSDLParser.get_types and WSDLParser.get_methods
        correspondingly.

        The client.types container consists of auto generated (by WSDLParser)
        class definitions. So that a call to a member returns and instance
        of the new type. New types are auto-generated according to a special
        convention by metaclass xmltypes.ComplexTypeMeta.

        The client.service container consists of methods wrapers
        methods.Method. The method wrapper is callable with free number of
        parameters. The input and output requirements of a method are
        contained in methods.Message instances Method.input and
        Method.output correspondingly. On a call a method converts
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
        #before getting types we handle anyType
        #anyType is somewhat tricky, because it must
        #know all the other types to work, therefore
        #we recreate it here. In such a way all other
        #service do not conflict with this instance
        primmap = wsdl._primmap.copy()
        primmap['anyType'] = type('XMLAny', (xmltypes.XMLAny,), {})
        #get all types - a dictionary
        types = parser.get_types(primmap)
        primmap['anyType']._types = types.copy()
        #get all methods - a dictionary
        methods = parser.get_methods(types)
        #create dispatchers for types and methods
        #first provide nice printing
        types["_container"] = types.keys()
        methods["_container"] = methods.keys()
        types["__str__"] = str_for_containers
        types["__repr__"] = str_for_containers
        methods["__str__"] = str_for_containers
        methods["__repr__"] = str_for_containers
        self.types = type('TypesDispatcher', (), types)()
        self.service = type('ServiceDispatcher', (), methods)()
        #get service names for printing
        self.names = parser.get_service_names()

    def __str__(self):
        res = ''
        for name in self.names:
            res = res + ', %s' %name
        res = res[2:] + " at:\n\t%s" %(self.wsdl_url)
        return res

    def __repr__(self):
        return self.__str__()


