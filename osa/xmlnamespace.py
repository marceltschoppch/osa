# xmlnamespace.py - data for namespaces, part of osa.
# Copyright 2013 Sergey Bozhenkov, boz at ipp.mpg.de
# Licensed under LGPLv3 or later, see the COPYING file.

"""
    A list of default namespaces and some simplistic help functions.
"""
# default namespaces
NS_SOAP_ENV = "http://schemas.xmlsoap.org/soap/envelope/"
NS_SOAP_ENC = "http://schemas.xmlsoap.org/soap/encoding/"
NS_SOAP = 'http://schemas.xmlsoap.org/wsdl/soap/'
NS_SOAP12 = 'http://schemas.xmlsoap.org/wsdl/soap12/'
NS_XSI = "http://www.w3.org/2001/XMLSchema-instance"
NS_XSD = "http://www.w3.org/2001/XMLSchema"
NS_WSDL = 'http://schemas.xmlsoap.org/wsdl/'


def get_local_name(full_name):
    """
        Removes namespace part of the name.

        Namespaces can appear in 2 forms:
            {full.namespace.com}name, and
            prefix:name.
        Both cases are handled correctly here.
    """
    full_name = full_name[full_name.find('}')+1:]
    full_name = full_name[full_name.find(':')+1:]
    return full_name


def get_ns(tag):
    """
        Extract namespace.

        This function is opposite to get_local_name, in that
        it returns the first part of the tag: the namespace.

        Parameters
        ----------
        tag : str
            Tag to process.
    """
    p_open = tag.find('{')
    p_close = tag.find('}')
    if p_open != -1 and p_close != -1:
        return tag[p_open+1:p_close]
    else:
        return ''
