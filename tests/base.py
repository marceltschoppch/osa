# -*- coding: utf-8 -*-
# base.py - basic stuff for tests, part of osa.
# Copyright 2013 Sergey Bozhenkov, boz at ipp.mpg.de
# Licensed under LGPLv3 or later, see the COPYING file.

import unittest
import os

test_dir = os.path.abspath(os.path.dirname(__file__))
path_join = lambda f: os.path.join(test_dir, f)


class BaseTest(unittest.TestCase):

    test_files = {
        'test.wsdl': path_join('test.wsdl'),
        'test.xml': path_join('test.xml'),
        'schema.xml': path_join('schema.xml'),
        'schema2.xml': path_join('schema2.xml'),
        'schema3.xml': path_join('schema3.xml'),
    }
