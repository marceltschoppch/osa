#!/usr/bin/env python
# test_xmltypes_complex.py - test serialization of compound classes, part of osa.
# Copyright 2013 Sergey Bozhenkov, boz at ipp.mpg.de
# Licensed under LGPLv3 or later, see the COPYING file.

import sys
sys.path.insert(0, "../")
from osa.xmltypes import *
from osa.xmlnamespace import *
from tests.base import BaseTest
import xml.etree.cElementTree as etree
import unittest


ns_test = 'test_namespace'

Arr = ComplexTypeMeta('Arr', (), {
                "_children":[
                    {'name':"ch", "type":XMLInteger, "min":3, "max": 10, "nillable":False, "fullname":"ch"},
                        ], "__doc__": "an info"})

Address = ComplexTypeMeta('Address', (), {
                "_children":[
                    {'name':"street", "type":XMLString, "min":1, "max": 1, "nillable":False, "fullname":"street"},
                    {'name':"city", "type":XMLString, "min":1, "max": 1, "fullname":"city"},
                    {'name':"zip", "type":XMLInteger, "min":1, "max": 1, "nillable":True, "fullname":"zip"},
                    {'name':"since", "type":XMLDateTime, "min":0, "max": 1, "fullname":"since"},
                    {'name':"lattitude", "type":XMLDouble, "min":1, "max": 1, "fullname":"lattitude"},
                    {'name':"longitude", "type":XMLDouble, "min":1, "max": 1, "fullname":"longitude"},
                        ], "__doc__": "an address info"})
Person = ComplexTypeMeta('Person', (), {
                "_children":[
                    {'name':"name", "type":XMLString, "min":0, "max": 1,"fullname":"name"},
                    {'name':"birthdate", "type":XMLDateTime, "min":0, "max": 1, "fullname":"birthdate"},
                    {'name':"age", "type":XMLInteger, "min":0, "max": 1,"fullname":"age"},
                    {'name':"addresses", "type":Address, "min":0, "max": 'unbounded',"fullname":"addresses"},
                    {'name':"titles", "type":XMLString, "min":0, "max": 'unbounded',"fullname":"titles"},
                        ], "__doc__": "a person info"})

Employee = ComplexTypeMeta('Employee', (Person,), {
                "_children":[
                    {'name':"id", "type":XMLInteger, "min":1, "max": 1,"fullname":"id"},
                    {'name':"salary", "type":XMLDouble, "min":1, "max": 1,"fullname":"salary"},
                        ], "__doc__": "an employee info"})

Level2 = ComplexTypeMeta('Level2', (), {
                "_children":[
                    {'name':"arg1", "type":XMLString, "min":1, "max": 1,"fullname":"arg1"},
                    {'name':"arg2", "type":XMLDouble, "min":1, "max": 1,"fullname":"arg2"},
                        ], "__doc__": "don't know"})

Level3 = ComplexTypeMeta('Level3', (), {
                "_children":[
                    {'name':"arg1", "type":XMLInteger, "min":1, "max": 1,"fullname":"arg1"},
                        ], "__doc__": "don't know"})
Level4 = ComplexTypeMeta('Level4', (), {
                "_children":[
                    {'name':"arg1", "type":XMLString, "min":1, "max": 1,"fullname":"arg1"},
                        ], "__doc__": "don't know"})

Level1 = ComplexTypeMeta('Level1', (), {
                "_children":[
                    {'name':"level2", "type":Level2, "min":1, "max": 1,"fullname":"level2"},
                    {'name':"level3", "type":Level3, "min":0, "max": 'unbouneded', "fullname":"level3"},
                    {'name':"level4", "type":Level4, "min":0, "max": 'unbouneded',"fullname":"level4"},
                        ], "__doc__": "don't know"})


