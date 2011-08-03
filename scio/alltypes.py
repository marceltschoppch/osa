from exceptions import *
from soap import *
from lxml import etree
from decimal import Decimal
from datetime import date, datetime, time
from urllib2 import urlopen, Request, HTTPError

class XMLType(object):
    """
        Base xml schema type.

        It defines basic functions to_xml and from_xml.
    """
    _namespace = ""
    def check_constraints(self, n, min_occurs, max_occurs):
        """
            Performs constraints checking.

            Parameters
            ----------
            n : int
                Actual number of occurrences.
            min_occurs : int
                Minimal allowed number of occurrences.
            max_occurs : int or 'unbounded'
                Maximal allowed number of occurrences.

           Raises
           ------
            ValueError
                If constraints are not satisfied.
        """
        if n<min_occurs:
            raise ValueError("Number of values is less than min_occurs")
        if max_occurs != 'unbounded' and n > max_occurs:
            raise ValueError("Number of values is more than max_occurs")

    def to_xml(self, parent, name):
        """
            Function to convert to xml from python representation.

            This is basic function and it is suitable for complex types.
            Primitive types must overload it.

            Parameters
            ----------
            parent : lxml.etree.Element
                Parent xml element to append this child to.
            name : str
                Full qualified (with namespace) name of this element.
        """
        #this level element
        element = etree.SubElement(parent, name)

        #namespace for future naming
        ns = "{" + self._namespace + "}"
        #add all children to the current level
        #note that children include also base classes, as they are propagated by
        #the metaclass below
        for child in self._children:
            child_name = child["name"]
            #get the value of the argument
            val = getattr(self, child_name, None)

            #do constraints checking
            n = 0 #number of values for constraints checking
            if isinstance(val, (list, tuple)):
                n = len(val)
            elif val is not None:
                n = 1
                val = [val, ]
            self.check_constraints(n, child['min'], child['max'])
            if n == 0:
                continue #only nillables can get so far

            #conversion
            full_name = ns + child_name #name with namespace
            for single in val:
                if not(isinstance(single, child['type'])):
                    #useful for primitive types:  python int, e.g.,
                    #can be passed directly. If str is used instead
                    #an exception is fired up.
                    single = child['type'](single)
                single.to_xml(element, full_name)

    def from_xml(self, element):
        """
            Function to convert from xml to python representation.

            This is basic function and it is suitable for complex types.
            Primitive types must overload it.

            Parameters
            ----------
            element : lxml.etree.Element
                Element to recover from.
        """
        #element is nill
        if bool(element.get('nil')):
            return

        all_children_names = []
        for child in self._children:
            all_children_names.append(child["name"])

        for subel in element:
            name = get_local_name(subel.tag)
            #check we have such an attribute
            if name not in all_children_names:
                raise ValueErro('does not have a "%s" member' % name)

            ind = all_children_names.index(name)
            #used for conversion. for primitive types we receive back built-ins
            inst = self._children[ind]['type']()
            subvalue = inst.from_xml(subel)

            #check conversion
            if subvalue is None:
                if self._children[ind]['min'] != 0:
                    raise ValueError("Non-nillable %s element is nil." %name)
            else:
                #unbounded is larger than 1
                if self._children[ind]['max'] > 1:
                    current_value = getattr(self, name, None)
                    if current_value is None:
                        current_value = []
                        setattr(self, name, current_value)
                    current_value.append(subvalue)
                else:
                    setattr(self, name, subvalue)

        return self

