#!/usr/bin/env python
# test_xmltypes_primitive.py - test serialization of primitive classes, part of osa.
# Copyright 2013 Sergey Bozhenkov, boz at ipp.mpg.de
# Licensed under GPLv3 or later, see the COPYING file.

import sys
for x in sys.path:
    if x.find("osa") != -1:
        sys.path.remove(x)
sys.path.append("../")

from osa.xmltypes import *
from datetime import datetime
import unittest
import xml.etree.cElementTree as etree

ns_test = 'test_namespace'

class TestPrimitive(unittest.TestCase):
    def test_string(self):
        s = XMLString("value")
        element = etree.Element('test')
        s.to_xml(element, "{%s}%s" %(ns_test, "atach"))
        element=element[0]

        self.assertEquals(element.text, 'value')
        value = XMLString().from_xml(element)
        self.assertEquals(value, 'value')
    
    def test_stringenumeration(self):
        XMLStringEnumeration._allowedValues = ["me", "you"]
        s1 = XMLStringEnumeration("me")
        self.assertEquals(s1.value, "me")
        s2 = XMLStringEnumeration("he")
        self.assertEquals(s2.value, "he")

        #toxml
        element = etree.Element('test')
        s1.to_xml(element, "{%s}%s" %(ns_test, "atach"))
        element=element[0]
        self.assertEquals(element.text, 'me')

        element2 = etree.Element('test')
        self.assertRaises(ValueError, s2.to_xml, element2, "{%s}%s" %(ns_test, "atach"))

        #back
        value = XMLStringEnumeration().from_xml(element)
        self.assertEquals(value, 'me')
        element.text="he"
        self.assertRaises(ValueError, XMLStringEnumeration().from_xml, element)

    def test_datetime(self):
        d = XMLDateTime(datetime.now())

        element = etree.Element('test')
        d.to_xml(element, "{%s}%s" %(ns_test, "atach"))
        element = element[0]

        self.assertEquals(element.text, d.value.isoformat())
        dt = XMLDateTime().from_xml(element)
        self.assertEquals(d.value, dt)

    def test_date(self):
        x = datetime.now()
        x = x.date()
        d = XMLDate(x)

        element = etree.Element('test')
        d.to_xml(element, "{%s}%s" %(ns_test, "atach"))
        element = element[0]

        self.assertEquals(element.text, d.value.isoformat())
        dt = XMLDate().from_xml(element)
        self.assertEquals(d.value, dt)

    def test_integer(self):
        integer = XMLInteger(12)

        element = etree.Element('test')
        integer.to_xml(element, "{%s}%s" %(ns_test, "atach"))
        element = element[0]

        self.assertEquals(element.text, '12')
        value = XMLInteger().from_xml(element)
        self.assertEquals(value, integer)

    def test_large_integer(self):
        integer = XMLInteger(128375873458473)

        element = etree.Element('test')
        integer.to_xml(element, "{%s}%s" %(ns_test, "atach"))
        element = element[0]

        self.assertEquals(element.text, '128375873458473')
        value = XMLInteger().from_xml(element)
        self.assertEquals(value, integer)

    def test_float(self):
        f = XMLDouble(1.0/3.0)
        element = etree.Element('test')
        f.to_xml(element, "{%s}%s" %(ns_test, "atach"))
        element = element[0]

        self.assertEquals(element.text, repr(f))

        f2 = XMLDouble().from_xml(element)
        self.assertEquals(f2, f)

    def test_unicode(self):
        s = XMLString(u'\x34\x55\x65\x34')
        self.assertEquals(4, len(s))
        element = etree.Element('test')
        s.to_xml(element, "{%s}%s" %(ns_test, "atach"))
        element = element[0]
        value = XMLString().from_xml(element)
        self.assertEquals(value, s)

    def test_boolean(self):
        b = etree.Element('test')
        XMLBoolean(True).to_xml(b, "{%s}%s" %(ns_test, "atach"))
        b = b[0]
        self.assertEquals('true', b.text)

        b = etree.Element('test')
        XMLBoolean(0).to_xml(b, "{%s}%s" %(ns_test, "atach"))
        b = b[0]
        self.assertEquals('false', b.text)

        b = etree.Element('test')
        XMLBoolean(1).to_xml(b, "{%s}%s" %(ns_test, "atach"))
        b = b[0]
        self.assertEquals('true', b.text)

        b = XMLBoolean().from_xml(b)
        self.assertEquals(b, True)

        b = etree.Element('test')
        XMLBoolean(False).to_xml(b, "{%s}%s" %(ns_test, "atach"))
        b = b[0]
        self.assertEquals('false', b.text)

        b = XMLBoolean().from_xml(b)
        self.assertEquals(b, False)

        b = etree.Element('test')
        b.text = ''
        b = XMLBoolean().from_xml(b)
        self.assertEquals(b, None)

    def test_any(self):
        #test any from_xml, the other way is
        #should not be used in real life in any case
        element = etree.Element('test')
        element.text = "10.0"

        #no type => xml
        inst = XMLAny()
        v = inst.from_xml(element)
        self.assertEquals(type(v).__name__ , "Element")

        #float
        element.set("{%s}type" %xmlnamespace.NS_XSI, "{%s}float" %xmlnamespace.NS_XSD)
        v = inst.from_xml(element)
        self.assertEquals(v.__class__.__name__, "float")
        self.assertEquals(v, 10.0)

        #string
        element.set("{%s}type" %xmlnamespace.NS_XSI, "{%s}string" %xmlnamespace.NS_XSD)
        v = inst.from_xml(element)
        self.assertEquals(v.__class__.__name__, "str")
        self.assertEquals(v, "10.0")





if __name__ == '__main__':
    unittest.main()
