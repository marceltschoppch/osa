# method.py - Method class, part of osa.
# Copyright 2013 Sergey Bozhenkov, boz at ipp.mpg.de
# Licensed under LGPLv3 or later, see the COPYING file.

"""
    SOAP operation class.
"""
from . import xmlnamespace
from . import xmlparser
import sys
if sys.version_info[0] < 3:
    from urllib2 import urlopen, Request, HTTPError
else:
    from urllib.request import urlopen, Request, HTTPError
import xml.etree.cElementTree as etree

# some standard stuff
SOAP_BODY = '{%s}Body' % xmlnamespace.NS_SOAP_ENV
SOAP_FAULT = '{%s}Fault' % xmlnamespace.NS_SOAP_ENV
SOAP_HEADER = '{%s}Header' % xmlnamespace.NS_SOAP_ENV


class Method(object):
    """
        Definition of a single SOAP method, including location, action, name
        and input and output classes.

        Parameters
        ----------
        name : str
            Name of operation
        input : `osa.message.Message` instance
            Input message.
        output : `osa.message.Message` instance
            Output message.
        doc : str, optional - default to None
            Documentation of the method as found in portType section of WSDL.
        action : str
            Soap action string.
        location : str
            Location as found in service part of WSDL.
    """
    def __init__(self, name, input, output, doc=None,
                 action=None, location=None):
        self.name = name
        self.input = input
        self.output = output
        self.location = location
        self.action = action
        self._doc = doc
        self._redoc()

    def _redoc(self):
        """
            Add call signatures to doc.
        """
        sign = '%s\n%s\n%s' % (self.__str__(),
                               self.__str__(switch="positional"),
                               self.__str__(switch="keyword"))
        self.__doc__ = '%s\n%s' % (sign, self._doc)

    def __str__(self, switch='wrap'):
        """
            String representation of the call in three forms:
                - wrapped message
                - positional sub-arguments
                - keyword sub-arguments.

            Parameters
            ----------
            switch : str, optional
                Specifies which form to return: wrap, positional, keyword.
        """
        input_msg = self.input.__str__(switch=switch)
        if self.output is None:
            output_msg = "None"
        else:
            output_msg = self.output.__str__(switch='out')

        return '%s = %s(%s)' % (output_msg, self.name, input_msg)

    def __call__(self, *arg, **kw):
        """
            Process rpc-call.
        """
        # create soap-wrap around our message
        env = etree.Element('{%s}Envelope' % xmlnamespace.NS_SOAP_ENV)
        # header = etree.SubElement(env, '{%s}Header' % xmlnamespace.NS_SOAP_ENV)
        body = etree.SubElement(env, '{%s}Body' % xmlnamespace.NS_SOAP_ENV)

        # compose call message - convert all parameters and encode the call
        kw["_body"] = body
        self.input.to_xml(*arg, **kw)

        text_msg = etree.tostring(env)  # message to send
        del env

        # http stuff
        request = Request(self.location, text_msg,
                          {'Content-Type': 'text/xml',
                           'SOAPAction': self.action})
        del text_msg

        # real rpc
        try:
            response = urlopen(request)
            del request
            # check http code returned
            if response.code == 200:
                if self.output is None:
                    return None
                # string to xml
                # use qualified parsing to get the anyType
                # type properly, unless it hits the performance heavily
                xml = xmlparser.parse_qualified(response)
                # response = response.read()
                # xml = etree.fromstring(response)
                del response
                # find soap body
                body = xml.find(SOAP_BODY)
                if body is None:
                    raise RuntimeError("No SOAP body found in response")
                body = body[0]
                return self.output.from_xml(body)
            elif response.code == 202 or response.code == 204 \
                    and self.output is None:
                return None
            else:
                raise RuntimeError("Bad HTTP status code: %d" % response.code)
        except HTTPError as e:
            if e.code == 500:
                # read http error body and make xml from it
                try:
                    xml = etree.fromstring(e.fp.read())
                except Exception:
                    print(e)
                    return None
                body = xml.find(SOAP_BODY)
                if body is None:
                    raise
                # process service fault
                fault = body.find(SOAP_FAULT)
                if fault is not None:
                    code = fault.find('faultcode')
                    if code is not None:
                        code = code.text or ''
                    string = fault.find('faultstring')
                    if string is not None:
                        string = string.text or ''
                    detail = fault.find('detail')
                    if detail is not None:
                        detail = detail.text or ''
                    raise RuntimeError("SOAP Fault %s: %s <%s> %s %s" %
                                       (self.location, self.name, code,
                                        string, detail))
                else:
                    raise
            else:
                raise
