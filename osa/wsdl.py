# wsdl.py - WSDLParser class, part of osa.
# Copyright 2013 Sergey Bozhenkov, boz at ipp.mpg.de
# Licensed under LGPLv3 or later, see the COPYING file.

"""
    Conversion of WSDL documents into Python.
"""
from . import xmlnamespace
from . import xmlparser
from . import xmlschema
from . import xmltypes
from . import message
from . import method
import xml.etree.cElementTree as etree


class WSDLParser(object):
    """
        Parser to get types and methods defined in the document.
    """
    def __init__(self, wsdl_url):
        """
            Initialize parser.

            The WSDL document is loaded and is converted into xml.

            Initialized members:
            self.wsdl_url  - url of wsdl document, or file
            self.wsdl - xml document read from wsdl_url (etree.Element)
            self.tns - target namespace

            Parameters
            ----------
            wsdl_url : str
                Address of the WSDL document.
        """
        self.wsdl_url = wsdl_url
        self.wsdl = xmlparser.parse_qualified_from_url(wsdl_url)
        if self.wsdl.tag != "{%s}definitions" % xmlnamespace.NS_WSDL:
            raise ValueError("Not a WSDL xml, the top level element: %s" %
                             self.wsdl.tag)
        # get target namespace
        self.tns = self.wsdl.get('targetNamespace', "")

    def get_types(self, ):
        """
            Constructs a map of all types defined in the document.

            Returns
            -------
            out : dict
                A map of found types {type_name : complex class}
        """
        types_section = self.wsdl.findall('.//{%s}types' %
                                          xmlnamespace.NS_WSDL)[0]
        schemas = types_section.findall('./{%s}schema' % xmlnamespace.NS_XSD)
        xtypes = {}
        for schema in schemas:
            parser = xmlschema.XMLSchemaParser(schema, wsdl_url=self.wsdl_url)
            xtypes.update(parser.get_list_of_defined_types())
        types = xmlschema.XMLSchemaParser.convert_xmltypes_to_python(xtypes)
        xmltypes.XMLAny._types.update(types)
        return types

    def get_messages(self, types):
        """
            Construct messages from message section.

            Parameters
            ----------
            types : dictionary of types
                Types as returned by get_types().

           Returns
           -------
           out : dict
            Map message name -> Message instance
        """
        xmessages = self.wsdl.findall('./{%s}message' % xmlnamespace.NS_WSDL)
        messages = {}
        for x in xmessages:
            message_name = "{%s}%s" % (self.tns, x.get("name", ""))
            parts = []
            xparts = x.findall('./{%s}part' % xmlnamespace.NS_WSDL)
            for y in xparts:
                part_name = y.get("name", "")
                part_type = y.get("element", None)
                if part_type is None:
                    part_type = y.get("type", None)
                if part_type is None:
                    raise ValueError("Could not find part type in:\n %s"
                                     % (etree.tostring(x).decode()))
                cls = None
                if part_type in types:
                    cls = types[part_type]
                elif part_type in xmltypes.primmap:
                    cls = xmltypes.primmap[part_type]
                else:
                    raise ValueError("Type %s not found for message:\n%s" %
                                     (part_type, etree.tostring(x).decode()))
                parts.append([part_name, cls])
            messages[message_name] = message.Message(message_name,
                                                     parts)
        return messages

    def get_operations(self, messages):
        """
            Get list of operations with messages
            from portType section.

            Parameters
            ----------
            messages : dict
                Dictionary of message from `get_messages`.

           Returns
           -------
           out : dict
            {portType -> {operation name -> Method instance}}
            The method here does not have location.
        """
        xports = self.wsdl.findall('./{%s}portType' % xmlnamespace.NS_WSDL)
        ports = {}
        for xport in xports:
            port_name = "{%s}%s" % (self.tns, xport.get("name", ""))
            ports[port_name] = {}
            xops = xport.findall('./{%s}operation' % xmlnamespace.NS_WSDL)
            for xop in xops:
                op_name = xop.get("name", "")
                ports[port_name][op_name] = {}
                xin = xop.findall('./{%s}input' % xmlnamespace.NS_WSDL)
                if not(xin):
                    raise ValueError("No input message in operation: \n%s" %
                                     (etree.tostring(xop).decode()))
                in_name = xin[0].get("message", "")
                if not in_name in messages:
                    raise ValueError("Message %s not found." % in_name)
                in_cl = messages[in_name]
                out_cl = None
                xout = xop.findall('./{%s}output' % xmlnamespace.NS_WSDL)
                if xout:
                    out_name = xout[0].get("message", "")
                    if not out_name in messages:
                        raise ValueError("Message %s not found." % in_name)
                    out_cl = messages[out_name]

                # documentation
                doc = xop.find('{%s}documentation' % xmlnamespace.NS_WSDL)
                if doc is not None:
                    doc = doc.text

                op = method.Method(op_name, in_cl, out_cl, doc=doc)
                ports[port_name][op_name] = op
        return ports

    def get_bindings(self, operations):
        """
            Check binding document/literal and http transport.

            If any of the conditions is not satisfied
            the binding is dropped, i.e. not present in
            the return value. This also sets soapAction
            and use_parts of the messages.

            Parameters
            ----------
            operations : dict as returned by get_operations

            Returns
            -------
            out : dict
             Map similar to that from get_operations but
             with binding names instead of portType names.
        """
        xbindings = self.wsdl.findall("./{%s}binding" % xmlnamespace.NS_WSDL)
        bindings = {}
        for xb in xbindings:
            b_name = "{%s}%s" % (self.tns, xb.get("name", ""))
            b_type = xb.get("type", None)
            if b_type is None:
                raise ValueError("No type in binding %s" %
                                 (etree.tostring(xb).decode()))
            if not b_type in operations:
                raise ValueError("Binding type %s no in operations" % b_type)
            xb_soap = xb.findall("./{%s}binding" % xmlnamespace.NS_SOAP)
            if not(xb_soap):
                continue  # not a soap binding in wsdl
            if xb_soap[0].get("style", "") == "rpc":
                continue
            if xb_soap[0].get("transport", "") !=\
                    "http://schemas.xmlsoap.org/soap/http":
                continue
            ops = operations[b_type]
            bindings[b_name] = {}
            xops = xb.findall("./{%s}operation" % xmlnamespace.NS_WSDL)
            for xop in xops:
                op_name = xop.get("name", "")
                if not op_name in ops:
                    raise ValueError("operation %s no in operations" %
                                     op_name)
                soap_op = xop.find("./{%s}operation" % xmlnamespace.NS_SOAP)
                s_action = None
                if soap_op is not None:
                    s_action = soap_op.get("soapAction", "")

                all_literal = True
                xop_in = xop.find("./{%s}input" % xmlnamespace.NS_WSDL)
                if xop_in is not None:
                    xop_in_body = xop_in.find("./{%s}body" % xmlnamespace.NS_SOAP)
                    if xop_in_body is None:
                        raise ValueError("No body found for %s" %
                                         (etree.tostring(xop).decode()))
                    if xop_in_body.get("use") != "literal":
                        all_literal = False
                    parts = xop_in_body.get("parts")
                    if parts is None:
                        ops[op_name].input.use_parts = ops[op_name].input.parts
                    else:
                        parts = parts.split(" ")
                        ops[op_name].input.use_parts = []
                        for p in parts:
                            for pp in ops[op_name].input.parts:
                                if pp[0] == p:
                                    ops[op_name].input.use_parts.append(pp)
                                    break

                xop_out = xop.find("./{%s}output" % xmlnamespace.NS_WSDL)
                if xop_out is not None:
                    xop_out_body = xop_out.find("./{%s}body" % xmlnamespace.NS_SOAP)
                    if xop_out_body is None:
                        raise ValueError("No body found for %s" %
                                         (etree.tostring(xop).decode()))
                    if xop_out_body.get("use") != "literal":
                        all_literal = False
                    parts = xop_out_body.get("parts")
                    if parts is None:
                        ops[op_name].output.use_parts = ops[op_name].output.parts
                    else:
                        parts = parts.split(" ")
                        ops[op_name].output.use_parts = []
                        for p in parts:
                            for pp in ops[op_name].output.parts:
                                if pp[0] == p:
                                    ops[op_name].output.use_parts.append(pp)
                                    break
                # rebuild __doc__ after messing with messages
                ops[op_name]._redoc()

                if all_literal:
                    ops[op_name].action = s_action
                    bindings[b_name][op_name] = ops[op_name]
        return bindings

    def get_services(self, bindings):
        """
            Find all services an make final list of
            operations.

            This also sets location to all operations.

            Parameters
            ----------
            bindings : dic from get_bindings.

            Returns
            -------
            out : dict
                Dictionary {service -> {operation name -> method}.
        """

        xservices = self.wsdl.findall('./{%s}service' % xmlnamespace.NS_WSDL)
        services = {}
        for xs in xservices:
            s_name = xs.get("name", "")
            xports = xs.findall('./{%s}port' % xmlnamespace.NS_WSDL)
            for xp in xports:
                b = xp.get("binding", "")
                xaddr = xp.findall('./{%s}address' % xmlnamespace.NS_SOAP)
                if not(xaddr):
                    continue  # no soap 11
                loc = xaddr[0].get("location", "")
                if b in bindings:
                    for k, v in bindings[b].items():
                        v.location = loc
                    services[s_name] = bindings[b]
        return services

    def parse(self):
        """
            Do parsing, return types, services.

            Returns
            -------
            out : (types, services)
        """
        t = self.get_types()
        m = self.get_messages(t)
        op = self.get_operations(m)
        b = self.get_bindings(op)
        s = self.get_services(b)
        return t, s
