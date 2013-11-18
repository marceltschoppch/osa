#!/usr/bin/env python
# test_xmltypes_primitive.py - test serialization of primitive classes, part of osa.
# Copyright 2013 Sergey Bozhenkov, boz at ipp.mpg.de
# Licensed under LGPLv3 or later, see the COPYING file.

import sys
sys.path.insert(0, "../")
from osa.xmltypes import *
from tests.base import BaseTest
from datetime import datetime
import xml.etree.cElementTree as etree
import unittest


ns_test = 'test_namespace'


class TestPrimitive(BaseTest):

    def test_string(self):
        s = XMLString("value")
        element = etree.Element('test')
        s.to_xml(element, "{%s}%s" %(ns_test, "atach"))
        element=element[0]

        self.assertEqual(element.text, 'value')
        value = XMLString().from_xml(element)
        self.assertEqual(value, 'value')

        #empty element test, bug 7
        element.text = None
        value = XMLString().from_xml(element)
        self.assertEqual(value, "")

    def test_stringenumeration(self):
        XMLStringEnumeration._allowedValues = ["me", "you"]
        s1 = XMLStringEnumeration("me")
        self.assertEqual(s1.value, "me")
        s2 = XMLStringEnumeration("he")
        self.assertEqual(s2.value, "he")

        #toxml
        element = etree.Element('test')
        s1.to_xml(element, "{%s}%s" %(ns_test, "atach"))
        element=element[0]
        self.assertEqual(element.text, 'me')

        element2 = etree.Element('test')
        self.assertRaises(ValueError, s2.to_xml, element2, "{%s}%s" %(ns_test, "atach"))

        #back
        value = XMLStringEnumeration().from_xml(element)
        self.assertEqual(value, 'me')
        element.text="he"
        self.assertRaises(ValueError, XMLStringEnumeration().from_xml, element)

        #empty element test, bug 7
        element.text = None
        XMLStringEnumeration._allowedValues.append("")
        value = XMLStringEnumeration().from_xml(element)
        self.assertEqual(value, "")

    def test_datetime(self):
        d = XMLDateTime(datetime.now())

        element = etree.Element('test')
        d.to_xml(element, "{%s}%s" %(ns_test, "atach"))
        element = element[0]

        self.assertEqual(element.text, d.value.isoformat())
        dt = XMLDateTime().from_xml(element)
        self.assertEqual(d.value, dt)

        #empty element test, bug 7
        element.text = None
        value = XMLDateTime().from_xml(element)
        self.assertEqual(value, datetime(1970,1,1))

        element.text = "2012-01-31T10:00:00.538"
        value = XMLDateTime().from_xml(element)
        self.assertEqual(value, datetime(2012,01,31, 10, 0, 0, 538000))
        element.text = "2012-01-30T10:00:00"
        value = XMLDateTime().from_xml(element)
        self.assertEqual(value, datetime(2012,01,30, 10, 0, 0))
        element.text = "2012-01-20T10:00:00UTC"
        value = XMLDateTime().from_xml(element)
        self.assertEqual(value, datetime(2012,01,20, 10, 0, 0))
        element.text = "2012-01-10T10:00:00Z"
        value = XMLDateTime().from_xml(element)
        self.assertEqual(value, datetime(2012,01,10, 10, 0, 0))
        # with time zone - bug 9
        element.text = "2012-01-31T10:00:00.538+02:30"
        value = XMLDateTime().from_xml(element)
        self.assertEqual(value, datetime(2012,01,31, 7, 30, 0, 538000))
        element.text = "2012-01-30T01:00:00+01:30"
        value = XMLDateTime().from_xml(element)
        self.assertEqual(value, datetime(2012,01,29, 23, 30, 0))
        element.text = "2012-01-31T10:00:00.538-02:30"
        value = XMLDateTime().from_xml(element)
        self.assertEqual(value, datetime(2012,01,31, 12, 30, 0, 538000))
        element.text = "2012-01-31T10:00:00-01:00"
        value = XMLDateTime().from_xml(element)
        self.assertEqual(value, datetime(2012,01,31, 11, 00, 0))

    def test_date(self):
        x = datetime.now()
        x = x.date()
        d = XMLDate(x)

        element = etree.Element('test')
        d.to_xml(element, "{%s}%s" %(ns_test, "atach"))
        element = element[0]

        self.assertEqual(element.text, d.value.isoformat())
        dt = XMLDate().from_xml(element)
        self.assertEqual(d.value, dt)
         
        #empty element test, bug 7
        element.text = None
        value = XMLDate().from_xml(element)
        self.assertEqual(value, date(1970,1,1))

        element.text = "2013-01-31UTC"
        value = XMLDate().from_xml(element)
        self.assertEqual(value, date(2013,01,31))
        element.text = "2013-02-11Z"
        value = XMLDate().from_xml(element)
        self.assertEqual(value, date(2013,02,11))
        # with time zone - bug 9
        element.text = "2012-01-31+06:00"
        value = XMLDate().from_xml(element)
        self.assertEqual(value, date(2012,01,31))
        element.text = "2012-02-20-04:00"
        value = XMLDate().from_xml(element)
        self.assertEqual(value, date(2012,02,20))

    def test_integer(self):
        integer = XMLInteger(12)

        element = etree.Element('test')
        integer.to_xml(element, "{%s}%s" %(ns_test, "atach"))
        element = element[0]

        self.assertEqual(element.text, '12')
        value = XMLInteger().from_xml(element)
        self.assertEqual(value, integer)

        #empty element test, bug 7
        element.text = None
        value = XMLInteger().from_xml(element)
        self.assertEqual(value, 0)

    def test_large_integer(self):
        integer = XMLInteger(128375873458473)

        element = etree.Element('test')
        integer.to_xml(element, "{%s}%s" %(ns_test, "atach"))
        element = element[0]

        self.assertEqual(element.text, '128375873458473')
        value = XMLInteger().from_xml(element)
        self.assertEqual(value, integer)

    def test_float(self):
        f = XMLDouble(1.0/3.0)
        element = etree.Element('test')
        f.to_xml(element, "{%s}%s" %(ns_test, "atach"))
        element = element[0]

        self.assertEqual(element.text, repr(f))

        f2 = XMLDouble().from_xml(element)
        self.assertEqual(f2, f)
         
        #empty element test, bug 7
        element.text = None
        value = XMLDouble().from_xml(element)
        self.assertEqual(value, 0)

    def test_unicode(self):
        s = XMLString('\x34\x55\x65\x34')
        self.assertEqual(4, len(s))
        element = etree.Element('test')
        s.to_xml(element, "{%s}%s" %(ns_test, "atach"))
        element = element[0]
        value = XMLString().from_xml(element)
        self.assertEqual(value, s)

    def test_boolean(self):
        b = etree.Element('test')
        XMLBoolean(True).to_xml(b, "{%s}%s" %(ns_test, "atach"))
        b = b[0]
        self.assertEqual('true', b.text)

        b = etree.Element('test')
        XMLBoolean(0).to_xml(b, "{%s}%s" %(ns_test, "atach"))
        b = b[0]
        self.assertEqual('false', b.text)

        b = etree.Element('test')
        XMLBoolean(1).to_xml(b, "{%s}%s" %(ns_test, "atach"))
        b = b[0]
        self.assertEqual('true', b.text)

        b = XMLBoolean().from_xml(b)
        self.assertEqual(b, True)

        b = etree.Element('test')
        XMLBoolean(False).to_xml(b, "{%s}%s" %(ns_test, "atach"))
        b = b[0]
        self.assertEqual('false', b.text)

        b = XMLBoolean().from_xml(b)
        self.assertEqual(b, False)

        b = etree.Element('test')
        b.text = ''
        b = XMLBoolean().from_xml(b)
        self.assertEqual(b, False)

    def test_any(self):
        #test any from_xml, the other way is
        #should not be used in real life in any case
        element = etree.Element('test')
        element.text = "10.0"

        #no type => xml
        inst = XMLAny()
        v = inst.from_xml(element)
        self.assertEqual(type(v).__name__ , "Element")

        #float
        element.set("{%s}type" %xmlnamespace.NS_XSI, "{%s}float" %xmlnamespace.NS_XSD)
        v = inst.from_xml(element)
        self.assertEqual(v.__class__.__name__, "float")
        self.assertEqual(v, 10.0)

        #string
        element.set("{%s}type" %xmlnamespace.NS_XSI, "{%s}string" %xmlnamespace.NS_XSD)
        v = inst.from_xml(element)
        self.assertEqual(v.__class__.__name__, "str")
        self.assertEqual(v, "10.0")