class ComplexTypeMeta(type):
    """
        Metaclass to create complex types on the fly.
    """
    def __new__(cls, name, bases, attributes):
        """
            Method to create new types.

            _children attribute must be present in attributes. It describes
            the arguments to be present in the new type. The he
            _children argument must be a list of the form:
            [{'name':'arg1', 'min':1, 'max':1, 'type':ClassType}, ...]

            Parameters
            ----------
            cls : this class
            name : str
                Name of the new type.
            bases : tuple
                List of bases classes.
            attributes : dict
                Attributes of the new type.
        """
        #list of children, even if empty, must be always present
        if "_children" not in attributes:
            raise ValueError("_children attribute must be present")

        #create dictionary for initializing class arguments
        clsDict = {}
        #iterate over children and add arguments to the dictionary
        #all arguments are initially have None value
        for attr in attributes["_children"]:
            #set the argument
            clsDict[attr['name']] = None
        #propagate documentation
        clsDict["__doc__"] = attributes.get("__doc__", None)

        #extend children list with that of base classes
        new = []
        for b in bases:
            base_children = getattr(b, "_children", None)
            if base_children is not None:
                #append
                new.extend(base_children)
        new.extend(attributes["_children"])
        attributes["_children"] = new

        #children property is passed through
        clsDict["_children"] = attributes["_children"]

        #add ComplexType to base list
        if XMLType not in bases:
            newBases = list(bases)
            newBases.append(XMLType)
            bases = tuple(newBases)

        #create new type
        return type.__new__(cls, name, bases, clsDict)

#the following is a modified copy from soaplib library

class XMLString(XMLType, str):
    def to_xml(self, parent, name):
        element = etree.SubElement(parent, name)
        element.text = unicode(self)

    def from_xml(self, element):
        if element.text:
            return element.text.encode('utf-8')
        else:
            return None

class XMLInteger(XMLType, int):
    def to_xml(self, parent, name):
        element = etree.SubElement(parent, name)
        element.text = repr(self)

    def from_xml(self, element):
        if element.text:
            try:
                return int(element.text)
            except:
                return long(element.text)
        return None

class XMLDouble(XMLType, float):
    def to_xml(self, parent, name):
        element = etree.SubElement(parent, name)
        element.text = repr(self)

    def from_xml(self, element):
        if element.text:
            return float(element.text)
        return None

class XMLBoolean(XMLType, str):
    def to_xml(self, parent, name):
        element = etree.SubElement(parent, name)
        if self in ('True', 'true', '1'):
            element.text = repr(True).lower()
        else:
            element.text = repr(False).lower()

    def from_xml(cls, element):
        if element.text:
            return (element.text.lower() in ['true', '1'])
        return None

class XMLAny(XMLType, str):
    def to_xml(self, parent, name):
        value = etree.fromstring(self)
        element = etree.SubElement(parent, name)
        element.append(value)

    def from_xml(self, element):
        children = element.getchildren()
        if children:
            return children[0]
        return None

class XMLDecimal(XMLType, Decimal):
    def to_xml(self, parent, name):
        element = etree.SubElement(parent, name)
        element.text = str(self)

    def from_xml(self, element):
        if element.text:
            return Decimal(element.text)
        return None

class XMLDate(XMLType):
    def __init__(self, *arg):
        if len(arg) == 1 and isinstance(arg[0], date):
            self.value = arg[0]
        else:
            self.value = date(2008, 11, 11)
    def to_xml(self, parent, name):
        element = etree.SubElement(parent, name)
        element.text = self.value.isoformat()

    def from_xml(self, element):
        """expect ISO formatted dates"""
        if not(element.text):
            return None
        text = element.text

        full = datetime.strptime(text, '%Y-%m-%d')

        return full.date()


class XMLDateTime(XMLType):
    def __init__(self, *arg):
        if len(arg) == 1 and isinstance(arg[0], datetime):
            self.value = arg[0]
        else:
            self.value = datetime(2008, 11, 11)
    def to_xml(self, parent, name):
        element = etree.SubElement(parent, name)
        element.text = self.value.isoformat('T')

    def from_xml(self, element):
        return datetime.strptime('2011-08-02T17:00:01.000122',
                                        '%Y-%m-%dT%H:%M:%S.%f')