class TestClassSerializer(unittest.TestCase):

    def test_simple_class(self):
        a = Address()
        a.street = '123 happy way'
        a.city = 'badtown'
        a.zip = 32
        a.lattitude = 4.3
        a.longitude = 88.0

        element = etree.Element('test')
        a.to_xml( element, "{%s}%s" %(ns_test, "atach"))
        element = element[0]
        self.assertEqual(5, len(element.getchildren()))

        r = Address().from_xml(element)

        self.assertEqual(a.street, r.street)
        self.assertEqual(a.city, r.city)
        self.assertEqual(a.zip, r.zip)
        self.assertEqual(a.lattitude, r.lattitude)
        self.assertEqual(a.longitude, r.longitude)
        self.assertEqual(a.since, r.since)

    def test_nested_class(self):
        p = Person()
        element = etree.Element('test')
        p.to_xml(element, "{%s}%s" %(ns_test, "atach"))
        element = element[0]

        self.assertEqual(None, p.name)
        self.assertEqual(None, p.birthdate)
        self.assertEqual(None, p.age)
        self.assertEqual(None, p.addresses)

    def test_complex_class(self):
        l = Level1()
        l.level2 = Level2()
        l.level2.arg1 = 'abcd'
        l.level2.arg2 = 1.0/3.0
        l.level3 = []
        l.level4 = []

        for i in range(0, 100):
            a = Level3()
            a.arg1 = i
            l.level3.append(a)

        for i in range(0, 4):
            a = Level4()
            a.arg1 = str(i)
            l.level4.append(a)

        element = etree.Element('test')
        l.to_xml(element, "{%s}%s" %(ns_test, "atach"))
        element = element[0]
        l1 = Level1().from_xml(element)

        self.assertEqual(l1.level2.arg1, l.level2.arg1)
        self.assertEqual(l1.level2.arg2, l.level2.arg2)
        self.assertEqual(len(l1.level4), len(l.level4))
        self.assertEqual(len(l1.level3), len(l.level3))
        for i in range(100):
            self.assertEqual(l1.level3[i].arg1, l.level3[i].arg1)
        for i in range(4):
            self.assertEqual(l1.level4[i].arg1, l.level4[i].arg1)


    def test_any(self):
        a = Address()
        a.street = '123 happy way'
        a.city = 'badtown'
        a.zip = 32
        a.lattitude = 4.3
        a.longitude = 88.0

        element = etree.Element('test')
        a.to_xml( element, "{%s}%s" %(ns_test, "atach"))
        element = element[0]
        element.set("{%s}type" %NS_XSI, 'Address')

        XMLAny._types.update({'Person':Person, 'Address':Address,
                              'Level4':Level4, 'Level3':Level3,
                              'Level2': Level2, 'Level1':Level1})

        r = XMLAny().from_xml(element)
        self.assertTrue(isinstance(r, Address))

        self.assertEqual(a.street, r.street)
        self.assertEqual(a.city, r.city)
        self.assertEqual(a.zip, r.zip)
        self.assertEqual(a.lattitude, r.lattitude)
        self.assertEqual(a.longitude, r.longitude)
        self.assertEqual(a.since, r.since)

    def test_tofrom_file(self):
        fname = "out.xml"
        a = Address()
        a.street = '123 happy way'
        a.city = 'badtown'
        a.zip = 32
        a.lattitude = 4.3
        a.longitude = 88.0
        try:
            os.remove(fname)
        except:
            pass
        a.to_file(fname)
        b = Address.from_file(fname)
        self.assertEqual(b, a)
        self.assertTrue(b is not a)

    def test_nillable(self):
        a = Address()
        a.street = '123 happy way'
        a.city = 'badtown'
        a.zip = 32
        a.lattitude = 4.3
        a.longitude = 88.0

        element = etree.Element('test')
        a.to_xml( element, "{%s}%s" %(ns_test, "atach"))
        element = element[0]
        self.assertEqual(5, len(element.getchildren()))

        element[2].text=None  # zip is nillable 
        element[2].set('{%s}nil' % xmlnamespace.NS_XSI, 'true')
        r = Address().from_xml(element)
        self.assertEqual(a.street, r.street)
        self.assertEqual(a.city, r.city)
        self.assertEqual(r.zip, 0) # bug 7 None)
        self.assertEqual(a.lattitude, r.lattitude)
        self.assertEqual(a.longitude, r.longitude)
        self.assertEqual(a.since, r.since)

        element = etree.Element('test')
        a.to_xml( element, "{%s}%s" %(ns_test, "atach"))
        element = element[0]
        self.assertEqual(5, len(element.getchildren()))
        element[0].text=None  # street is not nillable 
        element[0].set('{%s}nil' % xmlnamespace.NS_XSI, 'true')
        # bug 7
        # self.assertNotRaises(ValueError, Address().from_xml, element)
        Address().from_xml(element)

        element = etree.Element('test')
        a.to_xml( element, "{%s}%s" %(ns_test, "atach"))
        element = element[0]
        element.clear()
        self.assertEqual(0, len(element.getchildren()))
        element.set('{%s}nil' % xmlnamespace.NS_XSI, 'true')
        self.assertRaises(ValueError,  Address().from_xml, element)

    def test_min_max_check(self):
        a = Arr()
        a.ch = [1,2,3,4]

        element = etree.Element('test')
        a.to_xml( element, "{%s}%s" %(ns_test, "atach"))
        element = element[0]

        # working
        r = Arr().from_xml(element)

        # < minOccrus
        element = etree.Element('test')
        a.to_xml( element, "{%s}%s" %(ns_test, "atach"))
        element = element[0]
        element.remove(element[-1])
        element.remove(element[-1])
        self.assertEqual(2, len(element.getchildren()))
        self.assertRaises(ValueError,  Arr().from_xml, element)

        # > maxOccurs
        element = etree.Element('test')
        a.to_xml( element, "{%s}%s" %(ns_test, "atach"))
        element = element[0]
        for i in range(7):
            element.append(element[-1])
        self.assertEqual(11, len(element.getchildren()))
        self.assertRaises(ValueError,  Arr().from_xml, element)
