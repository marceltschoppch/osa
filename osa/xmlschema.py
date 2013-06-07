"""
    Conversion of XML Schema types into Python classes.
"""
import xmlnamespace
import xmltypes
import xmlparser
import xml.etree.cElementTree as etree

class XMLSchemaParser(object):
    """
        Parser to get types from an XML Schema.
    """
    def __init__(self, root):
        """
            Initialize parser.

            self.schema - the root node of the schema
            self.tns - target namespace
            self.imported - a list of parsers for imported schemas

            Parameters
            ----------
            wsdl_url : xml schema, i.e. <schema ...> ... </schema>
                The schema to parse
        """
        #check we have a schema
        if root.tag != "{%s}schema" %xmlnamespace.NS_XSD:
            raise ValueError("Supplied root node '%s'"\
                             " is not of XML Schema type." %root.tag)

        #set schema parameters
        self.schema = root
        self.tns = self.schema.get("targetNamespace", "")

        #find and initialize imported ones
        self.imported = [] 
        imports = self.schema.findall('.//{%s}import' %xmlnamespace.NS_XSD)
        for schema in imports:
            loc = schema.get("schemaLocation", None)
            #basically says that types from that namespace will be used, no real
            #import, i.e. the real schema was defined already
            if loc is None:
                continue
            #standard namespace we know by default
            if loc in (xmlnamespace.NS_SOAP, xmlnamespace.NS_SOAP12,
                       xmlnamespace.NS_SOAP_ENC, xmlnamespace.NS_SOAP_ENV,
                       xmlnamespace.NS_WSDL, xmlnamespace.NS_XSD,
                       xmlnamespace.NS_XSI):
                continue
            #try getting the schema
            parser = XMLSchemaParser(xmlparser.parse_qualified_from_url(loc))
            #check if want to change the schema namespace
            ns = schema.get("namespace", None)
            if ns is not None:
                parser.tns = ns
            self.imported.append(parser)

    def generate_classes(self):
        """
            Generate Python classes from this schema.

            Returns
            -------
            out : dictionary
                Dictionary of types {ns}name -> Python class
        """
        xlist = self.get_list_of_defined_types()
        types = XMLSchemaParser.convert_xmltypes_to_python(xlist)
        return types

    def get_list_of_defined_types(self):
        """
            Construct a dictionary: type name -> xml node

            Types are given by complexType, simpleType or element.
            Types from imported schemas are included as well.
            Type names include namespaces.

            Returns
            -------
            out : dict
                A dictionary of defined types.
        """
        #get list of types
        raw = self.schema.findall('./{%s}complexType' %xmlnamespace.NS_XSD)
        raw.extend(self.schema.findall('./{%s}simpleType' %xmlnamespace.NS_XSD))
        #<element> entries are usually used in message section in
        #wsdl. Such an entry can either define its type inside,
        #or simply be an alias to defined type. However. we
        #can not simply attach all elements to types, because
        #element names can shadow the types. Therefore, do it
        #one by one.
        elements = self.schema.findall('./{%s}element' %xmlnamespace.NS_XSD)

        #create dictionary by getting also names of the types
        types = {}
        for el in raw:
            name = el.get("name", None)
            if name is not None: #consider an exception
                name = "{%s}%s" %(self.tns, name)
                types[name] = el

        for el in elements:
            name = el.get("name", None)
            if name is not None:
                name = "{%s}%s" %(self.tns, name)
                if not(types.has_key(name)):
                    types[name] = el

        #go over all children and append their types
        for parser in self.imported:
            types.update(parser.get_list_of_defined_types())

        return types

    @staticmethod
    def convert_xmltypes_to_python(xtypes):
        """
            Convert xml types definitions in the dictionary
            into Python classes.
            
            Parameters
            ----------
            xtypes : dictionary name -> xml element
                A dictionary as returned by get_list_of_defined_types.

            Returns
            -------
            out : dictionary name -> Python class
        """
        types = {} 
        for k in xtypes.keys():
            #if the class was already created as a parent of another class, do nothing
            if types.has_key(k):
                continue
            x = xtypes[k]
            XMLSchemaParser.create_type(k, x, xtypes, types)
        return types

    @staticmethod
    def create_type(name, element, xtypes, types):
        """
            Creates proper type for the element.

            The created types is appended to the types.

            Parameters
            ----------
            name : str
                Class name
            element : xml element
                Class node.
            xtypes : dictionary class name -> xml node
            types : dictionary class name -> Python class
                The result is appended here.
        """
        #I need this a a separate function to be able to call
        #it recursively for parents and children
        #a switch to decide what to do
        #element.complexType = complexType
        #element.simpleType = simpleType
        #element empty with type = xx = an alias to xx
        #element empty - empty class
        #complexType.sequence/all/choice - complex class, no parent
        #complexContent.extension - complex class with parent
        #simpleType.restriction - e.g. string enumeration
        if element.tag ==  "{%s}element" %xmlnamespace.NS_XSD:
            if len(element)>0:
                element = element[0]
            else:
                type = element.get("type", None)
                if type is not None:
                    #alias
                    XMLSchemaParser.create_alias(name, type, xtypes, types)
                    return
                else:
                    #empty class
                    XMLSchemaParser.create_empty_class(name, types)
                    return
        if element.tag == "{%s}complexType" %xmlnamespace.NS_XSD:
            #complex class
            XMLSchemaParser.create_complex_class(name, element, xtypes, types)
        elif element.tag == "{%s}simpleType" %xmlnamespace.NS_XSD and\
                element[0].tag == "{%s}restriction" %xmlnamespace.NS_XSD \
                and element[0].get("base", None) == "{%s}string" %xmlnamespace.NS_XSD \
                and element[0][0].tag == "{%s}enumeration" %xmlnamespace.NS_XSD:
            XMLSchemaParser.create_string_enumeration(name, element, types)

    @staticmethod
    def get_doc(x):
        """
            Extract documentation from element.

            Parameters
            -----------
            x : xml element

            Returns
            -------
            out : str
                Documentation from whatever found <documentation> out </documentation>
        """
        doc = x.find('.//{%s}documentation' %xmlnamespace.NS_XSD)
        if doc is None:
            doc = x.find('.//documentation')
        if doc is not None:
            return doc.text
        else:
            return "no documentation"

    @staticmethod
    def create_alias(name, alias_type, xtypes, types):
        """
            Create a copy of known class with proper namespace.

            Parameters
            ----------
            name : str
                Name of the new class.
            alias_type : str
                The target alias
            xtypes : dictionary class name -> xml node
            types : dictionary of classes
                The new aliases is appended here.
        """
        alias = None
        if alias_type is None:
            return
        elif xmltypes.primmap.has_key(alias_type):
            alias = xmltypes.primmap[alias_type]
        elif types.has_key(alias_type):
            alias = types[alias_type]
        elif not(xtypes.has_key(alias_type)):
            raise ValueError(" Alias class %s not found in schema" %(alias_type))
        else:
            XMLSchemaParser.create_type(alias_type,
                            xtypes[alias_type], xtypes, types)
            alias = types[alias_type]
        cls_name = xmlnamespace.get_local_name(name)
        cls_ns = xmlnamespace.get_ns(name)
        cls = type(cls_name, (alias,), {"__doc__":"no documentation",
                                  "_namespace":cls_ns})
        types[name] = cls

    @staticmethod
    def create_empty_class(name, types):
        """
            Create empty class, i.e. no children.

            Parameters
            ----------
            name : str
                Name of the new class.
            alias_type : str
                The target alias
            xtypes : dictionary class name -> xml node
            types : dictionary of classes
                The new aliases is appended here.
        """
        cls_name = xmlnamespace.get_local_name(name)
        cls_ns = xmlnamespace.get_ns(name)
        cls = xmltypes.ComplexTypeMeta(cls_name, [],
                                  {"_children":[], "__doc__":"no documentation",
                                   "_namespace":cls_ns})
        types[name] = cls
    

    @staticmethod
    def create_string_enumeration(name, element, types):
        """
            Creates a copy of XMLStringEnumertion with properly set
            allowed values.

            The created class is attached to types.

            Parameters
            ----------
            name : str
                Name of the new class.
            element : `etree.Element`
                XML description of the enumeration
            types : dictionary of classes
        """
        xvalues = element.findall('.//{%s}enumeration' %xmlnamespace.NS_XSD)
        values = []
        for x in xvalues:
            values.append(x.get("value", None))
        doc = XMLSchemaParser.get_doc(element)
        #create new class
        #I choose to give short names to classes, i.e. without
        # a namespace, even though Python can manage full names as well
        cls_name = xmlnamespace.get_local_name(name)
        cls_ns = xmlnamespace.get_ns(name)
        cls = type(cls_name, (xmltypes.XMLStringEnumeration,),
                                {"_allowedValues":values, "__doc__":doc,
                                  "_namespace":cls_ns})
        types[name] = cls
        
    @staticmethod
    def create_complex_class(name, element, xtypes, types):
        """
            Create complex class.

            Parameters
            ----------
            name : str
                Class name
            element : xml element
                Class node.
            xtypes : dictionary class name -> xml node
            types : dictionary class name -> Python class
                The result is appended here.
        """
        #decide if we have a parent and first create that
        parents = []
        exts = element.findall("./{%s}complexContent/{%s}extension" %(xmlnamespace.NS_XSD, xmlnamespace.NS_XSD))
        if exts is not None:
            for ext in exts:
                parent_name = ext.get("base", None) 
                if parent_name is None:
                    continue
                elif types.has_key(parent_name):
                    parent = types[parent_name]
                elif not(xtypes.has_key(parent_name)):
                    raise ValueError(" Parent class not found in schema for:\n %s" %(etree.tostring(element)))
                else:
                    XMLSchemaParser.create_type(parent_name,
                                    xtypes[parent_name], xtypes, types)
                    parent = types[parent_name]
                parents.append(parent)

        #find sequence/choice/all
        seq = None
        for str in ("sequence", "all", "choice"):
            seq = element.find("./{%s}%s" %(xmlnamespace.NS_XSD, str))
            if seq is not None:
                break

        #collect children
        children = []
        if seq is not None:
            for s in seq:
                #iterate over sequence, do not consider in place defs
                type_name = s.get('type', None)
                if type_name is None:
                    continue
                elif xmltypes.primmap.has_key(type_name):
                    type = xmltypes.primmap[type_name]
                elif types.has_key(type_name):
                    type = types[type_name]
                elif not(xtypes.has_key(type_name)):
                    raise ValueError("Type not found in schema for:\n %s" %(etree.tostring(element)))
                else:
                    XMLSchemaParser.create_type(type_name,
                                    xtypes[type_name], xtypes, types)
                    type = types[type_name]
                child_name = s.get('name', 'unknown')
                minOccurs = int(s.get('minOccurs', 1))
                maxOccurs = s.get('maxOccurs', 1)
                if maxOccurs != 'unbounded':
                    maxOccurs = int(maxOccurs)
                children.append({ "name":child_name,
                                 'type' : type,
                                 'min' : minOccurs,
                                 'max' : maxOccurs})

        #get doc
        doc = XMLSchemaParser.get_doc(element)

        #create new class
        #I choose to give short names to classes, i.e. without
        # a namespace, even though Python can manage full names as well
        cls_name = xmlnamespace.get_local_name(name)
        cls_ns = xmlnamespace.get_ns(name)
        cls = xmltypes.ComplexTypeMeta(cls_name, parents,
                                  {"_children":children, "__doc__":doc,
                                   "_namespace":cls_ns})
        types[name] = cls
