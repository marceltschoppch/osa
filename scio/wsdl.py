from alltypes import *

class WSDLParser(object):
    """
        Parser to get types and methods defined in the document.
    """
    def __init__(self, wsdl_url):
        """
            Initialize parser.

            The WSDL document is loaded.

            Parameters
            ----------
            wsdl_url : str
                Address of the WSDL document.
        """
        #read wsdl
        #parse into xml
