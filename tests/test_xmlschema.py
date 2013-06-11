#!/usr/bin/env python
# test_xmlschema.py - test schema parsing, part of osa.
# Copyright 2013 Sergey Bozhenkov, boz at ipp.mpg.de
# Licensed under GPLv3 or later, see the COPYING file.

import sys
for x in sys.path:
    if x.find("osa") != -1:
        sys.path.remove(x)
sys.path.append("../")

import unittest
import xml.etree.cElementTree as etree
from osa.xmlschema import *
from osa.xmlparser import *

class TestXMLSchema(unittest.TestCase):
    def setUp(self):
        root = parse_qualified_from_url("schema.xml")
        self.schema = XMLSchemaParser(root)
    def tearDown(self):
        self.schema = None
    def test_get_list_of_types(self):
        res = self.schema.get_list_of_defined_types()
        self.assertTrue(res.has_key("{vostok}Name"))
        self.assertEquals(res["{vostok}Name"].tag, "{%s}complexType" %xmlnamespace.NS_XSD)
        self.assertEquals(res["{vostok}Name"].get("name"), "Name")
        self.assertTrue(res.has_key("{vostok}Person"))
        self.assertEquals(res["{vostok}Person"].tag, "{%s}element" %xmlnamespace.NS_XSD)
        self.assertEquals(res["{vostok}Person"].get("name"), "Person")
        self.assertTrue(res.has_key("{vostok}Robot"))
        self.assertEquals(res["{vostok}Robot"].tag, "{%s}element" %xmlnamespace.NS_XSD)
        self.assertEquals(res["{vostok}Robot"].get("name"), "Robot")
        self.assertTrue(res.has_key("{vostok}Counter"))
        self.assertEquals(res["{vostok}Counter"].tag, "{%s}simpleType" %xmlnamespace.NS_XSD)
        self.assertEquals(res["{vostok}Counter"].get("name"), "Counter")
        self.assertTrue(res.has_key("{vostok}Profession"))
        self.assertEquals(res["{vostok}Profession"].tag, "{%s}simpleType" %xmlnamespace.NS_XSD)
        self.assertEquals(res["{vostok}Profession"].get("name"), "Profession")
        self.assertTrue(res.has_key("{vostok}Shish"))
        self.assertEquals(res["{vostok}Shish"].tag, "{%s}element" %xmlnamespace.NS_XSD)
        self.assertEquals(res["{vostok}Shish"].get("name"), "Shish")
        self.assertTrue(res.has_key("{zapad}Address"))
        self.assertEquals(res["{zapad}Address"].tag, "{%s}complexType" %xmlnamespace.NS_XSD)
        self.assertEquals(res["{zapad}Address"].get("name"), "Address")
        self.assertTrue(res.has_key("{sever}Car"))
        self.assertEquals(res["{sever}Car"].tag, "{%s}complexType" %xmlnamespace.NS_XSD)
        self.assertEquals(res["{sever}Car"].get("name"), "Car")
    def test_convert(self):
        xtypes = self.schema.get_list_of_defined_types()
        types = XMLSchemaParser.convert_xmltypes_to_python(xtypes)
        self.assertEqual(types["{vostok}Name"].__class__.__name__, "ComplexTypeMeta")
        self.assertTrue(types.has_key("{vostok}Name"))
        self.assertTrue(hasattr(types["{vostok}Name"], "firstName"))
        self.assertTrue(hasattr(types["{vostok}Name"], "lastName"))
        self.assertEquals(types["{vostok}Name"]._namespace, "vostok")
        self.assertTrue(types.has_key("{vostok}Person"))
        self.assertEqual(types["{vostok}Person"].__class__.__name__, "ComplexTypeMeta")
        self.assertTrue(hasattr(types["{vostok}Person"], "age"))
        self.assertTrue(hasattr(types["{vostok}Person"], "weight"))
        self.assertTrue(hasattr(types["{vostok}Person"], "name"))
        self.assertTrue(hasattr(types["{vostok}Person"], "place"))
        self.assertTrue(hasattr(types["{vostok}Person"], "car"))
        self.assertTrue(hasattr(types["{vostok}Person"], "Comment"))
        self.assertEquals(types["{vostok}Person"]._namespace, "vostok")
        self.assertTrue(types.has_key("{vostok}Robot"))
        self.assertEqual(types["{vostok}Robot"].__class__.__name__, "ComplexTypeMeta")
        self.assertTrue(hasattr(types["{vostok}Robot"], "age"))
        self.assertTrue(hasattr(types["{vostok}Robot"], "weight"))
        self.assertTrue(hasattr(types["{vostok}Robot"], "name"))
        self.assertTrue(hasattr(types["{vostok}Robot"], "place"))
        self.assertTrue(hasattr(types["{vostok}Robot"], "car"))
        self.assertTrue(hasattr(types["{vostok}Robot"], "Comment"))
        self.assertEquals(types["{vostok}Robot"]._namespace, "vostok")
        self.assertTrue(types.has_key("{vostok}Counter"))
        self.assertEquals(types["{vostok}Counter"].__base__.__name__, "XMLInteger")
        self.assertTrue(isinstance(types["{vostok}Counter"](), int))
        self.assertEquals(types["{vostok}Counter"]._namespace, "vostok")
        self.assertTrue(types.has_key("{vostok}Profession"))
        self.assertEquals(len(types["{vostok}Profession"]._allowedValues), 2)
        self.assertTrue("cosmonaut" in types["{vostok}Profession"]._allowedValues)
        self.assertTrue("scientist" in types["{vostok}Profession"]._allowedValues)
        self.assertEquals(types["{vostok}Profession"]._namespace, "vostok")
        self.assertEquals(types["{vostok}Profession"].__base__.__name__, "XMLStringEnumeration")
        self.assertTrue(types.has_key("{vostok}Shish"))
        self.assertEqual(types["{vostok}Shish"].__class__.__name__, "ComplexTypeMeta")
        self.assertEqual(len(types["{vostok}Shish"]._children), 0)
        self.assertTrue(types.has_key("{zapad}Address"))
        self.assertTrue(hasattr(types["{zapad}Address"], "city"))
        self.assertTrue(hasattr(types["{zapad}Address"], "country"))
        self.assertEquals(types["{zapad}Address"]._namespace, "zapad")
        self.assertEqual(types["{zapad}Address"].__class__.__name__, "ComplexTypeMeta")
        self.assertTrue(types.has_key("{sever}Car"))
        self.assertTrue(hasattr(types["{sever}Car"], "model"))
        self.assertTrue(hasattr(types["{sever}Car"], "weight"))
        self.assertEquals(types["{sever}Car"]._namespace, "sever")
        self.assertEqual(types["{sever}Car"].__class__.__name__, "ComplexTypeMeta")
if __name__ == '__main__':
    unittest.main()
