#!/usr/bin/env python

import sys
for x in sys.path:
    if x.find("osa") != -1:
        sys.path.remove(x)
sys.path.append("../")

import datetime
import unittest

import xml.etree.cElementTree as etree

from osa.client import Client
from osa.wsdl import WSDLParser, _primmap
from osa.methods import Method
from osa.xmltypes import *

wsdl_url = 'http://lxpowerboz:88/services/python/HelloWorldService?wsdl'

class TestClient(unittest.TestCase):
    def test_init(self):
        cl = Client(wsdl_url)
        self.assertEquals(cl.wsdl_url, wsdl_url)
        self.assertEquals(cl.names, ["HelloWorldService",])
        for t in ("Person", "Name", "echoString", "sayHello"):
            self.assertTrue(hasattr(cl.types, t))
            self.assertEquals(type(getattr(cl.types, t)), ComplexTypeMeta)
            self.assertTrue(t in cl.types.anyType._types.keys())
        for method in ("testMe", "giveMessage", "echoString", "sayHello", "faultyThing"):
            self.assertTrue(hasattr(cl.service, method))
            self.assertEquals(type(getattr(cl.service, method)), Method)

    def test_testme(self):
        #note: giveMessage is broken at the server side
        cl = Client(wsdl_url)
        res = cl.service.testMe()
        self.assertEqual(type(res), cl.types.testMeResponse)

    def test_echoString(self):
        cl = Client(wsdl_url)

        self.assertEquals('my message 1', cl.service.echoString('my message 1'))
        self.assertEquals('my message 2', cl.service.echoString(msg = 'my message 2'))
        m = cl.types.echoString()
        m.msg = 'my message 3'
        self.assertEquals('my message 3', cl.service.echoString(m))

    def test_sayHello(self):
        cl = Client(wsdl_url)

        n = cl.types.Name()
        n.firstName = "first"
        n.lastName = "last"
        p = cl.types.Person()
        p.name = n
        p.age = 30
        p.weight = 80
        p.height = 175

        self.assertEquals(['Hello, first']*5, cl.service.sayHello(p, 5))
        self.assertEquals(['Hello, first']*8, cl.service.sayHello(person = p, times = 8))
        m = cl.types.sayHello()
        m.person = p
        m.times = 10
        self.assertEquals(['Hello, first']*10, cl.service.sayHello(m))

    def test_faultyThing(self):
        cl = Client(wsdl_url)
        self.assertRaises(RuntimeError, cl.service.faultyThing)
        try:
            cl.service.faultyThing()
        except RuntimeError as e:
            self.assertFalse(str(e).find('4u!') == -1)




if __name__ == '__main__':
    unittest.main()
