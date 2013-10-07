#!/usr/bin/env python
# test_wsdl.py - test WSDLParser class, part of osa.
# Copyright 2013 Sergey Bozhenkov, boz at ipp.mpg.de
# Licensed under LGPLv3 or later, see the COPYING file.

import sys
sys.path.insert(0, "../")
from osa.wsdl import *
from osa.method import *
from osa.message import *
from osa.xmltypes import *
from tests.base import BaseTest
import xml.etree.cElementTree as etree
import unittest

wsdl_url = 'test.wsdl'
ns1 = "de.mpg.ipp.hgw.boz.gsoap.helloworld"
ns2 = "de.mpg.ipp.hgw.boz.gsoap.helloworld.types"


class TestWSDL(unittest.TestCase):

    def test_reading(self):
        w = WSDLParser(wsdl_url)
        self.assertEqual(w.wsdl_url, wsdl_url)
        self.assertEqual(w.tns, "de.mpg.ipp.hgw.boz.gsoap.helloworld")
        self.assertEqual(type(w.wsdl), type(etree.Element('root')))

    def test_get_types(self):
        w = WSDLParser(wsdl_url)
        types = w.get_types()
        self.assertTrue('{%s}Name' %ns2 in types.keys())
        self.assertTrue('{%s}Person' %ns2 in types.keys())
        self.assertTrue('{%s}echoString' %ns1 in types.keys())
        self.assertTrue('{%s}faultyThing' %ns1 in types.keys())
        self.assertTrue('{%s}testMe' %ns1 in types.keys())
        self.assertTrue('{%s}sayHello' %ns1 in types.keys())
        self.assertTrue('{%s}echoStringResponse' %ns1 in types.keys())
        self.assertTrue('{%s}faultyThingResponse' %ns1 in types.keys())
        self.assertTrue('{%s}sayHelloResponse' %ns1 in types.keys())
        self.assertTrue(types['{%s}Name' %ns2], 'firstName')
        self.assertTrue(types['{%s}Name' %ns2], 'lastName')
        self.assertTrue(types['{%s}Person' %ns2], 'name')
        self.assertTrue(types['{%s}Person' %ns2], 'age')
        self.assertTrue(types['{%s}Person' %ns2], 'height')
        self.assertTrue(types['{%s}Person' %ns2], 'weight')
        self.assertTrue(types['{%s}Person' %ns2]._children[3]['name'] == "name")
        self.assertTrue(types['{%s}Person' %ns2]._children[0]['name'] == "age")
        self.assertTrue(types['{%s}Person' %ns2]._children[3]['type'] == types['{%s}Name' %ns2])
        self.assertTrue(types['{%s}Person' %ns2]._children[0]['type'] == xmltypes.XMLInteger)
        self.assertTrue(types['{%s}sayHello' %ns1], 'person')
        self.assertTrue(types['{%s}sayHello' %ns1], 'times')
        self.assertTrue(types['{%s}sayHello' %ns1]._children[0]['name'] == "person")
        self.assertTrue(types['{%s}sayHello' %ns1]._children[1]['name'] == "times")
        self.assertTrue(types['{%s}sayHello' %ns1]._children[0]['type'] == types['{%s}Person' %ns2])
        self.assertTrue(types['{%s}sayHello' %ns1]._children[1]['type'] == xmltypes.XMLInteger)

    def test_get_messages(self):
        w = WSDLParser(wsdl_url)
        types = w.get_types()
        msgs = w.get_messages(types)
        names = ("testMe", "giveMessageRequest",
                 "giveMessageResponse", "echoStringRequest",
                 "echoStringResponse", "faultyThingRequest",
                 "faultyThingResponse", "sayHello",
                 "sayHelloResponse")
        for n in names:
            self.assertTrue("{%s}%s" %(ns1, n) in msgs)
            m = msgs["{%s}%s" %(ns1, n)]
            self.assertTrue(isinstance(m, Message))
            self.assertEqual(m.name, "{%s}%s" %(ns1, n))
            self.assertEqual(len(m.parts), 1)
            self.assertEqual(len(m.parts[0]), 2)
            self.assertEqual(m.parts[0][0], "parameters")

    def test_get_operations(self):
        w = WSDLParser(wsdl_url)
        types = w.get_types()
        msgs = w.get_messages(types)
        ops = w.get_operations(msgs)
        self.assertTrue("{%s}HelloWorldServicePortType" %ns1 in ops)
        ops = ops["{%s}HelloWorldServicePortType" %ns1]
        names = ("testMe", "giveMessage", "echoString", "faultyThing", "sayHello")
        for n in names:
            self.assertTrue(n in ops)
            op = ops[n]
            self.assertTrue(isinstance(op, Method))
            self.assertTrue(isinstance(op.input, Message))
            if n != "testMe":
                self.assertTrue(isinstance(op.output, Message))

        self.assertTrue(ops["testMe"].input is msgs["{%s}testMe" %ns1])
        self.assertTrue(ops["giveMessage"].input is msgs["{%s}giveMessageRequest" %ns1])
        self.assertTrue(ops["giveMessage"].output is msgs["{%s}giveMessageResponse" %ns1])
        self.assertTrue(ops["echoString"].input is msgs["{%s}echoStringRequest" %ns1])
        self.assertTrue(ops["echoString"].output is msgs["{%s}echoStringResponse" %ns1])
        self.assertTrue(ops["faultyThing"].input is msgs["{%s}faultyThingRequest" %ns1])
        self.assertTrue(ops["faultyThing"].output is msgs["{%s}faultyThingResponse" %ns1])
        self.assertTrue(ops["sayHello"].input is msgs["{%s}sayHello" %ns1])
        self.assertTrue(ops["sayHello"].output is msgs["{%s}sayHelloResponse" %ns1])

    def test_get_bindings(self):
        w = WSDLParser(wsdl_url)
        types = w.get_types()
        msgs = w.get_messages(types)
        ops = w.get_operations(msgs)
        bs = w.get_bindings(ops)
        ops = ops["{%s}HelloWorldServicePortType" %ns1]
        self.assertTrue("{%s}HelloWorldService" %ns1 in bs)
        bs = bs["{%s}HelloWorldService" %ns1]
        names = ("testMe", "giveMessage", "echoString", "faultyThing", "sayHello")
        for n in names:
            self.assertTrue(n in bs)
            b = bs[n]
            op = ops[n]
            self.assertTrue(b is op)
            self.assertTrue(b.input.use_parts is not None)
            self.assertEqual(len(b.input.use_parts), 1)
            self.assertEqual(b.input.use_parts[0][0], "parameters")
            if n != "testMe":
                self.assertEqual(len(b.output.use_parts), 1)
                self.assertEqual(b.output.use_parts[0][0], "parameters")
            self.assertEqual(b.action, "")

    def test_get_services(self):
        w = WSDLParser(wsdl_url)
        types = w.get_types()
        msgs = w.get_messages(types)
        ops = w.get_operations(msgs)
        bs = w.get_bindings(ops)
        ss = w.get_services(bs)
        bs = bs["{%s}HelloWorldService" %ns1]
        self.assertTrue("HelloWorldService" in ss)
        ss = ss["HelloWorldService"]
        names = ("testMe", "giveMessage", "echoString", "faultyThing", "sayHello")
        for n in names:
            self.assertTrue(n in ss)
            s = ss[n]
            b = bs[n]
            self.assertTrue(s is b)
            self.assertEqual(s.location, "http://lxpowerboz:88/services/cpp/HelloWorldService")
