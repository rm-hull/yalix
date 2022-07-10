#!/usr/bin/env python
# -*- coding: utf-8 -*-

import unittest
from yalix.exceptions import EvaluationError


class Primitive(object):

    def __init__(self, source=None, location=None):
        if source:
            self.__source__ = source
        if location:
            self.__location__ = location


class EvaluationErrorTests(unittest.TestCase):

    def test_no_source_location(self):
        ex = EvaluationError(Primitive(), "Message with {0}", "argument")
        self.assertEqual("Message with argument", str(ex))

    def test_with_source_location(self):
        prim = Primitive("aaaaaaaaaa\nbbbbbbbbbb\ncccccccccc\ndddddddddd", 23)
        ex = EvaluationError(prim, "Message with {0}", "argument")
        self.assertEqual("Message with argument at line:3, col:2", str(ex))


if __name__ == '__main__':
    unittest.main()
