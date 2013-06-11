#!/usr/bin/env python
# test_client.py - test Client class, part of osa.
# Copyright 2013 Sergey Bozhenkov, boz at ipp.mpg.de
# Licensed under GPLv3 or later, see the COPYING file.

import sys
for x in sys.path:
    if x.find("osa") != -1:
        sys.path.remove(x)
sys.path.append("../")

import unittest
import xml.etree.cElementTree as etree
from osa.client import *
from osa.wsdl import *
from osa.method import *
from osa.xmltypes import *
import urllib2

wsdl_url = 'http://lxpowerboz:88/services/python/HelloWorldService?wsdl'

class TestClient(unittest.TestCase):
    def setUp(self):
        self.client = Client("test.wsdl")
    def tearDown(self):
        self.client = None
    def test_init(self):
        self.assertEquals(self.client.names, ["service HelloWorldService",])
        for t in ("Person", "Name", "echoString", "sayHello"):
            self.assertTrue(hasattr(self.client.types, t))
            self.assertEquals(type(getattr(self.client.types, t)), ComplexTypeMeta)
        for method in ("testMe", "giveMessage", "echoString", "sayHello", "faultyThing"):
            self.assertTrue(hasattr(self.client.service, method))
            self.assertEquals(type(getattr(self.client.service, method)), Method)

    def test_giveMessage(self):
        try:
            urllib2.urlopen("http://lxpowerboz:88")
        except urllib2.HTTPError:
            pass
        except urllib2.URLError:
            return
        res = self.client.service.giveMessage()
        self.assertTrue(isinstance(res, str))

    def test_echoString(self):
        try:
            urllib2.urlopen("http://lxpowerboz:88")
        except urllib2.HTTPError:
            pass
        except urllib2.URLError:
            return
        self.assertEquals('my message 1', self.client.service.echoString('my message 1'))

    def test_sayHello(self):
        try:
            urllib2.urlopen("http://lxpowerboz:88")
        except urllib2.HTTPError:
            pass
        except urllib2.URLError:
            return
        n = self.client.types.Name()
        n.firstName = "first"
        n.lastName = "last"
        p = self.client.types.Person()
        p.name = n
        p.age = 30
        p.weight = 80
        p.height = 175
        self.assertEquals(['Hello, first\n']*5, self.client.service.sayHello(p, 5))

    def test_faultyThing(self):
        try:
            urllib2.urlopen("http://lxpowerboz:88")
        except urllib2.HTTPError:
            pass
        except urllib2.URLError:
            return
        try:
            self.client.service.faultyThing()
        except RuntimeError as e:
            self.assertFalse(str(e).find('4u!') == -1)


if __name__ == '__main__':
    unittest.main()