class Message(object):
    """
        Message for input and output of service operations.

        Messages perform conversion of Python to xml and backwards
        of the calls and returns.

        Parameters
        ----------
        tag : str
            Name of the message.
        namespafe : str
            Namespace of the message.
        nsmap : dict
            Map of namespace prefixes.
        parts : list
            List of message parts in the form
            (part name, part type class).
        style : str
            Operation style document/rpc.
        literal : bool
            True = literal, False = encoded.
    """
    def __init__(self, tag, namespace, nsmap, parts, style, literal):
        self.tag = tag
        self.namespace = namespace
        self.nsmap = nsmap
        self.parts = parts
        self.style = style
        self.literal = literal

    def to_xml(self, *arg, **kw):
        """
            Convert from Python into xml message.
        """
        if self.style != "document" or not(self.literal):
            raise RuntimeError(
                "Only document/literal are supported. Improve Message class!")

        p = self.parts[0][1]() #encoding instance

        #wrapped message is supplied
        if len(arg) == 1 and isinstance(arg[0], self.parts[0][1]):
            for child in p._children:
                setattr(p, child['name'], getattr(arg[0], child['name'], None))
        else:
            #reconstruct wrapper from expanded input
            counter = 0
            for child in p._children:
                name = child["name"]
                #first try keyword
                val = kw.get(name, None)
                if val is None: #not keyword
                    if counter < len(arg):
                        #assume this is positional argument
                        val = arg[counter]
                        counter = counter + 1
                if val is None: #check if nillable
                    if child["min"] == 0:
                        continue
                    else:
                        raise ValueError(\
                                "Non-nillable parameter %s is not present"\
                                                                    %name)
                setattr(p, name, val)

        p.to_xml(kw["_body"], "{%s}%s" %(self.namespace, self.tag))

    def from_xml(self, body, header = None):
        """
            Convert from xml message to Python.
        """
        if self.style != "document" or not(self.literal):
            raise RuntimeError(
                "Only document/literal are supported. Improve Message class.")

        p = self.parts[0][1]() #decoding instance

        res = p.from_xml(body)

        #for wrapped doc style (the only one implemented) we now, that
        #wrapper has only one child, get it
        if len(p._children) == 1:
            return getattr(res, p._children[0]["name"], None)
        else:
            return res

class Method(object):
    """
        Definition of a single SOAP method, including the location, action, name
        and input and output classes.

        TODO: add a useful repr

        This is a copy from Scio.

        self.input - input message - to convert from Python to xml
        self.output - output message - to convert from xml to Python
    """
    def __init__(self, location, name, action, input, output, doc=None):
        self.location = location
        self.name = name
        self.action = action
        self.input = input
        self.output = output
        self.__doc__ = doc

    def __call__(self, *arg, **kw):
        """
            Process rpc-call.
        """
        #create soap-wrap around our message
        env = etree.Element('{%s}Envelope' % SOAPNS['soap-env'], nsmap=SOAPNS)
        header = etree.SubElement(env, '{%s}Header' % SOAPNS['soap-env'],
                                                                 nsmap=SOAPNS)
        body = etree.SubElement(env, '{%s}Body' % SOAPNS['soap-env'],
                                                                 nsmap=SOAPNS)

        #compose call message - convert all parameters and encode the call
        kw["_body"] = body
        self.input.to_xml(*arg, **kw)

        text_msg = etree.tostring(env) #message to send
        del env

        #http stuff
        request = Request(self.location, text_msg,
                                {'Content-Type': 'text/xml',
                                'SOAPAction': self.action})

        #real rpc
        try:
            response = urlopen(request).read()
        except HTTPError, e:
            if e.code in (202, 204):#empty returns
                pass
                #return self.client.handle_response(self.method, None)
            else:
                pass
                #return self.client.handle_error(self.method, e)
            raise

        #string to xml
        xml = etree.fromstring(response)
        del response

        #find soap body
        body = xml.find(SOAP_BODY)
        if body is None:
            raise NotSOAP("No SOAP body found in response", response)
        fault = body.find(SOAP_FAULT)
        if fault is not None:
            code = fault.find('faultcode')
            if code is not None:
                code = code.text
            string = fault.find('faultstring')
            if string is not None:
                string = string.text
            detail = fault.find('detail')
            if detail is not None:
                detail = detail.text
            raise RuntimeError("SOAP Fault %s:%s <%s> %s%s"\
                    %(method.location, method.name, code, string, detail))
        body = body[0] # hacky? get the first real element

        return self.output.from_xml(body)

def get_local_name(full_name):
    """
        Removes namespace part of the name.
    """
    full_name = full_name[full_name.find('}')+1:]
    full_name = full_name[full_name.find(':')+1:]
    return full_name
