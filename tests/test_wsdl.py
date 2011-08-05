#!/usr/bin/env python

import sys
for x in sys.path:
    if x.find("osa") != -1:
        sys.path.remove(x)
sys.path.append("../")

import datetime
import unittest

import xml.etree.cElementTree as etree

from osa.wsdl import WSDLParser, _primmap
from osa.methods import Method
from osa.xmltypes import *

wsdl_url = 'http://lxpowerboz:88/services/python/HelloWorldService?wsdl'

class TestWSDL(unittest.TestCase):
    def test_reading(self):
        w = WSDLParser(wsdl_url)
        self.assertEquals(w.wsdl_url, wsdl_url)
        self.assertEquals(w.tns, 'helloworldservice.soaplib.boz.hgw.ipp.mpg.de')
        self.assertEquals(type(w.wsdl), type(etree.Element('root')))

    def test_service_name(self):
        w = WSDLParser(wsdl_url)
        self.assertEquals(w.get_service_names(), ["HelloWorldService"])

    def test_conversions(self):
        w = WSDLParser(wsdl_url)
        types = w.get_types(_primmap)
        self.assertTrue('Name' in types.keys())
        self.assertTrue('Person' in types.keys())
        self.assertTrue('echoString' in types.keys())
        self.assertTrue('faultyThing' in types.keys())
        self.assertTrue('testMe' in types.keys())
        self.assertTrue('sayHello' in types.keys())
        self.assertTrue('echoStringResponse' in types.keys())
        self.assertTrue('faultyThingResponse' in types.keys())
        self.assertTrue('testMeResponse' in types.keys())
        self.assertTrue('sayHelloResponse' in types.keys())
        self.assertTrue(types['Name'], 'firstName')
        self.assertTrue(types['Name'], 'lastName')
        self.assertTrue(types['Person'], 'name')
        self.assertTrue(types['Person'], 'age')
        self.assertTrue(types['Person'], 'height')
        self.assertTrue(types['Person'], 'weight')
        self.assertTrue(types['Person']._children[0]['name'] == "name")
        self.assertTrue(types['Person']._children[2]['name'] == "age")
        self.assertTrue(types['Person']._children[0]['type'] == types['Name'])
        self.assertTrue(types['Person']._children[2]['type'] == types['int'])
        self.assertTrue(types['sayHello'], 'person')
        self.assertTrue(types['sayHello'], 'times')
        self.assertTrue(types['sayHello']._children[0]['name'] == "person")
        self.assertTrue(types['sayHello']._children[1]['name'] == "times")
        self.assertTrue(types['sayHello']._children[0]['type'] == types['Person'])
        self.assertTrue(types['sayHello']._children[1]['type'] == types['int'])
        methods = w.get_methods(types)
        self.assertTrue('testMe' in methods.keys())
        self.assertTrue('giveMessage' in methods.keys())
        self.assertTrue('echoString' in methods.keys())
        self.assertTrue('sayHello' in methods.keys())
        self.assertTrue('faultyThing' in methods.keys())
        self.assertTrue(isinstance(methods['testMe'], Method))
        self.assertTrue(isinstance(methods['giveMessage'], Method))
        self.assertTrue(isinstance(methods['echoString'], Method))
        self.assertTrue(isinstance(methods['sayHello'], Method))
        self.assertTrue(isinstance(methods['faultyThing'], Method))

    def test_methods(self):
        w = WSDLParser(wsdl_url)
        types = w.get_types(_primmap)
        methods = w.get_methods(types)

        root = etree.Element('root')
        self.assertEquals(len(root), 0)
        methods['testMe'].input.to_xml(_body = root)
        self.assertEquals(len(root), 1)

        root = etree.Element('root')
        self.assertEquals(len(root), 0)
        methods['giveMessage'].input.to_xml(_body = root)
        self.assertEquals(len(root), 1)

        root = etree.Element('root')
        self.assertEquals(len(root), 0)
        methods['faultyThing'].input.to_xml(_body = root)
        self.assertEquals(len(root), 1)

        root = etree.Element('root')
        self.assertEquals(len(root), 0)
        methods['echoString'].input.to_xml(msg = 'message', _body = root)
        self.assertEquals(len(root), 1)
        self.assertEquals('message', XMLString().from_xml(root[0][0]))
        root = etree.Element('root')
        self.assertEquals(len(root), 0)
        methods['echoString'].input.to_xml('message', _body = root)
        self.assertEquals(len(root), 1)
        self.assertEquals('message', XMLString().from_xml(root[0][0]))
        root = etree.Element('root')
        self.assertEquals(len(root), 0)
        mm = types['echoString']()
        mm.msg = 'message'
        methods['echoString'].input.to_xml(mm, _body = root)
        self.assertEquals(len(root), 1)
        self.assertEquals('message', XMLString().from_xml(root[0][0]))

        n = types['Name']()
        n.firstName = "first"
        n.lastName = "last"
        p = types['Person']()
        p.name = n
        p.age = 30
        p.weight = 80
        p.height = 175
        t = 5
        root = etree.Element('root')
        self.assertEquals(len(root), 0)
        methods['sayHello'].input.to_xml(person = p, times = t, _body = root)
        self.assertEquals(len(root), 1)
        self.assertEquals(len(root[0]), 2)
        rp = types['Person']().from_xml(root[0][0])
        rt = types['int']().from_xml(root[0][1])
        self.assertEquals(rt, t)
        self.assertEquals(rp.age, p.age)
        self.assertEquals(rp.weight, p.weight)
        self.assertEquals(rp.height, p.height)
        self.assertEquals(rp.name.firstName, p.name.firstName)
        self.assertEquals(rp.name.lastName, p.name.lastName)
        root = etree.Element('root')
        self.assertEquals(len(root), 0)
        methods['sayHello'].input.to_xml( p, t, _body = root)
        self.assertEquals(len(root), 1)
        self.assertEquals(len(root[0]), 2)
        rp = types['Person']().from_xml(root[0][0])
        rt = types['int']().from_xml(root[0][1])
        self.assertEquals(rt, t)
        self.assertEquals(rp.age, p.age)
        self.assertEquals(rp.weight, p.weight)
        self.assertEquals(rp.height, p.height)
        self.assertEquals(rp.name.firstName, p.name.firstName)
        self.assertEquals(rp.name.lastName, p.name.lastName)
        root = etree.Element('root')
        self.assertEquals(len(root), 0)
        mm = types['sayHello']()
        mm.person = p
        mm.times = t
        methods['sayHello'].input.to_xml(mm, _body = root)
        self.assertEquals(len(root), 1)
        self.assertEquals(len(root[0]), 2)
        rp = types['Person']().from_xml(root[0][0])
        rt = types['int']().from_xml(root[0][1])
        self.assertEquals(rt, t)
        self.assertEquals(rp.age, p.age)
        self.assertEquals(rp.weight, p.weight)
        self.assertEquals(rp.height, p.height)
        self.assertEquals(rp.name.firstName, p.name.firstName)
        self.assertEquals(rp.name.lastName, p.name.lastName)

if __name__ == '__main__':
    unittest.main()
