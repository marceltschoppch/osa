"""
    Conversion of WSDL documents into Python.
"""
from xmltypes import *
from methods import *
from soap import *
import urllib2
import xml.etree.cElementTree as etree

#primitive types mapping xml -> python
_primmap = { 'anyType'          : XMLAny,
             'boolean'          : XMLBoolean,
             'decimal'          : XMLDecimal,
             'int'              : XMLInteger,
             'integer'          : XMLInteger,
             'positiveInteger'  : XMLInteger,
             'unsignedInt'      : XMLInteger,
             'short'            : XMLInteger,
             'byte'             : XMLInteger,
             'long'             : XMLInteger,
             'float'            : XMLDouble,
             'double'           : XMLDouble,
             'string'           : XMLString,
             'base64Binary'     : XMLString,
             'anyURI'           : XMLString,
             'language'         : XMLString,
             'token'            : XMLString,
             'date'             : XMLDate,
             'dateTime'         : XMLDateTime,
             # FIXME: probably timedelta, but needs parsing.
             # It looks like P29DT23H54M58S
             'duration'         : XMLString}

class WSDLParser(object):
    """
        Parser to get types and methods defined in the document.
    """
    def __init__(self, wsdl_url):
        """
            Initialize parser.

            The WSDL document is loaded and is converted into xml.

            Initialized members:
            self.wsdl_url  - url of wsdl document
            self.wsdl - xml document read from wsdl_url (etree.Element)
            self.tns - target namespace

            Parameters
            ----------
            wsdl_url : str
                Address of the WSDL document.
        """
        #open wsdl page - get a file like object and
        # parse it into xml
        page_handler = urllib2.urlopen(wsdl_url)
        self.wsdl = etree.parse(page_handler).getroot()
        page_handler.close()
        del page_handler
        self.wsdl_url = wsdl_url
        #get target namespace
        self.tns = self.wsdl.get('targetNamespace', None)

    def get_service_names(self):
        """
            Returns names of services found in WSDL.

            This is from wsdl:service section.

            Returns
            -------
            out : list of str
                Names.
        """
        services = self.wsdl.findall('.//{%s}service' % NS_WSDL)
        res = []
        for service in services:
            name = service.get("name", None)
            if name is not None:
                res.append(name)
        return res

    def get_type_name(self, element):
        """
            Get type name from XML element.

            Parameters
            ----------
            element : etree.Element
                XML description of the type.
        """
        name = element.get('name', None)
        if name is None:
            #try to find parent. ElementTree does not keep track
            #of parent, so we search for element and see if current
            #element is in children, a bit weird :).
            elements = self.wsdl.findall('.//{%s}element' % NS_XSD)
            parent = None
            for e in elements:
                if element in e:
                    parent = e
                    break
            if parent is None:
                return None
            name = parent.get('name', None)
        return name

    def create_named_class(self, name, types, allelements):
        """
            Creates a single named type.

            Function searches through all available elements to find one
            suitable. This is useful if a type is present as a child before
            it is present in the list.

            Parameters
            ----------
            name : str
                Name of the type.
            types : dict
                Map of known types.
            allelements : list of etree.Element instance
                List of all types found in WSDL. It is used to create
                related classes in place.
        """
        for element in allelements:
            el_name = self.get_type_name(element)
            if el_name == name:
                self.create_class(element, el_name, types, allelements)
                break

    def collect_children(self, element, children, types, allelements):
        """
            Collect information about children (xml sequence, etc.)

            Parameters
            ----------
            element : etree.Element
                XML sequence container.
            children : list
                Information is appended to this list.
            types : dict
                Known types map.
            allelements : list of etree.Element instance
                List of all types found in WSDL. It is used to create
                related classes in place.
        """
        for subel in element:
            #iterate over sequence, do not consider in place defs
            type = get_local_name(subel.get('type', None))
            if type is None:
                raise ValueError(
                        "Do not support this type of complex type: %s"
                                                         %subsub.tag)
            ch = types.get(type, None)
            if ch is None:
                self.create_named_class(type, types, allelements)
            ch = types.get(type, None)
            if ch is None:
                raise ValueError("Child %s class is not found " %type)
            child_name = subel.get('name', 'unknown')
            minOccurs = int(subel.get('minOccurs', 1))
            maxOccurs = subel.get('maxOccurs', 1)
            if maxOccurs != 'unbounded':
                maxOccurs = int(maxOccurs)
            children.append({ "name":child_name,
                             'type' : ch,
                             'min' : minOccurs,
                             'max' : maxOccurs})

    def create_class(self, element, name, types, allelements):
        """
            Create new type from xml description.

            Parameters
            ----------
            element : etree.Element instance
                XML description of a complex type.
            name : str
                Name of the new class.
            types : dict
                Map of already known types.
            allelements : list of etree.Element instance
                List of all types found in WSDL. It is used to create
                related classes in place.
        """
        doc = None
        children = []
        base = []
        #iterate over children
        #handle only children, bases non-primitive classes and docs
        for subel in element:
            if subel.tag in ("{%s}sequence" %NS_XSD,
                             "{%s}all" %NS_XSD,
                             "{%s}choice" %NS_XSD):
                #add children - arguments of new class
                self.collect_children(subel, children, types, allelements)

            elif subel.tag == "{%s}complexContent" %NS_XSD:
                #base class
                subel = subel[0]
                if subel.tag == "{%s}extension" %NS_XSD:
                    base_name = get_local_name(subel.get("base", None))
                    b = types.get(base_name, None)
                    if b is None:
                        self.create_named_class(base_name, types, allelements)
                    b = types.get(base_name, None)
                    if b is None:
                        raise ValueError("Base %s class is not found" %base_name)
                    base.append(b)
                for subsub in subel:
                    if subsub.tag in ("{%s}sequence" %NS_XSD,
                                      "{%s}all" %NS_XSD,
                                      "{%s}choice" %NS_XSD):
                        self.collect_children(subsub, children, types, allelements)
            elif subel.tag == "{%s}annotation" %NS_XSD:
                if len(subel) and\
                   subel[0].tag == "{%s}documentation" %NS_XSD:
                    doc = subel[0].text

        if name not in types:
            #create new class
            cls = ComplexTypeMeta(name, base,
                                      {"_children":children, "__doc__":doc})
            types[name] = cls


    def get_types(self, initialmap):
        """
            Constructs a map of all types defined in the document.

            At the moment simple types are not processed at all!
            Only complex types are considered. If attribute
            or what so ever are encountered an exception if fired.

            Parameters
            ----------
            initialmap : dict
                Initial map of types. Usually it will be _primmap.
                This is present here so that different services
                can create own types of XMLAny.

            Returns
            -------
            out : dict
                A map of found types {type_name : complex class}
        """
        #find all types defined here
        types = self.wsdl.findall('.//{%s}complexType' %NS_XSD)
        types.extend(self.wsdl.findall('.//{%s}simpleType' %NS_XSD))

        res = initialmap.copy() #types container
        #iterate over the found types and fill in the container
        # If an element used types placed later in the document, it will
        #created in place when calling create_class.
        for t in types:

            #get name of the type
            name = self.get_type_name(t)
            if name is None:
                continue

            #if type is primitive or was already processed, skip it
            if (res.get(name, None) is not None):
                continue

            #if unknown simple type - raise error
            if t.tag == "{%s}simpleType" %NS_XSD:
                raise ValueError("Uknown simple type %s" %name)

            #handle complex type, this also registers new class to result
            self.create_class(t, name, res, types)

        return res

    def get_methods(self, types):
        """
            Construct a map of all operations defined in the document.

            Parameters
            ----------
            types : dict
                Map of known types as returned by get_types.

            Returns
            -------
            out : dict
                A map of operations: {operation name : method object}
        """
        res = {} # future result

        #find all service definitions
        services = self.wsdl.findall('.//{%s}service' %NS_WSDL)
        bindings = self.wsdl.findall(".//{%s}binding" %NS_WSDL)
        port_types = self.wsdl.findall(".//{%s}portType" %NS_WSDL)
        messages = self.wsdl.findall('.//{%s}message' %NS_WSDL)
        for service in services:
            #all ports defined in this service. Port contains
            #operations
            ports = service.findall('.//{%s}port' %NS_WSDL)
            for port in ports:
                subel = port[0]

                #check that this is a soap port, since wsdl can
                #also define other ports
                if get_ns(subel.tag) not in (NS_SOAP, NS_SOAP12):
                    continue

                #port location
                location = subel.get('location')

                #find binding for this port
                binding_name = get_local_name(port.get('binding'))
                for binding in bindings:
                    if binding.get("name") == binding_name:
                        break

                #find binding style
                soap_binding = binding.find('{%s}binding' % NS_SOAP)
                if soap_binding is None:
                    soap_binding = binding.find('{%s}binding' % NS_SOAP12)
                if soap_binding is None:
                    soap_binding = binding.find('binding')
                if soap_binding is None:
                    raise SyntaxError("No SOAP binding found in %s" %
                                                    etree.tostring(binding))
                style =  soap_binding.get('style')

                #get port type - operation + message links
                port_type_name = get_local_name(binding.get('type'))
                for port_type in port_types:
                    if port_type.get("name") == port_type_name:
                        break
                port_operations = port_type.findall("{%s}operation" %NS_WSDL)

                #get operations
                operations = binding.findall('{%s}operation' % NS_WSDL)
                for operation in operations:
                    #get operation name
                    name = get_local_name(operation.get("name"))

                    #check we have soap operation
                    soap_op = operation.find('{%s}operation' % NS_SOAP)
                    if soap_op is None:
                        soap_op = operation.find('{%s}operation' % NS_SOAP12)
                    if soap_op is None:
                        soap_op = operation.find('operation')
                    if soap_op is None:
                        raise SyntaxError("No SOAP operation found in %s" %
                                                  etree.tostring(operation))

                    #operation action(?), style
                    action = soap_op.attrib['soapAction']
                    operation_style = soap_op.get('style', style)

                    # FIXME is it reasonable to assume that input and output
                    # are the same? Is it ok to ignore the encoding style?
                    input = operation.find('{%s}input' % NS_WSDL)[0]
                    literal = input.get('use') == 'literal'

                    #do not support in/out headers, otherwise must be found here

                    #go to port part and find messages.
                    for port_operation in port_operations:
                        if port_operation.get("name") == name:
                            break
                    in_msg_name = get_local_name(
                            port_operation.find('{%s}input' %NS_WSDL).get("message"))
                    out_msg_name = get_local_name(
                            port_operation.find('{%s}output' %NS_WSDL).get("message"))
                    #documentation
                    doc = port_operation.find('{%s}documentation' %NS_WSDL)
                    if doc is not None:
                        doc = doc.text

                    #finally go to message section
                    for in_msg_xml in messages:
                        if in_msg_xml.get("name") == in_msg_name:
                            break
                    for out_msg_xml in messages:
                        if out_msg_xml.get("name") == out_msg_name:
                            break
                    in_types = in_msg_xml.findall('{%s}part' %NS_WSDL)
                    out_types = out_msg_xml.findall('{%s}part' %NS_WSDL)
                    #create input and output messages
                    in_msg = self.create_msg(name, in_types, operation_style,
                                                                 literal, types)
                    out_msg = self.create_msg(name, out_types, operation_style,
                                                                 literal, types)
                    method = Method(location, name, action, in_msg, out_msg, doc=doc)
                    res[name] = method
        return res

    def create_msg(self, name, part_elements, style, literal, types):
        """
            Create input or output message.

            Parameters
            ----------
            name : str
                Name of this message.
            part_elements : list instance
                List of parts as found in message section.
            style : str
                Style of operation: 'document', 'rpc'.
            literal : bool
                True = literal, False = encoded.
            types : dict
                Map of known types as returned by get_types.

            Returns
            -------
            out : Message instance
                Message for handling calls in/out.
        """
        #get all parameters - parts of the message
        parts = []
        for t in part_elements:
            part_name = t.get("name", None)
            if part_name is None:
                continue
            type_name = t.get('element', None)
            if type_name is None:
                type_name = t.get('type', None)
            type_name = get_local_name(type_name)
            parts.append((part_name, types[type_name]))

        #create message
        return Message(name, self.tns, parts, style, literal)



