# -*- coding: utf-8 -*-

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

if __name__ == '__main__':
    unittest.main()
