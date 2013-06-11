#!/usr/bin/env python
# test_xmlparser.py - test ns substitution, part of osa.
# Copyright 2013 Sergey Bozhenkov, boz at ipp.mpg.de
# Licensed under GPLv3 or later, see the COPYING file.

import sys
for x in sys.path:
    if x.find("osa") != -1:
        sys.path.remove(x)
sys.path.append("../")

import unittest
import xml.etree.cElementTree as etree
from osa.xmlparser import *

class TestXMLParser(unittest.TestCase):
    def test_ns_attr_parsing(self):
        root = parse_qualified_from_url("test.xml", attr=["a"])
        self.assertEquals(root.get("bok"), "ns:round")
        self.assertEquals(root[0].get("a"), "{39kingdom}angry")

if __name__ == '__main__':
    unittest.main()
