#!/usr/bin/env python
# test_message.py - test Message class, part of osa.
# Copyright 2013 Sergey Bozhenkov, boz at ipp.mpg.de
# Licensed under LGPLv3 or later, see the COPYING file.

import sys
sys.path.insert(0, "../")
from osa.xmlschema import *
from osa.xmlparser import *
from osa.message import *
from tests.base import BaseTest
import xml.etree.cElementTree as etree
import unittest


class TestMessage(BaseTest):

    def setUp(self):
        root = parse_qualified_from_url(self.test_files["schema.xml"])
        schema = XMLSchemaParser(root)
        xtypes = schema.get_list_of_defined_types()
        self.types = XMLSchemaParser.convert_xmltypes_to_python(xtypes)

    def tearDown(self):
        self.types = None

    def test_toxml(self):
        message = Message("{vostok}msg",
                          [["add", self.types["{vostok}Person"]],
                           ["params", self.types["{vostok}Name"]],
                           ["params", self.types["{sever}Car"]]])

        #empty
        root = etree.Element("root")
        message.to_xml(_body=root)

        #name
        message.use_parts = [message.parts[1]]
        #empty input=> exception
        self.assertRaises(ValueError, message.to_xml, _body=root)
        #single instance, wrong type => exception, the same path as above
        car = self.types["{sever}Car"]()
        car.model = "zaz"
        self.assertRaises(ValueError, message.to_xml, car, _body=root)
        #single instance of proper type
        name = self.types["{vostok}Name"]()
        name.firstName = "bobo"
        name.lastName = "khnyk"
        message.to_xml(name, _body=root)
        self.assertEqual(len(root), 1)
        self.assertEqual(root[0].tag, "{vostok}Name")
        self.assertEqual(len(root[0]), 2)
        #positional parameters
        root = etree.Element("root")
        message.to_xml("bobik", "sharikov", _body=root)
        self.assertEqual(len(root), 1)
        self.assertEqual(root[0].tag, "{vostok}Name")
        self.assertEqual(len(root[0]), 2)
        #keyword parameters
        root = etree.Element("root")
        message.to_xml(lastName = "zaa", firstName="yoyo", _body=root)
        self.assertEqual(len(root), 1)
        self.assertEqual(root[0].tag, "{vostok}Name")
        self.assertEqual(len(root[0]), 2)

    def test_fromxml(self):
        root = etree.Element("Name")
        fn = etree.SubElement(root, "firstName")
        fn.text = "kolo"
        sn = etree.SubElement(root, "lastName")
        sn.text = "bok"

        message = Message("{vostok}msg", [["add", self.types["{vostok}Person"]],
                                  ["params", self.types["{vostok}Name"]],
                                  ["params", self.types["{sever}Car"]],
                                  ])
        message.use_parts = [message.parts[1]]
        res = message.from_xml(root)
        self.assertEqual(res.__class__.__name__, "Name")
        self.assertEqual(res.firstName, "kolo")
        self.assertEqual(res.lastName, "bok")
