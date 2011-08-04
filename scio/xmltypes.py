"""
    Python classes corresponding to XML schema.
"""
from exceptions import *
from soap import *
from lxml import etree
#import xml.etree.cElementTree as etree
from decimal import Decimal
from datetime import date, datetime, time

def toinit(self, deep = False):
    """
        Nice init for complex types.

        All obligatory (nonnillable) children can also be created.

        Parameters
        ----------
        deep : bool, optional, defaule False
            If True all non-nillable children are created, otherwise
            they are simplty None. The latter is used when
            converting response from XML to Python.
    """
    if not(deep):
        return
    for child in self._children:
        if child['min'] == 0:
            continue
        val_type = child['type']
        val = None
        if getattr(val_type, "_children", None) is not None:
            val = val_type(deep=deep)
        else:
            val = val_type()
        if child['max'] > 1:
            #'unbounded' > 1
            val = [val,]
        setattr(self, child['name'], val)

def tostr(self):
    """
        Nice printing facility for complex types.
    """
    children = ''
    for child in self._children:
        child_name = child['name']
        array = ''
        if child['max']>1:
             # 'unbounded'>1
             array = '[]'
        child_value = getattr(self, child_name, None)
        many = False
        if len(array) and isinstance(child_value, (list, tuple)):
            many = True
        shift = len(child_name) + len(array) + 7 # 4 comes from tab
        if many:
            shift = shift + 1
            tmp = child_value
            stop = len(child_value)
            after = '\n]'
            if stop > 10:
                stop = 10
                after = '\n...' + after
            child_value = ''
            for val in tmp:
                child_value = child_value + ',\n%s' %str(val)
            child_value = '[\n' + child_value[2:] + after
        else:
            child_value = str(child_value)
        child_value = child_value.replace('\n', '\n%s' %(' '*shift))
        descr = '    %s%s = %s' %(child_name, array, child_value)
        children = children + '\n%s' %descr
    res = '(%s){%s\n}' %(self.__class__.__name__, children)

    return res

def torepr(self):
    """
        Nice printing facility for complex types.
    """
    return tostr(self)

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

        #now all children were processed, so remove them to save memory
        element.clear()

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
        #add nice printing
        clsDict["__str__"] = tostr
        clsDict["__repr__"] = torepr
        #add complex init
        clsDict["__init__"] = toinit

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
    _types = {} #dict of known types
    def to_xml(self, parent, name):
        value = etree.fromstring(self)
        element = etree.SubElement(parent, name)
        element.append(value)

    def from_xml(self, element):
        #try to find types
        type = element.get('{http://www.w3.org/2001/XMLSchema-instance}type',
                                                                        None)
        if type is None:
            return element
        type = get_local_name(type)
        type_class = self._types.get(type, None)
        if type_class is not None:
            res = type_class()
            return res.from_xml(element)
        else:
            return element

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
