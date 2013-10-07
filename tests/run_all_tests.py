#!/usr/bin/env python
# -*- coding: utf-8 -*-
# run_all_tests.py - run all tests, part of osa.
# Copyright 2013 Sergey Bozhenkov, boz at ipp.mpg.de
# Licensed under LGPLv3 or later, see the COPYING file.

import unittest
from test_xmlparser import TestXMLParser
from test_xmltypes_primitive import TestPrimitive
from test_xmltypes_complex import TestClassSerializer
from test_xmlschema import TestXMLSchema
from test_wsdl import TestWSDL
from test_message import TestMessage
from test_client import TestClient

if __name__ == '__main__':
    unittest.main()
