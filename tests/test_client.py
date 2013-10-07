#!/usr/bin/env python
# test_client.py - test Client class, part of osa.
# Copyright 2013 Sergey Bozhenkov, boz at ipp.mpg.de
# Licensed under LGPLv3 or later, see the COPYING file.


import os
import sys
sys.path.insert(0, "../")
from osa.client import Client
from osa.wsdl import *
from osa.method import *
from osa.xmltypes import *
from tests.base import BaseTest
import unittest
if sys.version_info[0] < 3:
    from urllib2 import urlopen, HTTPError, URLError
else:
    from urllib.request import urlopen, HTTPError, URLError
    basestring = str

wsdl_url = 'http://lxpowerboz:88/services/python/HelloWorldService?wsdl'
test_path = os.path.abspath(os.path.dirname(__file__))


class TestClient(BaseTest):

    def setUp(self):
        self.client = Client(self.test_files['test.wsdl'])

    def tearDown(self):
        self.client = None

    def test_init(self):
        self.assertEqual(self.client.names, ["service HelloWorldService"])

        for t in ("Person", "Name", "echoString", "sayHello"):
            self.assertTrue(hasattr(self.client.types, t))
            self.assertEqual(type(getattr(self.client.types, t)), ComplexTypeMeta)

        for method in ("testMe", "giveMessage", "echoString", "sayHello", "faultyThing"):
            self.assertTrue(hasattr(self.client.service, method))
            self.assertEqual(type(getattr(self.client.service, method)), Method)

    def test_giveMessage(self):
        try:
            urlopen("http://lxpowerboz:88")
        except HTTPError:
            pass
        except URLError:
            return
        res = self.client.service.giveMessage()
        self.assertTrue(isinstance(res, basestring))

    def test_echoString(self):
        try:
            urlopen("http://lxpowerboz:88")
        except HTTPError:
            pass
        except URLError:
            return
        self.assertEqual('my message 1', self.client.service.echoString('my message 1'))

    def test_sayHello(self):
        try:
            urlopen("http://lxpowerboz:88")
        except HTTPError:
            pass
        except URLError:
            return
        n = self.client.types.Name()
        n.firstName = "first"
        n.lastName = "last"
        p = self.client.types.Person()
        p.name = n
        p.age = 30
        p.weight = 80
        p.height = 175
        self.assertEqual(['Hello, first\n']*5, self.client.service.sayHello(p, 5))

    def test_faultyThing(self):
        try:
            urlopen("http://lxpowerboz:88")
        except HTTPError:
            pass
        except URLError:
            return
        try:
            self.client.service.faultyThing()
        except RuntimeError as e:
            self.assertFalse(str(e).find('4u!') == -1)
