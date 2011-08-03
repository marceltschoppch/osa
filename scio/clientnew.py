from alltypes import *
import wsdl

class Client(object):
    """
        Top level class to talk to soap services.

        Parameters
        ----------
        wsdl_url : str
            Address of wsdl document to consume.
    """
    def __init__(self, wsdl_url):
        parser = wsdl.WSDLParser(wsdl_url)
        types = parser.get_types()
        methods = parser.get_methods(types)
        self.types = type('TypesDispatcher', (), types)()
        self.service = type('ServiceDispatcher', (), methods)()


