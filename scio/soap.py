"""
    Some common soap stuff.
"""

# soap contstants
NS_SOAP_ENV = "http://schemas.xmlsoap.org/soap/envelope/"
NS_SOAP_ENC = "http://schemas.xmlsoap.org/soap/encoding/"
NS_SOAP = 'http://schemas.xmlsoap.org/wsdl/soap/'
NS_SOAP12 = 'http://schemas.xmlsoap.org/wsdl/soap12/'
NS_XSI = "http://www.w3.org/1999/XMLSchema-instance"
NS_XSD = "http://www.w3.org/1999/XMLSchema"
NS_WSDL = 'http://schemas.xmlsoap.org/wsdl/'
SOAP_BODY = '{%s}Body' % NS_SOAP_ENV
SOAP_FAULT = '{%s}Fault' % NS_SOAP_ENV
SOAP_HEADER = '{%s}Header' % NS_SOAP_ENV

#namespace mapping
SOAPNS = {
             'soap-env'         : NS_SOAP_ENV,
             'soap-enc'         : NS_SOAP_ENC,
             'soap'             : NS_SOAP,
             'soap12'           : NS_SOAP12,
             'wsdl'             : NS_WSDL,
             'xsi'              : NS_XSI,
             'xsd'              : NS_XSD }

def get_local_name(full_name):
    """
        Removes namespace part of the name.

        In lxml namespacec can appear in 2 forms:
            {full.namespace.com}name, and
            prefix:name.
        Both cases are handled correctly here.
    """
    full_name = full_name[full_name.find('}')+1:]
    full_name = full_name[full_name.find(':')+1:]
    return full_name

def get_local_type(xmltype):
    """
        Simplifies types names, e.g. XMLInteger is
        presented as int.

        This is used for nice printing only.
    """
    if xmltype == "XMLBoolean":
        return 'bool'
    elif xmltype == "XMLDecimal":
        return 'decimal'
    elif xmltype == "XMLInteger":
        return 'int'
    elif xmltype == "XMLDouble":
        return 'float'
    elif xmltype == "XMLString":
        return 'str'
    elif xmltype == "XMLDate":
        return 'date'
    elif xmltype == "XMLDateTime":
        return 'datetime'
    else:
        return xmltype
