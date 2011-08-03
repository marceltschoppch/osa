"""
    Some common soap constants.
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
